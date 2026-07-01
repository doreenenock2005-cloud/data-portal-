from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import Count, Sum
from datasets.models import Dataset, Category, Subcategory
from accounts.models import Profile
from data_transform.engine import TransformationEngine
from accounts.models import User
from core.models import ContactMessage
import os
import pandas as pd
from datetime import datetime

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_datasets = Dataset.objects.count()
    total_users = Profile.objects.exclude(role='admin').count()
    total_downloads = Dataset.objects.aggregate(total=Sum('download_count'))['total'] or 0
    total_categories = Category.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    recent_activities = []
    return render(request, 'admin_portal/dashboard.html', {
        'total_datasets': total_datasets,
        'total_users': total_users,
        'total_downloads': total_downloads,
        'total_categories': total_categories,
        'recent_activities': recent_activities,
        'categories': Category.objects.all(),
        'unread_messages': unread_messages,
    })

@login_required
@user_passes_test(is_admin)
def admin_dataset_management(request):
    datasets = Dataset.objects.all().select_related('category', 'subcategory')
    categories = Category.objects.all().prefetch_related('subcategories')
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    subcategory_filter = request.GET.get('subcategory', '')
    if search_query:
        datasets = datasets.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query)).distinct()
    if category_filter:
        datasets = datasets.filter(category__slug=category_filter)
    if subcategory_filter:
        datasets = datasets.filter(subcategory__slug=subcategory_filter)
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        description = request.POST.get('description')
        source_department = request.POST.get('source_department')
        temporal_start = request.POST.get('temporal_start')
        temporal_end = request.POST.get('temporal_end')
        raw_file = request.FILES.get('raw_file')
        if not title or not category_id or not raw_file:
            messages.error(request, 'Title, category, and file are required.')
        else:
            category = Category.objects.get(id=category_id)
            ext = os.path.splitext(raw_file.name)[1].lower()
            file_type = 'csv' if ext == '.csv' else 'xlsx' if ext in ['.xls', '.xlsx'] else None
            if not file_type:
                messages.error(request, 'Only CSV and XLSX files are allowed.')
            else:
                engine = TransformationEngine()
                subcategory = None
                if subcategory_id:
                    subcategory = Subcategory.objects.filter(id=subcategory_id, category=category).first()
                result = engine.process(raw_file, subcategory.name if subcategory else category.name)
                dataset = Dataset.objects.create(
                    title=title,
                    description=description or 'Dar es Salaam open dataset.',
                    category=category,
                    subcategory=subcategory,
                    source_department=source_department or 'City Administrative Secretariat',
                    data_owner='Dar es Salaam City Council',
                    region='Dar es salaam',
                    temporal_extent_start=datetime.strptime(temporal_start, '%Y-%m-%d').date() if temporal_start else datetime.now().date(),
                    temporal_extent_end=datetime.strptime(temporal_end, '%Y-%m-%d').date() if temporal_end else datetime.now().date(),
                    language='English',
                    resource_type='Dataset',
                    format=file_type,
                    file_size=f"{raw_file.size / (1024*1024):.1f} MB",
                    records=result['records'],
                    status='published',
                    raw_file=raw_file,
                    processed_file=result['processed_file'],
                    chart_image=result.get('chart_image'),
                    chart_data=result.get('chart_data'),
                )
                messages.success(request, 'Dataset uploaded and processed successfully.')
                return redirect('admin_portal:admin_datasets')
    return render(request, 'admin_portal/dataset_management.html', {
        'datasets': datasets,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_subcategory': subcategory_filter,
    })

@login_required
@user_passes_test(is_admin)
def admin_dataset_edit(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    categories = Category.objects.all().prefetch_related('subcategories')
    if request.method == 'POST':
        dataset.title = request.POST.get('title', dataset.title)
        dataset.description = request.POST.get('description', dataset.description)
        dataset.source_department = request.POST.get('source_department', dataset.source_department)
        cat_id = request.POST.get('category')
        if cat_id:
            dataset.category = Category.objects.get(id=cat_id)
        subcat_id = request.POST.get('subcategory')
        if subcat_id:
            dataset.subcategory = Subcategory.objects.get(id=subcat_id)
        dataset.save()
        messages.success(request, 'Dataset updated successfully.')
        return redirect('admin_portal:admin_datasets')
    return render(request, 'admin_portal/dataset_edit.html', {
        'dataset': dataset,
        'categories': categories,
    })

@login_required
@user_passes_test(is_admin)
def admin_dataset_delete(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    if request.method == 'POST':
        dataset.delete()
        messages.success(request, 'Dataset deleted successfully.')
        return redirect('admin_portal:admin_datasets')
    return render(request, 'admin_portal/dataset_confirm_delete.html', {'dataset': dataset})

@login_required
@user_passes_test(is_admin)
def admin_category_management(request):
    categories = Category.objects.all().prefetch_related('subcategories')
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', 'traffic')
        category_id = request.POST.get('category')
        subcategory_name = request.POST.get('subcategory_name')
        subcategory_description = request.POST.get('subcategory_description')
        
        if name and category_id:
            category = Category.objects.get(id=category_id)
            if icon:
                category.icon = icon
                category.save()
                messages.success(request, 'Category updated successfully.')
            if subcategory_name and subcategory_description:
                Subcategory.objects.create(
                    category=category,
                    name=subcategory_name,
                    description=subcategory_description
                )
                messages.success(request, 'Subcategory added successfully.')
            return redirect('admin_portal:admin_categories')
    return render(request, 'admin_portal/category_management.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def admin_user_management(request):
    role_filter = request.GET.get('role', 'all')
    users = Profile.objects.select_related('user').all()
    if role_filter != 'all':
        users = users.filter(role=role_filter)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if full_name and email and password:
            name_parts = full_name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, last_name=last_name
            )
            profile = user.profile
            profile.role = 'admin'
            profile.save()
            messages.success(request, 'Administrator account created successfully.')
            return redirect('admin_portal:admin_users')
    return render(request, 'admin_portal/user_management.html', {
        'users': users,
        'role_filter': role_filter,
        'categories': Category.objects.all(),
    })

@login_required
@user_passes_test(is_admin)
def admin_reports_view(request):
    return render(request, 'admin_portal/reports.html', {'categories': Category.objects.all()})

@login_required
@user_passes_test(is_admin)
def admin_messages(request):
    messages_list = ContactMessage.objects.all()
    return render(request, 'admin_portal/messages.html', {
        'messages_list': messages_list,
        'categories': Category.objects.all(),
    })

@login_required
@user_passes_test(is_admin)
def admin_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return render(request, 'admin_portal/message_detail.html', {
        'message': msg,
        'categories': Category.objects.all(),
    })

@login_required
@user_passes_test(is_admin)
def admin_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Message deleted successfully.')
        return redirect('admin_portal:admin_messages')
    return render(request, 'admin_portal/message_confirm_delete.html', {
        'message': msg,
        'categories': Category.objects.all(),
    })
