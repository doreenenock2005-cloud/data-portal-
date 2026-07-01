from django.urls import path
from reports import views as report_views

app_name = 'reports'

urlpatterns = [
    path('', report_views.reports_view, name='reports_view'),
    path('export/pdf/', report_views.export_reports_pdf, name='export_reports_pdf'),
    path('export/excel/', report_views.export_reports_excel, name='export_reports_excel'),
]
