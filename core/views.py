from django.shortcuts import render, redirect
from datasets.models import Category, Subcategory
from core.models import ContactMessage
from django.contrib import messages

def home(request):
    categories = Category.objects.all().prefetch_related('subcategories')
    return render(request, 'core/home.html', {'categories': categories})

def about(request):
    categories = Category.objects.all()
    return render(request, 'core/about.html', {'categories': categories})

def contact(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if full_name and email and subject and message:
            ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                subject=subject,
                message=message,
            )
            messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'All fields are required.')
    return render(request, 'core/contact.html', {'categories': categories})
