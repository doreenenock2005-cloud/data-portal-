from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from datasets.models import Dataset, Category
from accounts.models import Profile
from datetime import datetime, timedelta
import json
import pandas as pd

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def reports_view(request):
    datasets = Dataset.objects.all()
    categories = Category.objects.all()
    uploads_by_month = {}
    for i in range(6):
        month = datetime.now() - timedelta(days=30*i)
        label = month.strftime('%b')
        uploads_by_month[label] = Dataset.objects.filter(
            created_at__year=month.year, created_at__month=month.month
        ).count()
    download_by_category = []
    for cat in categories:
        count = Dataset.objects.filter(category=cat).aggregate(total=Sum('download_count'))['total'] or 0
        download_by_category.append({'category': cat.name, 'count': count})
    most_downloaded = datasets.order_by('-download_count')[:5]
    return render(request, 'admin_portal/reports.html', {
        'uploads_by_month': json.dumps(uploads_by_month),
        'download_by_category': json.dumps(download_by_category),
        'most_downloaded': most_downloaded,
        'total_users': Profile.objects.exclude(role='admin').count(),
        'researchers': Profile.objects.filter(role='researcher').count(),
        'developers': Profile.objects.filter(role='developer').count(),
        'active_users': Profile.objects.filter(is_active=True).exclude(role='admin').count(),
    })

@login_required
@user_passes_test(is_admin)
def export_reports_pdf(request):
    from weasyprint import HTML
    from django.template.loader import render_to_string
    html_string = render_to_string('admin_portal/reports_pdf.html', {})
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dportal_report.pdf"'
    return response

@login_required
@user_passes_test(is_admin)
def export_reports_excel(request):
    datasets = Dataset.objects.all().values('title', 'category__name', 'download_count', 'created_at', 'status')
    df = pd.DataFrame(list(datasets))
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="dportal_report.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datasets')
    return response
