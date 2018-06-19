from django.conf.urls import url, include
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from liquidacion.views import *
from . import views

app_name = 'liquidacion'

urlpatterns = [
    #path('accounts/login/', 'django.contrib.auth.views.login', name='login'),
    #path('accounts/logout/', 'django.contrib.auth.views.logout', name='logout'),
    path('home/', views.index, name='index'),
    path('opciones_proceso', views.opciones_proceso, name='opciones_proceso'),
    path('opciones_vacaciones', views.opciones_vacaciones, name='opciones_vacaciones'),
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
    path('liqpendientes/dpto/<int:iddpto>/mes/<int:mes>/anho/<int:anho>/', views.liq_pendientes_list, name='liq_pendientes_list'),
    path('editar_liquidacion/<int:idliquidacion>/', views.vista_liq_mensual, name='editar_liquidacion'),
    path('liquidacion_haber/<int:idliquidacionhaber>/', views.vista_liquidacionhaber, name='editar_liquidacionhaber'),
    path('liquidacionhaber/<int:idliquidacionhaber>/detalle/nuevo/', views.vista_detalleliquidacion, name='detalleliquidacion-add'),
    path('liquidacionhaber/<int:idliquidacionhaber>/detalle/<int:iddetalleliq>', views.vista_detalleliquidacion,
         name='detalleliquidacion-edit'),
    path('detalle/<int:pk>/delete/', views.delete_detalleliquidacion, name='detalleliquidacion-delete'),
    path('carga_vacaciones/', views.vacaciones_form, name='cargar_vacaciones'),
    path('liquidacion/pendientes/', views.liq_pendientes_filtro, name='liq_pendientes_filtro'),
    path('liqpendientes/funcionario/<int:funcionario>/mes/<int:mes>/', views.liq_funcionarios_list, name='liq_funcionarios_list'),
    path('ajax/traer_mes/', views.traer_mes, name='traer_mes'),
    path('liquidaciones/periodo/', views.liquidaciones_periodo, name='liquidaciones_periodo'),
    path('confirmar_liquidaciones/', views.confirmar_liquidaciones, name='confirmar_liquidaciones'),
    path('consulta_vacaciones/', views.consulta_vacaciones, name='consulta_vacaciones'),
    path('liquidaciones/confirmadas/periodo/', views.confirmadas_periodo, name='confirmadas_periodo'),
    path('liquidaciond/seleccion/', views.param_liq_definitiva, name='param_liq_definitiva'),
    path('liquidacion_baja/movimiento/<int:idmovimiento>/', views.generar_liq_definitiva, name='generar_liq_definitiva'),
   # path('pdf/', GeneratePdf.as_view()),
    path('pdf/', views.generate_view, name='generate_view'),
    path('liquidacion_filtro/', views.liquidacion_filtro, name='liquidacion_filtro'),

]