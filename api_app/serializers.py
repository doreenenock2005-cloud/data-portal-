from rest_framework import serializers
from datasets.models import Dataset, Category, Subcategory

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'slug', 'description', 'dataset_count']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'dataset_count', 'subcategories']

class DatasetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    class Meta:
        model = Dataset
        fields = ['id', 'title', 'slug', 'description', 'category', 'subcategory', 'source_department',
                  'data_owner', 'region', 'temporal_extent_start', 'temporal_extent_end',
                  'language', 'format', 'file_size', 'records', 'download_count',
                  'created_at', 'updated_at']
