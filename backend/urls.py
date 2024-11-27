"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views  # Import your views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL for getting all invoices (GET method)
    path('api/invoices/', views.get_invoices, name='get_invoices'),

    # URL for creating a new invoice (POST method)
    path('api/invoices/create/', views.create_invoice, name='create_invoice'),

    # URL for updating an existing invoice (PUT method)
    path('api/invoices/update/', views.update_invoice, name='update_invoice'),

    # URL for deleting an invoice (DELETE method)
    path('api/invoices/delete/', views.delete_invoice, name='delete_invoice'),
]
