from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('', core_views.home, name='home'),
    path('datasets/', include('datasets.urls')),
    path('categories/', include('datasets.category_urls')),
    path('accounts/', include('accounts.urls')),
    path('api/v1/', include('api_app.urls')),
    path('admin-portal/', include('admin_portal.urls')),
    path('reports/', include('reports.urls')),
    path('about/', core_views.about, name='about'),
    path('contact/', core_views.contact, name='contact'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
