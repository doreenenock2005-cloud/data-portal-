from django.db import models
from django.conf import settings

class Category(models.Model):
    ICON_CHOICES = [
        ('traffic', 'Traffic Light'),
        ('population', 'People'),
        ('waste', 'Waste Management'),
        ('health', 'Health Facility'),
        ('water', 'Water & Electricity'),
        ('environment', 'Environmental'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='traffic')
    dataset_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.name.lower().replace(' ', '-').replace('&', 'and')
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    dataset_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ['name']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f'{self.category.name} > {self.name}'

    def save(self, *args, **kwargs):
        self.slug = self.name.lower().replace(' ', '-').replace('&', 'and')
        super().save(*args, **kwargs)


class Dataset(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'XLSX'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='datasets')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='datasets', blank=True, null=True)
    source_department = models.CharField(max_length=200)
    data_owner = models.CharField(max_length=200, default='Dar es Salaam City Council')
    region = models.CharField(max_length=100, default='Dar es Salaam')
    temporal_extent_start = models.DateField()
    temporal_extent_end = models.DateField()
    language = models.CharField(max_length=50, default='English')
    resource_type = models.CharField(max_length=50, default='Dataset')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='csv')
    file_size = models.CharField(max_length=20, blank=True)
    records = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    raw_file = models.FileField(upload_to='datasets/raw/', blank=True, null=True)
    processed_file = models.FileField(upload_to='datasets/processed/', blank=True, null=True)
    chart_image = models.ImageField(upload_to='charts/', blank=True, null=True)
    chart_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title.lower().replace(' ', '-').replace(',', '').replace("'", '')[:200]
        super().save(*args, **kwargs)
        Category.objects.filter(pk=self.category_id).update(
            dataset_count=Dataset.objects.filter(category=self.category, status='published').count()
        )
        Subcategory.objects.filter(pk=self.subcategory_id).update(
            dataset_count=Dataset.objects.filter(subcategory=self.subcategory, status='published').count()
        )
