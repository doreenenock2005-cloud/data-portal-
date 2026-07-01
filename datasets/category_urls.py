from django.urls import path
from datasets import views as dataset_views

app_name = 'categories'

urlpatterns = [
    path('', dataset_views.category_list, name='category_list'),
    path('<slug:slug>/', dataset_views.category_detail, name='category_detail'),
]
