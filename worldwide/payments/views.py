import stripe
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from orders.models import Order
from .models import Payment
from .services import (
    PaypackError,
    find_transaction,
    payment_status_from_paypack,
    request_payment,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_view(request, order_number):
    """Payment page for an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = getattr(order, "payment", None)

    if order.payment_status == "paid":
        messages.info(request, "This order has already been paid.")
        return redirect("orders:detail", order_number=order.order_number)

    if request.method == "POST":
        method = request.POST.get("payment_method", "stripe")

        if method == "stripe":
            return redirect("payments:stripe_checkout", order_number=order.order_number)
        elif method in ("mtn_momo", "airtel_money"):
            phone = request.POST.get("phone_number", "").strip()
            if not phone:
                messages.error(request, "Please enter your Mobile Money phone number.")
                return render(request, "payments/payment.html", {
                    "order": order,
                    "payment": payment,
                    "selected_method": method,
                    "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
                })
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    "method": method,
                    "status": "pending",
                    "amount": order.total,
                    "amount_rwf": order.total,
                    "phone_number": phone,
                },
            )
            if not created:
                payment.method = method
                payment.phone_number = phone
                payment.amount = order.total
                payment.amount_rwf = order.total
                payment.status = "pending"
                payment.save()

            try:
                paypack_response = request_payment(
                    phone=phone,
                    amount=order.total,
                    idempotency_key=f"ww{order.pk}{payment.pk}{method}"[:32],
                )
            except PaypackError as exc:
                payment.status = "failed"
                payment.payment_details = {"error": str(exc)}
                payment.save(update_fields=["status", "payment_details", "updated_at"])
                messages.error(request, f"Paypack could not start payment: {exc}")
                return redirect("payments:pay", order_number=order.order_number)

            payment.transaction_id = paypack_response.get("ref", "")
            payment.status = payment_status_from_paypack(paypack_response.get("status"))
            payment.payment_details = paypack_response
            payment.save(update_fields=["transaction_id", "status", "payment_details", "updated_at"])
            return redirect("payments:momo_processing", order_number=order.order_number)
        elif method == "cod":
            order.payment_status = "pending"
            order.status = "confirmed"
            order.save()
            Payment.objects.create(
                order=order,
                method="cod",
                status="pending",
                amount=order.total,
                amount_rwf=order.total,
            )
            messages.success(request, "Order confirmed! Pay on delivery.")
            return redirect("orders:detail", order_number=order.order_number)

    return render(request, "payments/payment.html", {
        "order": order,
        "payment": payment,
        "selected_method": payment.method if payment else "mtn_momo",
        "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
    })


@login_required
def momo_processing(request, order_number):
    """Show Paypack Mobile Money processing page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = get_object_or_404(Payment, order=order)

    if payment.transaction_id and payment.status == "pending":
        try:
            transaction = find_transaction(payment.transaction_id)
            update_payment_from_paypack(payment, transaction)
        except PaypackError:
            pass

    return render(request, "payments/momo_processing.html", {
        "order": order,
        "payment": payment,
    })


@login_required
def stripe_checkout(request, order_number):
    """Create Stripe checkout session."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # cents
            currency="usd",
            metadata={"order_number": order.order_number},
        )

        Payment.objects.create(
            order=order,
            method="stripe",
            status="processing",
            amount=order.total,
            stripe_payment_intent=intent.id,
        )

        return render(request, "payments/stripe_checkout.html", {
            "order": order,
            "client_secret": intent.client_secret,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
        })
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("payments:pay", order_number=order.order_number)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks with signature verification."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_SECRET_KEY
        )
    except ValueError as e:
        logger.warning("Stripe webhook: Invalid payload - %s", str(e))
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning("Stripe webhook: Invalid signature - %s", str(e))
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_number = intent["metadata"].get("order_number")
        try:
            order = Order.objects.get(order_number=order_number)
            order.payment_status = "paid"
            order.status = "confirmed"
            order.save()
            payment = order.payment
            payment.status = "completed"
            payment.paid_at = timezone.now()
            payment.stripe_charge_id = intent["charges"]["data"][0]["id"]
            payment.save()
            logger.info("Stripe payment completed for order %s", order_number)
        except Order.DoesNotExist:
            logger.error("Stripe webhook: Order not found - %s", order_number)

    return JsonResponse({"status": "ok"})


@csrf_exempt
def momo_webhook(request):
    """
    Webhook endpoint for Paypack MTN MoMo / Airtel Money callbacks.
    Secure HMAC-SHA256 signature verification.
    """
    import json

    # Handle HEAD requests (for webhook testing)
    if request.method == "HEAD":
        return HttpResponse(status=200)

    # Verify webhook signature
    signature = request.headers.get("X-Paypack-Signature", "")
    if settings.PAYPACK_WEBHOOK_SECRET:
        if not verify_webhook_signature(request.body, signature):
            logger.warning("Paypack webhook: Invalid signature detected from %s", request.META.get("REMOTE_ADDR"))
            return JsonResponse({"error": "Invalid signature"}, status=403)
    else:
        logger.warning("Paypack webhook: PAYPACK_WEBHOOK_SECRET not configured")
        return JsonResponse({"error": "Webhook not configured"}, status=500)

    try:
        data = json.loads(request.body)
        transaction = data.get("data") or data
        
        # Extract transaction ID from various possible field names
        transaction_id = (
            transaction.get("ref") or 
            transaction.get("transaction_id") or 
            transaction.get("tx_ref")
        )
        
        if not transaction_id:
            logger.warning("Paypack webhook: No transaction_id in payload")
            return JsonResponse({"error": "Invalid transaction_id"}, status=400)
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            update_payment_from_paypack(payment, transaction)
            logger.info("Paypack webhook: Payment updated for transaction %s", transaction_id)
        except Payment.DoesNotExist:
            logger.warning("Paypack webhook: Payment not found for transaction %s", transaction_id)
            
    except json.JSONDecodeError:
        logger.error("Paypack webhook: Invalid JSON payload")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error("Paypack webhook: Unexpected error - %s", str(e))
        return JsonResponse({"error": "Internal error"}, status=500)

    return JsonResponse({"status": "ok"})


def update_payment_from_paypack(payment, transaction):
    payment.payment_details = transaction
    payment.status = payment_status_from_paypack(transaction.get("status"))
    if payment.status == "completed":
        payment.paid_at = timezone.now()
        payment.order.payment_status = "paid"
        payment.order.status = "confirmed"
        payment.order.save(update_fields=["payment_status", "status", "updated_at"])
    elif payment.status == "failed":
        payment.order.payment_status = "failed"
        payment.order.save(update_fields=["payment_status", "updated_at"])
    payment.save(update_fields=["status", "paid_at", "payment_details", "updated_at"])
    return payment


@login_required
def check_payment_status(request, order_number):
    """API endpoint to check payment status (for polling on frontend)."""
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        payment = get_object_or_404(Payment, order=order)
        
        # If payment is still pending, refresh from Paypack
        if payment.status == "pending" and payment.transaction_id:
            try:
                transaction = find_transaction(payment.transaction_id)
                update_payment_from_paypack(payment, transaction)
            except PaypackError:
                pass
        
        return JsonResponse({
            "status": payment.status,
            "order_number": order_number,
            "method": payment.method,
        })
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return JsonResponse({"error": "Not found"}, status=404)
