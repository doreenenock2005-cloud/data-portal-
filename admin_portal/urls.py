from django.urls import path
from admin_portal import views as admin_views

app_name = 'admin_portal'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('datasets/', admin_views.admin_dataset_management, name='admin_datasets'),
    path('datasets/edit/<int:pk>/', admin_views.admin_dataset_edit, name='admin_dataset_edit'),
    path('datasets/delete/<int:pk>/', admin_views.admin_dataset_delete, name='admin_dataset_delete'),
    path('categories/', admin_views.admin_category_management, name='admin_categories'),
    path('users/', admin_views.admin_user_management, name='admin_users'),
    path('reports/', admin_views.admin_reports_view, name='admin_reports'),
    path('messages/', admin_views.admin_messages, name='admin_messages'),
    path('messages/<int:pk>/read/', admin_views.admin_message_read, name='admin_message_read'),
    path('messages/<int:pk>/delete/', admin_views.admin_message_delete, name='admin_message_delete'),
]
