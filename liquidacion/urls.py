from django.conf.urls import url, include
from django.urls import path

from . import views

app_name = 'liquidacion'

urlpatterns = [
    path('', views.index, name='index'),
    #path('categoriasalarial_list', views.categoriasalarial_list, name='categoriasalarial_list'),
    #path('categoriasalarial/create/', views.vista_categoriasalarial, name='nueva_categoria'),
    path('opciones_proceso', views.opciones_proceso, name='opciones_proceso'),
    path('funcionario/<int:idfuncionario>/movimiento/nuevo/', views.movimiento_vista, name='nuevo_movimiento'),
    path('movimiento/<int:idmovimiento>', views.movimiento_vista, name='modificar_movimiento'),
    path('movimiento/<int:idmovimiento>', views.movimiento_vista, name='ver_movimiento'),
    path('buscar_funcionario', views.busqueda_funcionarios, name='buscar_funcionario'),
    path('buscar_movimiento', views.busqueda_movimiento_funcionario, name='buscar_movimiento'),
    path('get_movimientos/<int:idfuncionario>', views.get_movimientos, name='get_movimientos'),
    path('movimiento/<int:idmovimiento>/documento/nuevo/', views.documento_vista, name='nuevo_documento'),
    path('movimiento/<int:idmovimiento>/documento/<int:iddocumento>', views.documento_vista, name='ver_documento'),
    path('movimiento/<int:idmovimiento>/constante/nuevo/', views.constante_vista, name='nueva_constante'),
    path('movimiento/<int:idmovimiento>/constante/<int:idconstante>', views.constante_vista, name='borrar_constante'),

]