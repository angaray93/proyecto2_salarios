from datetime import timedelta, timezone
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator
from django.db.models import *
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from liquidacion.forms import *
from liquidacion.mixins import AjaxFormMixin, AjaxTemplateMixin
from liquidacion.models import *
from django_popup_view_field.registry import registry_popup_view
import json

def index(request):
    return render(request, 'index.html')


def vista_liq_mensual(request, idliquidacion):
    context = {}
    advertencia = liquidacion= None
    if request.method == 'POST':
        if idliquidacion:
            liquidacion = get_object_or_404(Liquidacion, pk=idliquidacion)
        form = LiqMensualForm(request.POST, instance=liquidacion)
        if form.is_valid():
            liquidacion = form.save()
            if request.POST.get('descartar', '') == 'Descartar':
                print(request.POST.get('descartar', ''))
            return redirect(reverse('liquidacion:editar_liquidacion', args=[liquidacion.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
        return render(request, 'liquidacionmensual/liqmensual_form.html', context)
    else:
        if idliquidacion :
            liquidacion = get_object_or_404(Liquidacion, pk=idliquidacion)
            haberes = Haber.objects.filter(movimiento__funcionario=liquidacion.funcionario)
            if liquidacion.estado_actual.name == 'Nuevo':
                for haber in haberes:
                    liq_haber = Liquidacionhaber(
                        haber=haber,
                        liquidacion=liquidacion
                    )
                    liq_haber.save()
            liq_haberes = Liquidacionhaber.objects.filter(liquidacion=liquidacion)
            form = LiqMensualForm(instance=liquidacion)
            context.update({
                'form': form ,
                'liquidacion': liquidacion,
                'liq_haberes': liq_haberes,
            })
            try:
                transition = Transition.objects.get(process=liquidacion.estado_actual.process, currentState=liquidacion.estado_actual)
                liquidacion.estado_actual = transition.nextState
                liquidacion.save()
            except MultipleObjectsReturned:
                advertencia = 'Seleccione una accion para continuar'
                context.update({
                    'advertencia': advertencia,
                })
    return render(request, 'liquidacionmensual/liqmensual_form.html', context)


def parametros_liq_mensual(request):
    context = {}
    if request.method == 'POST':
        form = PreLiqMensualForm(request.POST)
        if form.is_valid():
            depto = form.cleaned_data['departamento']
            fechafin = form.cleaned_data['hasta']
            fechainicio = form.cleaned_data['desde']
            mes = fechafin.month
            funcionarios = Movimiento.objects\
                .filter(division__departamento=depto, estado__name='Activo')\
                .values('funcionario__idFuncionario').distinct('funcionario__idFuncionario')
            tipo = LiquidacionType.objects.get(nombre='Mensual')
            proceso = Process.objects.get(name='Liquidacion Mensual')
            initial_state_type = StateType.objects.get(name='Inicio')
            initial_state = State.objects.get(process=proceso, stateType=initial_state_type)
            #liquidaciones = []
            for mov in funcionarios:
                funcionario = Funcionario.objects.get(pk = mov['funcionario__idFuncionario'])
                liquidacion = Liquidacion(
                    fechacreacion=datetime.datetime.now(),
                    ultimamodificacion = datetime.datetime.now(),
                    mes = mes,
                    inicio_periodo = fechainicio,
                    fin_periodo = fechafin,
                    funcionario = funcionario,
                    estado_actual = initial_state,
                    tipo = tipo,
                    propietario = request.user,
                )
                #print(liquidacion)
                liquidacion.save()
                lista = True
                #liquidaciones.append(liquidacion)
                #print(liquidaciones)
            context.update({
                'lista': True,
                'form': form
            })
            return redirect(reverse('liquidacion:liq_pendientes_list', args=[depto, mes]))
        else:
            context.update({
                'errors': form.errors,
                'form': form
            })
        #return redirect(reverse('liquidacion:liq_pendientes_list', args=[depto, mes]))
    else:
        form = PreLiqMensualForm()
    return render(request, 'liquidacionmensual/liqmensual_filtro.html', {'form': form})


def liq_pendientes_list(request, iddpto, mes):
    context = {}
    estado = State.objects.get(stateType__name='Inicio', process__name='Liquidacion Mensual')
    departamento = Departamento.objects.get(pk=iddpto)
    funcionarios = Movimiento.objects \
        .filter(division__departamento=departamento, estado__name='Activo') \
        .values('funcionario__idFuncionario').distinct('funcionario__idFuncionario')
    liquidaciones = Liquidacion.objects.filter(mes=mes, estado_actual=estado, funcionario__idFuncionario__in= funcionarios)

    return render(request, 'liquidacionmensual/liqmensual_list.html', {'lista': liquidaciones, 'dpto': departamento})


def vista_liquidacionhaber(request, idliquidacionhaber):
    context = {}
    advertencia = liq_haber= None
    if request.method == 'POST':
        print('POST')
    else:
        if idliquidacionhaber :
            liq_haber = get_object_or_404(Liquidacionhaber, pk=idliquidacionhaber)
            constantes = Constante.objects.filter(movimiento=liq_haber.haber.movimiento)\
                .annotate(tot=Sum('monto'))

            print(constantes)
            form = LiquidacionhaberForm(instance=liq_haber)
            context.update({
                'form': form ,
                'liq_haber': liq_haber,
                'constantes': constantes,
            })
    return render(request, 'liquidacionmensual/liquidacionhaber_form.html', context)


def success_page(request, idmovimiento):
    context = {}
    context.update({
        'idmovimiento': idmovimiento,
    })
    return render(request, 'success_page.html', context)


def mostrar_movimiento_resumen(request, idmovimiento):
    context = {}
    movimiento = Movimiento.objects.get(pk=idmovimiento)
    aguinaldos = Aguinaldo.objects.filter(movimiento=movimiento)
    vacaciones = Vacaciones.objects.filter(movimiento=movimiento)
    constantes = Constante.objects.filter(movimiento=movimiento)
    context.update({
        'movimiento': movimiento,
        'aguinaldos': aguinaldos,
        'vacaciones': vacaciones,
        'constantes': constantes,
    })

    return render(request, 'proceso/resumen_movimiento.html', context)


def movimiento_vista(request, idmovimiento=None, idpadre=None, idfuncionario=None):
    context = {}
    movimiento = None
    proceso = Process.objects.get(name='Alta de Movimiento')
    if request.POST:
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
            form = MovimientoForm(request.POST, instance=movimiento)
            if form.is_valid():
                movimiento = form.save()
                return redirect(reverse('liquidacion:editar_movimiento', args=[movimiento.pk]))
            else:
                return render(request, 'proceso/movimiento_form.html', {'movimiento': movimiento, 'form': form})
        else:
            estado_default = State.objects.get(name='Activo', process=proceso)
            if idpadre:
                movimiento_padre = Movimiento.objects.get(pk=idpadre)
                funcionario = movimiento_padre.funcionario
                movimiento = Movimiento(
                    esPrimero = False,
                    estado = estado_default,
                    movimiento_padre = movimiento_padre,
                    funcionario = funcionario
                )
            else:
                movimiento_padre = None
                funcionario = Funcionario.objects.get(pk=idfuncionario)
                movimientos = Movimiento.objects.filter(funcionario=funcionario)
                if movimientos.count() > 0:
                    esPrimero = False
                else:
                    esPrimero = True
                movimiento = Movimiento(
                    esPrimero=esPrimero,
                    estado=estado_default,
                    movimiento_padre=movimiento_padre,
                    funcionario=funcionario,
                )

            form = MovimientoForm(request.POST, instance=movimiento)
            if form.is_valid():
                movimiento = form.save()
                #-------------------------------------------------------------------------#
                if movimiento.motivo.nombre != 'Contrato':
                    haber = None
                    if movimiento.movimiento_padre:
                        #----------------------------Haberes----------------------------------#
                        haber = Haber.objects.get(movimiento=movimiento.movimiento_padre)
                        haber.movimiento = movimiento
                        # ---------------------------Vacaciones-------------------------------#
                        try:
                            vacaciones_padre = Vacaciones.objects.get(movimiento=movimiento_padre)

                        except Vacaciones.DoesNotExist:
                            vacaciones_padre = None

                        if vacaciones_padre is not None:
                            vacaciones_padre.fin = movimiento.fechainicio - timedelta(days=1)
                            vacaciones_padre.save()
                        if movimiento.tieneVacaciones is True:
                            vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                            vacaciones.save()
                        if movimiento.tieneAguinaldo is True:
                            aguinaldo = Aguinaldo(movimiento = movimiento)
                            aguinaldo.save()
                        movimiento.movimiento_padre.estado = State.objects.get(nombre='Inactivo', process=proceso)
                        movimiento.movimiento_padre.fechafin = movimiento.fechainicio - timedelta(days=1)
                        #ToDo Dar de baja el haber del viejo movimiento y asignar el del nuevo en su lugar antes de que se guarde
                        movimiento.movimiento_padre.save()
                    else:
                        haber = Haber(movimiento = movimiento)
                        if movimiento.tieneAguinaldo is True:
                            aguinaldo = Aguinaldo(movimiento = movimiento)
                            aguinaldo.save()
                        if movimiento.tieneVacaciones is True:
                            vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                            vacaciones.save()
                    haber.save()
                    return redirect(reverse('liquidacion:success_page', args=[movimiento.pk]))
                else:
                    return redirect(reverse('liquidacion:nuevo_pago', args=[movimiento.pk]))

                #-------------------------------------------------------------------------#
            else:
                # TODO Implementar sistema de errores
                context.update({
                    'errors': form.errors,
                    'form': form
                })
    else:
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
            documentos = DocumentoRespaldatorio.objects.filter(movimiento=movimiento)
            constantes = Constante.objects.filter(movimiento=movimiento)
            form = MovimientoForm(instance=movimiento)
            """if movimiento.tieneAguinaldo is True:
                aguinaldo = Aguinaldo.objects.get(movimiento=movimiento)
                if not aguinaldo:
                    aguinaldo = Aguinaldo(movimiento=movimiento)
                print(aguinaldo)
                aguinaldo.cantidad_meses = aguinaldo.calcular_cantidad_meses()
                aguinaldo.save()
                print(aguinaldo.cantidad_meses)"""
            context.update({
                'movimiento': movimiento,
                'documentos': documentos,
                'constantes': constantes,
                'form': form
            })
        else:
            if idpadre:
                movimiento_padre = Movimiento.objects.get(pk=idpadre)
                funcionario = movimiento_padre.funcionario
                context.update({
                    'movimiento_padre': movimiento_padre,
                })
            else:
                movimiento_padre = None
                q = request.GET.get('term', '')
                funcionario = Funcionario.objects.get(pk=idfuncionario)
            estado_default = State.objects.get(name='Activo', process=proceso)

            form = MovimientoForm(initial={
                'funcionario': funcionario,
                'movimiento_padre': movimiento_padre,
                'estado': estado_default,
            })
            context.update({
                'funcionario': funcionario,
                'form': form,
            })
    return render(request, 'proceso/movimiento_form.html', context)


def opciones_proceso(request):
    return render(request, 'proceso/opciones_proceso.html')


def busqueda_funcionarios(request):
    choice = request.GET.get("q")
    queryset_list = Funcionario.objects.all()
    recibido = request.GET.get("q")
    if recibido:
        queryset_list = queryset_list.filter\
            (Q(nombres__icontains=recibido) | Q(apellidos__icontains=recibido) | Q(cedula__icontains=recibido))

    return render(request, 'proceso/filtro_funcionarios_movimiento.html', {'funcionarios': queryset_list})


def busqueda_movimiento_funcionario(request):
    choice = request.GET.get("q")
    queryset_list = Funcionario.objects.all()
    recibido = request.GET.get("q")
    if recibido:
        queryset_list = queryset_list.filter\
            (Q(nombres__icontains=recibido) | Q(apellidos__icontains=recibido) | Q(cedula__icontains=recibido))

    return render(request, 'proceso/seleccion_movimiento_funcionario.html', {'funcionarios': queryset_list})


def get_movimientos(request):
    if request.is_ajax():
        q = request.GET.get('idfuncionario', '')
        movimientos = Movimiento.objects.filter(funcionario=q, estado__name = 'Activo')
        res = []
        for movimiento in movimientos:
            movimiento_json = {'idmovimiento' :movimiento.pk, 'motivo': movimiento.motivo.nombre, 'tipo': movimiento.tipo.nombre, 'categoria_salarial': movimiento.categoria_salarial.codigo}
            res.append(movimiento_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def documento_vista(request, idmovimiento=None, iddocumento=None):
    context = {}
    documento = None
    if request.POST:
        if iddocumento:
            documento = get_object_or_404(DocumentoRespaldatorio, pk=iddocumento)
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            documento = DocumentoRespaldatorio(
                movimiento=movimiento,
            )
        form = DocumentoRespaldatorioForm(request.POST, instance=documento)
        if form.is_valid():
            documento = form.save()
            return redirect(reverse('liquidacion:editar_movimiento', args=[documento.movimiento.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            return render(request, 'proceso/documento_form.html', context)
    else:
        if iddocumento:
            documento = get_object_or_404(DocumentoRespaldatorio, pk=iddocumento)
            form = DocumentoRespaldatorioForm(instance=documento)
            context.update({
                'documento': documento,
                'form': form
            })
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            form = DocumentoRespaldatorioForm(initial={
                'movimiento': movimiento,
            })
            context.update({
                'movimiento': movimiento,
                'form': form,
            })
        return render(request, 'proceso/documento_form.html', context)


def aguinaldo_vista(request, idmovimiento=None, idaguinaldo=None):
    context = {}
    aguinaldo = None
    if request.POST:
        if idaguinaldo:
            aguinaldo = get_object_or_404(Aguinaldo, pk=idaguinaldo)
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            aguinaldo = Aguinaldo(
                movimiento=movimiento,
            )
        form = AguinaldoForm(request.POST, instance=aguinaldo)
        if form.is_valid():
            aguinaldo = form.save()
            return redirect(reverse('liquidacion:ver_movimiento', args=[aguinaldo.movimiento.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            return render(request, 'aguinaldo/aguinaldo_form.html', context)
    else:
        if idaguinaldo:
            aguinaldo = get_object_or_404(Aguinaldo, pk=idaguinaldo)
            form = AguinaldoForm(request.POST, instance=aguinaldo)
            context.update({
                'aguinaldo': aguinaldo,
                'form': form
            })
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            form = AguinaldoForm(initial={
                'movimiento': movimiento,
            })
            context.update({
                'movimiento': movimiento,
                'form': form,
            })
        return render(request, 'aguinaldo/aguinaldo_form.html', context)


def constante_vista(request, idmovimiento=None, idconstante=None):
    context = {}
    constante = None
    if request.POST:
        if idconstante:
            constante = get_object_or_404(Constante, pk=idconstante)
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            constante = Constante(
                movimiento=movimiento,
            )
        form = ConstanteForm(request.POST, instance=constante)
        if form.is_valid():
            constante = form.save()
            constante.monto = constante.calcular_monto()
            constante.save()
            return redirect(reverse('liquidacion:nueva_constante', args=[constante.movimiento.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            return render(request, 'constante/constante_form.html', context)
    else:
        if idconstante:
            constante = get_object_or_404(Constante, pk=idconstante)
            form = ConstanteForm(request.POST, instance=constante)
            context.update({
                'constante': constante,
                'form': form
            })
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            constantes = Constante.objects.filter(movimiento=movimiento)
            form = ConstanteForm(initial={
                'movimiento': movimiento,
            })
            context.update({
                'movimiento': movimiento,
                'constantes': constantes,
                'form': form,
            })
        return render(request, 'constante/constante_form.html', context)


def pago_vista(request, idmovimiento=None, idpago=None):
    context = {}
    pago = None
    if request.POST:
        if idpago:
            pago = get_object_or_404(Pago, pk=idpago)
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            pago = Pago(
                movimiento=movimiento,
            )
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            pago = form.save()
            return redirect(reverse('liquidacion:nuevo_pago', args=[pago.movimiento.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            return render(request, 'pago_form.html', context)
    else:
        if idpago:
            pago = get_object_or_404(Constante, pk=idpago)
            form = PagoForm(request.POST, instance=idpago)
            context.update({
                'pago': pago,
                'form': form
            })
        else:
            movimiento = Movimiento.objects.get(pk=idmovimiento)
            pagos = Pago.objects.filter(movimiento=movimiento)
            form = PagoForm(initial={
                'movimiento': movimiento,
            })
            context.update({
                'movimiento': movimiento,
                'pagos': pagos,
                'form': form,
            })
        return render(request, 'pago_form.html', context)


class CategoriaSalarialList(ListView):
        model = CategoriaSalarial
        template_name = 'categoriasalarial_list.html'
        context_object_name = 'page_obj'


class ObjetoDeGastoCreate(AjaxTemplateMixin, CreateView):
    form_class = Objeto_De_GastoAdminForm
    template_name  = 'objetodegasto_form.html'
    success_url = reverse_lazy('liquidacion:objetodegasto-add')


class TipoMovimientoCreate(AjaxTemplateMixin, CreateView):
    form_class = MovimientoTypeForm
    template_name  = 'tipomovimiento_form.html'
    success_url = reverse_lazy('liquidacion:tipomovimiento-add')


class MovimientoMotivoCreate(AjaxTemplateMixin, CreateView):
    form_class = MovimientoMotivoForm
    template_name  = 'movimientomotivo_form.html'
    success_url = reverse_lazy('liquidacion:movimientomotivo-add')


@require_GET
def traer_og(request):
    if request.is_ajax():
        ogs = Objeto_De_Gasto.objects.all()
        res = []
        for og in ogs:
            og_json = {'id': og.pk, 'value': og.numero, 'value2': og.concepto}
            res.append(og_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@require_GET
def traer_tipomovimientos(request):
    if request.is_ajax():
        tipomovimientos = MovimientoType.objects.all()
        res = []
        for tipomovimiento in tipomovimientos:
            tipomovimiento_json = {'id': tipomovimiento.pk, 'value': tipomovimiento.nombre}
            res.append(tipomovimiento_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@require_GET
def traer_motivomovimientos(request):
    if request.is_ajax():
        motivomovimientos = MovimientoMotivo.objects.all()
        res = []
        for motivomovimiento in motivomovimientos:
            motivomovimiento_json = {'id': motivomovimiento.pk, 'value': motivomovimiento.nombre}
            res.append(motivomovimiento_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required()
@require_GET
def buscar_movimientos_funcionario(request):
    vista = 'buscar_movimientos_funcionario'

    if request.GET.get('q'):
        form = BusquedaMovimientoFuncionarioForm(request.GET)

        if not form.has_changed():
            sin_datos = 'Ingrese todos los datos solicitados'
            return render(request, 'reportes/filtro_movimiento_funcionario.html', {'form': BusquedaMovimientoFuncionarioForm(initial=request.GET),
                                                          'sin_datos': sin_datos, 'vista': vista})
        if form.is_valid():
            context = {}
            cedula = form.cleaned_data['cedula']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            context.update({
                'nombres': nombres,
                'apellidos': apellidos,
            })

            f = Q(funcionario__cedula = cedula) | \
                Q(funcionario__nombres__icontains = nombres) | \
                Q(funcionario__apellidos__icontains = apellidos)

            movimientos = Movimiento.objects.filter(f)

            context.update({
                'form': BusquedaMovimientoFuncionarioForm(initial=request.GET),
                'movimientos': movimientos,
                'vista': vista,
            })
            if movimientos.count() == 0:
                sin_datos = 'Sin resultados'
                return render(request, 'reportes/filtro_movimiento_funcionario.html', {'form': BusquedaMovimientoFuncionarioForm(initial=request.GET),
                                                              'sin_datos': sin_datos, 'vista': vista})

            return render(request, 'reportes/filtro_movimiento_funcionario.html', context)

    else:
        return render(request, 'reportes/filtro_movimiento_funcionario.html', {'form': BusquedaMovimientoFuncionarioForm(), 'vista': vista})


@require_GET
def traer_departamentos(request):
    if request.is_ajax():
        departamentos = Departamento.objects.all()
        res = []
        for departamento in departamentos:
            departamento_json = {'id': departamento.pk, 'value': departamento.nombre}
            res.append(departamento_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@require_GET
def traer_funcionarios(request):
    if request.is_ajax():
        funcionarios = Funcionario.objects.all()\
            .values("idFuncionario").order_by('-idFuncionario').distinct('idFuncionario')
        iddepartamento = request.GET.get('iddepartamento', '')
        if iddepartamento != 0:
            funcionarios = Movimiento.objects.filter(estado__name='Activo', division__departamento=iddepartamento)\
                .values('funcionario__idFuncionario','funcionario__nombres', 'funcionario__apellidos')\
                .order_by('-funcionario__idFuncionario').distinct('funcionario__idFuncionario')
        res = []
        for f in funcionarios:
            func_json = {'id': f['funcionario__idFuncionario'], 'value': f['funcionario__nombres'], 'value2': f['funcionario__apellidos']}
            res.append(func_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
