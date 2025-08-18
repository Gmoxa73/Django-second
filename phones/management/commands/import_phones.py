import csv
from decimal import Decimal
from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date
from phones.models import Phone


class Command(BaseCommand):
    help = 'Load phones from phones.csv into Phone model'
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            dest='path',
            default='phones.csv',
            help='Path to the phones CSV file'
        )

    def handle(self, *args, **options):
        path = options['path']

        try:
            with open(path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                # читаем заголовок
                headers = next(reader, None)
                header_index = {h: i for i, h in enumerate(headers or [])}

                with transaction.atomic():
                    for line_number, line in enumerate(reader, start=2):  # начиная со второй строки файла
                        if not line:
                            continue

                        # Привязка по именам заголовков
                        # Из примера: id;name;image;price;release_date;lte_exists
                        # можно игнорировать поле id, т.к. PK генерируется автоматически
                        name = line[header_index['name']].strip() if 'name' in header_index else ''
                        image = line[header_index['image']].strip() if 'image' in header_index else ''
                        price_raw = line[header_index['price']].strip() if 'price' in header_index else '0'
                        release_date_raw = line[
                            header_index['release_date']].strip() if 'release_date' in header_index else ''
                        lte_exists_raw = line[
                            header_index['lte_exists']].strip() if 'lte_exists' in header_index else 'False'
                        slug_value = ''  # slug столбец может быть пустым, сгенерируем

                        # преобразования
                        try:
                            price = Decimal(price_raw.replace(',', '.'))
                        except Exception:
                            price = Decimal('0.0')

                        release_date = parse_date(release_date_raw) if release_date_raw else None

                        lte_exists = str(lte_exists_raw).lower() in ('1', 'true', 't', 'yes', 'on')

                        if 'slug' in header_index:
                            slug_value = line[header_index['slug']].strip()
                        if not slug_value:
                            slug_value = slugify(name)

                        # создаем или обновляем объект по slug
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
                        if not created:
                            phone.name = name
                            phone.price = price
                            phone.image = image
                            phone.release_date = release_date
                            phone.lte_exists = lte_exists
                            phone.save()

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
        except KeyError as ke:
            self.stderr.write(self.style.ERROR(f"CSV header is missing expected column: {ke}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
