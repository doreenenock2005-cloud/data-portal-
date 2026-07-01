import os
import json
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.conf import settings
from django.db.models import Q
from datasets.models import Dataset, Category, Subcategory
from data_transform.engine import TransformationEngine

def dataset_list(request):
    categories = Category.objects.all()
    datasets = Dataset.objects.filter(status='published').select_related('category')
    category_slug = request.GET.get('category')
    if category_slug:
        datasets = datasets.filter(category__slug=category_slug)
    search = request.GET.get('q')
    if search:
        datasets = datasets.filter(Q(title__icontains=search) | Q(description__icontains=search)).distinct()
    return render(request, 'datasets/dataset_list.html', {
        'datasets': datasets,
        'categories': categories,
        'selected_category': category_slug,
        'page_title': 'All Datasets',
        'subcategories': Subcategory.objects.filter(category__slug=category_slug) if category_slug else Subcategory.objects.none(),
        'selected_subcategory': request.GET.get('subcategory'),
    })

def dataset_detail(request, slug):
    dataset = get_object_or_404(Dataset, slug=slug, status='published')
    chart_data = dataset.chart_data
    preview_rows = []
    if dataset.processed_file:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, str(dataset.processed_file))
            if os.path.exists(file_path):
                df = pd.read_csv(file_path) if str(dataset.processed_file).endswith('.csv') else pd.read_excel(file_path)
                preview_rows = df.to_dict('records')
        except Exception as e:
            pass
    categories = Category.objects.all()
    return render(request, 'datasets/dataset_detail.html', {
        'dataset': dataset,
        'chart_data': chart_data or {},
        'preview_rows': preview_rows,
        'categories': categories,
        'page_title': dataset.title,
        'subcategory': dataset.subcategory,
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'datasets/category_list.html', {
        'categories': categories,
        'page_title': 'Browse by Category',
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    datasets = Dataset.objects.filter(category=category, status='published').select_related('subcategory')
    subcategories = Subcategory.objects.filter(category=category)
    subcategory_slug = request.GET.get('subcategory')
    if subcategory_slug:
        datasets = datasets.filter(subcategory__slug=subcategory_slug)
    return render(request, 'datasets/category_detail.html', {
        'category': category,
        'datasets': datasets,
        'subcategories': subcategories,
        'page_title': category.name,
        'selected_subcategory': subcategory_slug,
    })

@login_required
def download_dataset(request, slug):
    dataset = get_object_or_404(Dataset, slug=slug, status='published')
    dataset.download_count += 1
    dataset.save()
    file_path = os.path.join(settings.MEDIA_ROOT, str(dataset.processed_file)) if dataset.processed_file else None
    if not file_path or not os.path.exists(file_path):
        messages.error(request, 'Dataset file not found.')
        return redirect('datasets:dataset_detail', slug=slug)
    
    fmt = request.GET.get('format', 'csv').lower()
    if fmt == 'xlsx':
        xlsx_path = file_path.replace('.csv', '.xlsx')
        if not os.path.exists(xlsx_path):
            df = pd.read_csv(file_path)
            df.to_excel(xlsx_path, index=False, engine='openpyxl')
        file_path = xlsx_path
        ext = 'xlsx'
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        ext = 'csv'
        content_type = 'text/csv'
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{dataset.title}.{ext}"'
        return response
