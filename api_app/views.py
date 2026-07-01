from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.response import Response
from datasets.models import Dataset, Category, Subcategory
from .serializers import DatasetSerializer, CategorySerializer, SubcategorySerializer

class DatasetListAPI(generics.ListAPIView):
    queryset = Dataset.objects.filter(status='published').select_related('category', 'subcategory')
    serializer_class = DatasetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'source_department', 'category__name', 'subcategory__name']
    ordering_fields = ['created_at', 'download_count', 'title']

class DatasetDetailAPI(generics.RetrieveAPIView):
    queryset = Dataset.objects.filter(status='published').select_related('category', 'subcategory')
    serializer_class = DatasetSerializer

class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all().prefetch_related('subcategories')
    serializer_class = CategorySerializer

class SubcategoryListAPI(generics.ListAPIView):
    queryset = Subcategory.objects.all().select_related('category')
    serializer_class = SubcategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category__name']

class CategoryDatasetsAPI(generics.ListAPIView):
    serializer_class = DatasetSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Dataset.objects.filter(status='published', category__slug=slug).select_related('category', 'subcategory')

class SubcategoryDatasetsAPI(generics.ListAPIView):
    serializer_class = DatasetSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        cat_slug = self.kwargs['cat_slug']
        sub_slug = self.kwargs['sub_slug']
        return Dataset.objects.filter(
            status='published', 
            category__slug=cat_slug, 
            subcategory__slug=sub_slug
        ).select_related('category', 'subcategory')

def api_docs(request):
    return render(request, 'api_app/docs.html')
