from django.db import models
from django.utils.text import slugify

class Phone(models.Model):
    id = models.AutoField(primary_key=True)  # явное указание первичного ключа (можно опустить, если хотим автоматический)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    lte_exists = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # генерируем slug из имени, если slug пустой
        if not self.slug:
            self.slug = slugify(self.name)
            # чтобы избежать коллизий slug, можно добавить логику дубликатов
            original_slug = self.slug
            queryset = Phone.objects.all()
            counter = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

