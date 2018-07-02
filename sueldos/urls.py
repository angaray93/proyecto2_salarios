"""sueldos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import django.contrib
import table
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from liquidacion import views

urlpatterns = [
    path('', auth_views.login, name = 'login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('liquidacion/', include('liquidacion.urls')),
    path('django_popup_view_field/', include('django_popup_view_field.urls', namespace="django_popup_view_field")),
    path('table/', include('table.urls')),
    path('home/', TemplateView.as_view(template_name='index.html'), name='home'),
]

handler404 = 'liquidacion.views.error_404_view'
handler500 = 'liquidacion.views.error_500_view'

