from django.conf.urls import url, include
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from liquidacion.views import *
from . import views

app_name = 'liquidacion'

urlpatterns = [
    path('', views.index, name='index'),
    #path('categoriasalarial_list', views.categoriasalarial_list, name='categoriasalarial_list'),
    #path('categoriasalarial/create/', views.vista_categoriasalarial, name='nueva_categoria'),
    path('opciones_proceso', views.opciones_proceso, name='opciones_proceso'),
    path('funcionario/<int:idfuncionario>/movimiento/nuevo/', views.movimiento_vista, name='nuevo_movimiento'),
    path('movimiento_padre/<int:idpadre>/', views.movimiento_vista, name='modificar_movimiento'),
    path('movimiento/<int:idmovimiento>', views.movimiento_vista, name='editar_movimiento'),
    path('buscar_funcionario', views.busqueda_funcionarios, name='buscar_funcionario'),
    path('buscar_movimiento', views.busqueda_movimiento_funcionario, name='buscar_movimiento'),
    path('get_movimientos', views.get_movimientos, name='get_movimientos'),
    path('movimiento/<int:idmovimiento>/documento/nuevo/', views.documento_vista, name='nuevo_documento'),
    path('movimiento/<int:idmovimiento>/documento/<int:iddocumento>', views.documento_vista, name='ver_documento'),
    path('movimiento/<int:idmovimiento>/constante/nuevo/', views.constante_vista, name='nueva_constante'),
    path('movimiento/<int:idmovimiento>/constante/<int:idconstante>', views.constante_vista, name='borrar_constante'),
    #path('django_popup_view_field/', include('django_popup_view_field.urls', namespace="django_popup_view_field")),
    path('categoriasalarial-list', CategoriaSalarialList.as_view(), name='categoriasalarial-list'),
    path('objetodegasto/add/', ObjetoDeGastoCreate.as_view(), name='objetodegasto-add'),
    path('tipomovimiento/add/', TipoMovimientoCreate.as_view(), name='tipomovimiento-add'),
    path('movimientomotivo/add/', MovimientoMotivoCreate.as_view(), name='movimientomotivo-add'),
    path('success_page/<int:idmovimiento>/', views.success_page, name='success_page'),
    path('movimiento_resumen/<int:idmovimiento>/', views.mostrar_movimiento_resumen, name='movimiento_resumen'),
    path('ajax/traer_tipomovimientos/', views.traer_tipomovimientos, name='traer_tipomovimientos'),
    path('ajax/traer_og/', views.traer_og, name='traer_og'),
    path('ajax/traer_motivomovimientos/', views.traer_motivomovimientos, name='traer_motivomovimientos'),
    path('buscarmovimientofuncionario/', views.buscar_movimientos_funcionario, name='buscar_movimientos_funcionario'),
    path('movimiento/<int:idmovimiento>/pago/nuevo/', views.pago_vista, name='nuevo_pago'),
    path('liquidacionm/seleccion/', views.parametros_liq_mensual, name='parametros_liq_mensual'),
    path('ajax/traer_departamentos/', views.traer_departamentos, name='traer_departamentos'),
    path('ajax/traer_funcionarios/', views.traer_funcionarios, name='traer_funcionarios'),
    path('liqpendientes/dpto/<int:iddpto>/mes/<int:mes>/', views.liq_pendientes_list, name='liq_pendientes_list'),
    path('editar_liquidacion/<int:idliquidacion>/', views.vista_liq_mensual, name='editar_liquidacion'),
    path('liquidacion_haber/<int:idliquidacionhaber>/', views.vista_liquidacionhaber, name='editar_liquidacionhaber'),

    #path('movimiento/<int:idmovimiento>/constante/<int:idconstante>', views.constante_vista, name='borrar_constante'),
]