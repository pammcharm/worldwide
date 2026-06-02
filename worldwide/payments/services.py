import base64
import hashlib
import hmac
import uuid
from decimal import Decimal, ROUND_HALF_UP

import requests
from django.conf import settings


class PaypackError(Exception):
    """Raised when Paypack cannot create or verify a payment."""


def paypack_configured():
    return bool(settings.PAYPACK_CLIENT_ID and settings.PAYPACK_CLIENT_SECRET)


def rwf_amount(amount):
    return int(Decimal(amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def paypack_headers(access_token=None, idempotency_key=None):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Webhook-Mode": settings.PAYPACK_WEBHOOK_MODE,
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key[:32]
    return headers


def parse_response(response):
    try:
        data = response.json()
    except ValueError as exc:
        raise PaypackError("Paypack returned an invalid response.") from exc

    if response.status_code >= 400:
        message = data.get("message") or data.get("error") or "Paypack request failed."
        raise PaypackError(message)
    return data


def get_access_token():
    if not paypack_configured():
        raise PaypackError("Paypack credentials are not configured.")

    response = requests.post(
        f"{settings.PAYPACK_BASE_URL}/auth/agents/authorize",
        json={
            "client_id": settings.PAYPACK_CLIENT_ID,
            "client_secret": settings.PAYPACK_CLIENT_SECRET,
        },
        headers=paypack_headers(),
        timeout=settings.PAYPACK_TIMEOUT_SECONDS,
    )
    data = parse_response(response)
    access_token = data.get("access")
    if not access_token:
        raise PaypackError("Paypack did not return an access token.")
    return data


def request_payment(phone, amount, idempotency_key=None):
    token_data = get_access_token()
    access_token = token_data["access"]
    response = requests.post(
        f"{settings.PAYPACK_BASE_URL}/transactions/cashin",
        json={
            "amount": rwf_amount(amount),
            "number": phone,
        },
        headers=paypack_headers(
            access_token=access_token,
            idempotency_key=idempotency_key or uuid.uuid4().hex,
        ),
        timeout=settings.PAYPACK_TIMEOUT_SECONDS,
    )
    return parse_response(response)


def find_transaction(ref):
    token_data = get_access_token()
    access_token = token_data["access"]
    response = requests.get(
        f"{settings.PAYPACK_BASE_URL}/transactions/find/{ref}",
        headers=paypack_headers(access_token=access_token),
        timeout=settings.PAYPACK_TIMEOUT_SECONDS,
    )
    return parse_response(response)


def verify_webhook_signature(raw_body, signature):
    if not settings.PAYPACK_WEBHOOK_SECRET:
        return False
    expected = hmac.new(
        settings.PAYPACK_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).digest()
    expected_signature = base64.b64encode(expected).decode("utf-8")
    return hmac.compare_digest(expected_signature, signature or "")


def payment_status_from_paypack(status):
    status = (status or "").lower()
    if status == "successful":
        return "completed"
    if status == "failed":
        return "failed"
    return "pending"
