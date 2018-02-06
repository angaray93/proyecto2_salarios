from django.conf.urls import url, include

from . import views

app_name = 'liquidacion'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^categoriasalarial_list', views.categoriasalarial_list, name='categoriasalarial_list'),
    url(r'^categoriasalarial/create/$', views.vista_categoriasalarial, name='nueva_categoria'),

]