from django.urls import path
from api_app import views as api_views

app_name = 'api_app'

urlpatterns = [
    path('', api_views.api_docs, name='api-docs'),
    path('datasets/', api_views.DatasetListAPI.as_view(), name='api-datasets'),
    path('datasets/<int:pk>/', api_views.DatasetDetailAPI.as_view(), name='api-dataset-detail'),
    path('categories/', api_views.CategoryListAPI.as_view(), name='api-categories'),
    path('subcategories/', api_views.SubcategoryListAPI.as_view(), name='api-subcategories'),
    path('categories/<slug:slug>/datasets/', api_views.CategoryDatasetsAPI.as_view(), name='api-category-datasets'),
    path('categories/<slug:cat_slug>/subcategories/<slug:sub_slug>/datasets/', api_views.SubcategoryDatasetsAPI.as_view(), name='api-subcategory-datasets'),
]
