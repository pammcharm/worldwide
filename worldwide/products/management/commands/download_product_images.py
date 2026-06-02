"""
Management command to download product images from URLs and store them locally.
Useful for importing products from Alibaba, Amazon, etc.

Usage:
    python manage.py download_product_images
    python manage.py download_product_images --product-id=123
"""
import os
import io
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image
import requests
from products.models import Product, ProductImage


class Command(BaseCommand):
    help = "Download product images from URLs and store them in media folder"

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='Download images for a specific product ID'
        )
        parser.add_argument(
            '--source-url',
            type=str,
            help='Download image from specific URL'
        )

    def handle(self, *args, **options):
        product_id = options.get('product_id')
        source_url = options.get('source_url')

        if product_id and source_url:
            try:
                product = Product.objects.get(pk=product_id)
                self.download_image_for_product(product, source_url)
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Product with ID {product_id} not found'))
        else:
            # Download images for all products with source_url but no images
            products = Product.objects.filter(
                source_url__isnull=False
            ).exclude(
                source_url__exact=''
            ).filter(
                images__isnull=True
            )[:10]  # Limit to first 10

            if not products.exists():
                self.stdout.write(self.style.WARNING('No products found with URLs but no images'))
                return

            for product in products:
                if product.source_url:
                    self.stdout.write(f'Processing {product.name}...')
                    self.download_image_for_product(product, product.source_url)

    def download_image_for_product(self, product, url):
        """Download and save image from URL"""
        try:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename_with_path = parsed_url.path
            filename = os.path.basename(filename_with_path) or 'product_image.jpg'

            # Download image
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if response.status_code == 200:
                # Validate it's an image
                try:
                    img = Image.open(io.BytesIO(response.content))
                    img.verify()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Invalid image: {e}'))
                    return

                # Save to ProductImage
                image_content = ContentFile(response.content)
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image_content,
                    alt_text=product.short_description or product.name,
                    is_primary=not product.images.exists(),  # First image is primary
                    order=product.images.count()
                )
                product_image.image.name = f'products/{product.id}/{filename}'
                product_image.save()

                self.stdout.write(
                    self.style.SUCCESS(f'✓ Saved image for {product.name}: {filename}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to download {url} (HTTP {response.status_code})')
                )

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'✗ Request failed for {product.name}: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error processing {product.name}: {e}'))
