from django.urls import path
from datasets import views as dataset_views

app_name = 'datasets'

urlpatterns = [
    path('', dataset_views.dataset_list, name='dataset_list'),
    path('<slug:slug>/', dataset_views.dataset_detail, name='dataset_detail'),
    path('<slug:slug>/download/', dataset_views.download_dataset, name='dataset_download'),
]
