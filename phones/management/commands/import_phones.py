import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.utils.dateparse import parse_date
from phones.models import Phone

class Command(BaseCommand):
    help = 'Import phones from a CSV file into Phone model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            required=True,
            help='Path to phones.csv (CSV delimiter ,)'
        )

    def handle(self, *args, **options):
        path = options['path']

        with open(path, newline='', encoding='utf-8') as f:
            # CSV пример: id,name,image,price,release_date,lte_exists,
            # delimiter - точка с запятой
            reader = csv.DictReader(f, delimiter=';')
            created_count = 0
            updated_count = 0
            with transaction.atomic():
                for row in reader:
                    if not row:
                        continue
                    name = (row.get('name') or '').strip()
                    image = (row.get('image') or '').strip()
                    price_raw = (row.get('price') or '0').strip()
                    release_date_raw = (row.get('release_date') or '').strip()
                    lte_exists_raw = (row.get('lte_exists') or 'False').strip()

                    if not name:
                        continue  # пропустим пустые записи

                    slug_value = slugify(name)

                    try:
                        price = Decimal(price_raw.replace(',', '.'))
                    except Exception:
                        price = Decimal('0.0')

                    release_date = parse_date(release_date_raw) if release_date_raw else None
                    lte_exists = str(lte_exists_raw).lower() in ('1', 'true', 'yes', 'on')

                    phone, created = Phone.objects.get_or_create(
                        slug=slug_value,
                        defaults={
                            'name': name,
                            'price': price,
                            'image': image,
                            'release_date': release_date,
                            'lte_exists': lte_exists,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        phone.name = name
                        phone.price = price
                        phone.image = image
                        phone.release_date = release_date
                        phone.lte_exists = lte_exists
                        phone.save()
                        updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Import finished. Created: {created_count}, Updated: {updated_count}"
            ))