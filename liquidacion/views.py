from datetime import timedelta, timezone, date, time
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import *
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template.loader import render_to_string, get_template
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from liquidacion.forms import *
from liquidacion.mixins import AjaxFormMixin, AjaxTemplateMixin
from liquidacion.models import *
import json
from liquidacion.tables import LiquidacionMensualTable
from django.http import HttpResponse
from django.views import View
from liquidacion.utils import render_to_pdf

def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@login_required
def print_liquidacion(request, idliquidacion):
    liquidacion = Liquidacion.objects.get(pk=idliquidacion)
    liq_haberes = Liquidacionhaber.objects.filter(liquidacion=liquidacion).order_by('pk')
    movimientos = Movimiento.objects.filter(
        pk__in=Subquery(liq_haberes.values('haber__movimiento__idmovimiento')))
    detalles = DetalleLiquidacion.objects.filter(liquidacion_haber__in=liq_haberes)

    template = get_template('reportes/print_liquidacionmensual.html')
    context = {
        'liquidacion': liquidacion,
        'haberes' : liq_haberes,
        'detalles' : detalles,
    }
    html = template.render(context)
    pdf = render_to_pdf('reportes/print_liquidacionmensual.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "liquidacionm_%s.pdf" % ("12341231")
        content = "inline; filename='%s'" % (filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required
def informe_altasbajas(request):
    context = {}
    if request.method == 'POST':
        form = FilroTipoMovimientoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            fechafin = form.cleaned_data['hasta']
            fechainicio = form.cleaned_data['desde']

            if tipo == 'Alta':
                f = ~Q(tipo__nombre='Baja') & Q(fechainicio__gte=fechainicio) & Q(fechainicio__lte=fechafin)
                lista = Movimiento.objects.filter(f)
            else:
                f = Q(liquidacion__tipo__nombre='Definitiva') & Q(liquidacion__fechacreacion__gte=fechainicio) & Q(liquidacion__fechacreacion__lte = fechafin)
                lista = Liquidacionhaber.objects.filter(f)

            template = get_template('reportes/filtro_altasybajas.html')
            context = {
                'lista' : lista,
                'tipo' : tipo,
                'fechainicio' : fechainicio,
                'fechafin' : fechafin,
            }
            html = template.render(context)
            pdf = render_to_pdf('reportes/print_altasybajas.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "file_%s.pdf" % ("12341231")
                content = "inline; filename='%s'" % (filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" % (filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
    else:
        form = FilroTipoMovimientoForm()
    return render(request, 'reportes/filtro_altasybajas.html', {'form': form})


@login_required
def monto_objetodegasto(request):
    context = {}
    if request.method == 'POST':
        form = FiltroMesForm(request.POST)
        if form.is_valid():
            mespk = form.cleaned_data['mes']
            og_lista = Objeto_De_Gasto.objects.filter(~Q(numero=111))

            if mespk != '0':
                lista_og = []
                valores = []
                mes = Mes.objects.get(numero=mespk, year=datetime.datetime.now().year)
                for og in og_lista:
                    og_nombre = {}
                    datos = Liquidacionhaber.objects.filter(liquidacion__mes=mes,
                                                            liquidacion__estado_actual__name='Confirmado',
                                                            haber__movimiento__motivo=MovimientoMotivo.objects.get(nombre='Contrato'),
                                                            haber__movimiento__og=og)\
                        .aggregate(
                            monto_mes=Sum('pago__monto', filter=Q(liquidacion__mes=mes)),
                        )
                    valores.append(datos)
                    if len(valores) != 0:
                        primes = list(valores)
                        og_nombre.update({
                            og: primes,
                        })
                        lista_og.append(og_nombre)
                        valores.clear()

                context.update({
                    'mes': mes,
                    'anho': mes.year,
                    'lista': lista_og,
                })
            else:
                lista_og = []
                valores = []
                for og in og_lista:
                    og_nombre = {}
                    datos = Liquidacionhaber.objects.filter(liquidacion__estado_actual__name='Confirmado',
                                                            haber__movimiento__motivo=MovimientoMotivo.objects.get(
                                                                nombre='Contrato'), haber__movimiento__og=og) \
                        .aggregate(
                            enero=Sum('pago__monto', filter=Q(liquidacion__mes__numero=1)),
                            febrero=Sum('pago__monto', filter=Q(liquidacion__mes__numero=2)),
                            marzo=Sum('pago__monto', filter=Q(liquidacion__mes__numero=3)),
                            abril=Sum('pago__monto', filter=Q(liquidacion__mes__numero=4)),
                            mayo=Sum('pago__monto', filter=Q(liquidacion__mes__numero=5)),
                            junio=Sum('pago__monto', filter=Q(liquidacion__mes__numero=6)),
                            julio=Sum('pago__monto', filter=Q(liquidacion__mes__numero=7)),
                            agosto=Sum('pago__monto', filter=Q(liquidacion__mes__numero=8)),
                            septiembre=Sum('pago__monto', filter=Q(liquidacion__mes__numero=9)),
                            octubre=Sum('pago__monto', filter=Q(liquidacion__mes__numero=10)),
                            noviembre=Sum('pago__monto', filter=Q(liquidacion__mes__numero=11)),
                            diciembre=Sum('pago__monto', filter=Q(liquidacion__mes__numero=12)),
                    )
                    valores.append(datos)
                    if len(valores) != 0:
                        primes = list(valores)
                        og_nombre.update({
                            og: primes,
                        })
                        lista_og.append(og_nombre)
                        valores.clear()
                print(lista_og)
                context.update({
                    'anho': datetime.datetime.now().year,
                    'lista': lista_og,
                })

            template = get_template('reportes/filtro_monto_objetodegasto.html')

            html = template.render(context)
            pdf = render_to_pdf('reportes/print_monto_objetodegasto.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "file_%s.pdf" % ("12341231")
                content = "inline; filename='%s'" % (filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" % (filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
    else:
        form = FiltroMesForm()
    return render(request, 'reportes/filtro_monto_objetodegasto.html', {'form': form})


@login_required
def nomina_funcionarios(request):
    context = {}
    if request.method == 'POST':
        form = FiltroDepartamentoForm(request.POST)
        if form.is_valid():
            dpto = form.cleaned_data['departamento']
            departamentos = Departamento.objects.all()
            if dpto != 0:
                departamentos = Departamento.objects.get(pk=dpto)
                context.update({
                    'departamento': departamentos,
                })
                movimientos = Movimiento.objects\
                    .filter(division__departamento=departamentos, estado__name='Activo').order_by('division__departamento')
            else:
                movimientos = Movimiento.objects \
                    .filter(division__departamento__in=departamentos, estado__name='Activo').order_by('division__departamento')

            template = get_template('reportes/filtro_nomina_funcionarios.html')
            context = {
                'movimientos': movimientos,
            }
            html = template.render(context)
            pdf = render_to_pdf('reportes/print_nominafuncionarios.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "file_%s.pdf" % ("12341231")
                content = "inline; filename='%s'" % (filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" % (filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
    else:
        form = FiltroDepartamentoForm()
    return render(request, 'reportes/filtro_nomina_funcionarios.html', {'form': form})


@require_GET
def traer_departamentos(request):
    if request.is_ajax():
        departamentos = Departamento.objects.all()
        res = []
        for departamento in departamentos:
            departamento_json = {'id': departamento.pk, 'value': departamento.descripcion}
            res.append(departamento_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required
def informe_vacaciones(request):
    context = {}
    if request.method == 'POST':
        form = VacacionesFuncionarioForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['funcionario']
            funcionario = Funcionario.objects.get(cedula=cedula)
            vacaciones = Vacaciones.objects.filter(movimiento__funcionario=funcionario).order_by('-inicio')

            template = get_template('reportes/filtro_informevacaciones.html')
            context = {
                'vacaciones': vacaciones,
                'funcionario': funcionario,
            }
            html = template.render(context)
            pdf = render_to_pdf('reportes/print_informevacaciones.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "file_%s.pdf" % ("12341231")
                content = "inline; filename='%s'" % (filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" % (filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
    else:
        form = VacacionesFuncionarioForm()
    return render(request, 'reportes/filtro_informevacaciones.html', {'form': form})


@login_required
def gastosxtipomovimiento(request):
    context = {}
    if request.method == 'POST':
        form = FiltroGastosForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            anho = form.cleaned_data['anho']
            contrato = MovimientoMotivo.objects.get(nombre='Contrato')

            if motivo == 'Contrato':
                monto = Liquidacionhaber.objects.filter(haber__movimiento__motivo=contrato, liquidacion__mes__year=anho)\
                    .values('liquidacion__mes__nombre').annotate(sumames=Sum('subTotal')).order_by('liquidacion__mes__numero')
            else:
                monto = Liquidacionhaber.objects.filter(~Q(haber__movimiento__motivo=contrato) & Q(liquidacion__mes__year=anho)) \
                    .values('liquidacion__mes__nombre').annotate(sumames=Sum('subTotal')).order_by('liquidacion__mes__numero')

            template = get_template('reportes/filtro_gastos_motivomovimiento.html')
            context = {
                'motivo': motivo,
                'monto': monto,
                'anho': anho,
            }
            html = template.render(context)
            pdf = render_to_pdf('reportes/print_gastos_motivomovimiento.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "file_%s.pdf" % ("12341231")
                content = "inline; filename='%s'" % (filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" % (filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
    else:
        form = FiltroGastosForm()
    return render(request, 'reportes/filtro_gastos_motivomovimiento.html', {'form': form})


@login_required
def historico_movimientos(request):
    context = {}
    if request.method == 'POST':
        form = LiquidacionDefinitivaForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['funcionario']
            try:
                funcionario = Funcionario.objects.get(cedula=cedula)
            except Funcionario.DoesNotExist:
                messages.error(request, "No existe funcionario con estas caracteristicas")
                return redirect(reverse('liquidacion:param_liq_definitiva'))

            movimientos = Movimiento.objects.filter(funcionario=funcionario).order_by('familia','fechainicio')
            if movimientos.count() == 0 :
                messages.error(request, "Sin resultados")
                return redirect(reverse('liquidacion:param_liq_definitiva'))
            else:
                template = get_template('reportes/filtro_historicomovimiento.html')
                context = {
                    'movimientos': movimientos,
                    'funcionario': funcionario,
                }
                html = template.render(context)
                pdf = render_to_pdf('reportes/print_historicomovimiento.html', context)
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "file_%s.pdf" % ("12341231")
                    content = "inline; filename='%s'" % (filename)
                    download = request.GET.get("download")
                    if download:
                        content = "attachment; filename='%s'" % (filename)
                    response['Content-Disposition'] = content
                    return response
                return HttpResponse("Not found")
    else:
        form = LiquidacionDefinitivaForm()
    return render(request, 'reportes/filtro_historicomovimiento.html', {'form': form})


@login_required
def liquidacion_filtro(request):
    context = {}
    if request.method == 'POST':
        form = LiqPendientesForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['funcionario']
            funcionario = Funcionario.objects.get(cedula=cedula)
            imes = form.cleaned_data['mes']
            anho = form.cleaned_data['anho']
            mes = Mes.objects.get(numero=imes, year=anho)
            try:
                liquidacion = Liquidacion.objects.get(mes=mes, funcionario__cedula=cedula, tipo__nombre='Mensual')
            except Liquidacion.DoesNotExist:
                messages.error(request, "Sin resultados")
                return redirect(reverse('liquidacion:liquidacion_filtro'))
            if liquidacion:
                liq_haberes = Liquidacionhaber.objects.filter(liquidacion=liquidacion).order_by('pk')
                movimientos = Movimiento.objects.filter(
                    pk__in=Subquery(liq_haberes.values('haber__movimiento__idmovimiento')))
                detalles = DetalleLiquidacion.objects.filter(liquidacion_haber__in=liq_haberes)

                template = get_template('reportes/print_liquidacionmensual.html')
                context = {
                    'liquidacion': liquidacion,
                    'haberes' : liq_haberes,
                    'detalles' : detalles,
                }
                html = template.render(context)
                pdf = render_to_pdf('reportes/print_liquidacionmensual.html', context)
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "liquidacionm_%s.pdf" % ("12341231")
                    content = "inline; filename='%s'" % (filename)
                    download = request.GET.get("download")
                    if download:
                        content = "attachment; filename='%s'" % (filename)
                    response['Content-Disposition'] = content
                    return response
                return HttpResponse("Not found")
                #return render(request, 'reportes/liquidacionmensual.html', {'form': form})
    else:
        form = LiqPendientesForm()
    return render(request, 'reportes/filtro_liquidacion.html', {'form': form})


@login_required
def generate_view(request, *args, **kwargs):
    template = get_template('pdf/invoice.html')
    lista = Division.objects.all()
    context = {
        'today': datetime.date.today(),
        'amount': 39.99,
        'customer_name': 'Cooper Mann',
        'order_id': 1233434,
        'lista' : lista,
    }
    html = template.render(context)
    pdf = render_to_pdf('pdf/invoice.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "liquidacionmensual_%s.pdf" % ("12341231")
        content = "inline; filename='%s'" % (filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def generar_liq_definitiva(request, idmovimiento):
    context = {}
    advertencia = liquidacion = None

    if idmovimiento:
        movimiento = Movimiento.objects.get(pk=idmovimiento)
        try:
            liquidacion = Liquidacion.objects.get(funcionario = movimiento.funcionario,
                                                  tipo__nombre='Definitiva', mes__numero=datetime.datetime.now().month)
        except Liquidacion.DoesNotExist:
            liquidacion = None
        if liquidacion == None:
            tipo = LiquidacionType.objects.get(nombre='Definitiva')
            proceso = Process.objects.get(name='Liquidacion Mensual')
            initial_state_type = StateType.objects.get(name='Inicio')
            initial_state = State.objects.get(process=proceso, stateType=initial_state_type)
            funcionario = Funcionario.objects.get(pk=movimiento.funcionario.idFuncionario)
            fecha_hoy = datetime.datetime.now()
            mes = Mes.objects.get(numero=datetime.datetime.now().month, year=datetime.datetime.now().year)
            existe_pago = True
            liquidacion = Liquidacion(
                fechacreacion = datetime.datetime.now(),
                ultimamodificacion = datetime.datetime.now(),
                mes = mes,
                inicio_periodo = fecha_hoy.replace(day=1),
                fin_periodo = fecha_hoy,
                funcionario = funcionario,
                estado_actual = initial_state,
                tipo = tipo,
                propietario=request.user,
            )
            try:
                liquidacion.save()
            except IntegrityError:
                messages.error(request, "Ya se ha creado las liquidaciones salariales de este departamento para el mes")
                return redirect(reverse('liquidacion:param_liq_definitiva'))

            liquidacion.dias_trabajados = (liquidacion.fin_periodo - liquidacion.inicio_periodo).days + 1
            liquidacion.save()

        haber = Haber.objects.get(movimiento=movimiento, estado__name='Activo')
        print('Liquidacion del movimiento numero :', haber.movimiento.pk)
        if haber.movimiento.motivo.nombre == 'Contrato' and haber.movimiento.formapago == 'M':
            liq_haber = None
            try:
                pago = Pago.objects.get(movimiento=haber.movimiento, mes=liquidacion.mes)
                existe_pago = True
            except Pago.DoesNotExist:
                pago = None
                existe_pago = False
                messages.warning(request, "No existe pagos asociados a este cargo")
                return redirect(reverse('liquidacion:param_liq_definitiva'))
            if existe_pago is True:
                liq_haber = Liquidacionhaber(
                    haber=haber,
                    liquidacion=liquidacion,
                    pago=pago,
                )
                liq_haber.save()
        else:
            liq_haber = Liquidacionhaber(
                haber=haber,
                liquidacion=liquidacion,
            )
        try:
            liq_haber.save()
        except IntegrityError:
            messages.error(request, "Ya se ha creado una liquidacion para este movimiento")
            return redirect(reverse('liquidacion:param_liq_definitiva'))

        liq_haber.salario_proporcional = liq_haber.calculo_salario_proporcional()
        liq_haber.monto_debito = liq_haber.suma_detalles_debito()
        liq_haber.monto_credito = liq_haber.suma_detalles_credito()
        liq_haber.subTotal = round(liq_haber.monto_credito - liq_haber.monto_debito, 0)

        if liq_haber.haber.movimiento.motivo.nombre == 'Contrato':
            salario_mes = DetalleLiquidacion(
                cantidad=1,
                monto=liq_haber.salario_proporcional,
                total_detalle=liq_haber.salario_proporcional,
                parametro=Parametro.objects.get(descripcion='Monto'),
                variable=Variable.objects.get(motivo='Asignacion Salarial'),
                liquidacion_haber=liq_haber,
                constante=Constante.objects.get(tipo__nombre='Asignacion Salarial',
                                                movimiento=liq_haber.haber.movimiento)
            )
        else:
            salario_mes = DetalleLiquidacion(
                cantidad=1,
                monto=liq_haber.salario_proporcional,
                total_detalle=liq_haber.salario_proporcional,
                parametro=Parametro.objects.get(descripcion='Monto'),
                variable=Variable.objects.get(motivo='Asignacion Salarial'),
                liquidacion_haber=liq_haber,
                constante = Constante.objects.get(tipo__nombre='Asignacion Salarial',
                                              movimiento=liq_haber.haber.movimiento)
            )
        salario_mes.save()

        try:
            aguinaldo = Aguinaldo.objects.get(movimiento=liq_haber.haber.movimiento,
                                              anho=datetime.datetime.now().year)
        except Aguinaldo.DoesNotExist:
            aguinaldo = None
        if aguinaldo != None:
            if liq_haber.haber.movimiento.tieneAguinaldo is True:
                aguinaldo_prop = DetalleLiquidacion(
                    cantidad=1,
                    monto=aguinaldo.total,
                    parametro = Parametro.objects.get(descripcion='Monto'),
                    variable = Variable.objects.get(motivo='Aguinaldo'),
                    liquidacion_haber = liq_haber,
                    constante = Constante.objects.get(tipo__nombre='Aguinaldo', movimiento=liq_haber.haber.movimiento)
                )
                aguinaldo_prop.save()

        #------------------------------VACACIONES-----------------------------------#
        if liq_haber.haber.movimiento.tieneVacaciones is True:
            cantidad_vacaciones = Vacaciones.objects.filter(movimiento__funcionario=liquidacion.funcionario,
                                                            movimiento__estado__name='Activo')\
                .aggregate(dias_acumulados=Sum('dias_restantes'))
            monto_vacaciones = round(cantidad_vacaciones['dias_acumulados'] * (liq_haber.haber.movimiento.categoria_salarial.asignacion / 30))
            constante = Constante.objects.get(tipo__nombre='Vacaciones', movimiento=liq_haber.haber.movimiento)
            constante.monto = monto_vacaciones
            constante.save()

        constantes_movimiento = Constante.objects.filter(movimiento=liq_haber.haber.movimiento)
        for constante in constantes_movimiento:
            if constante.tipo.nombre != 'Asignacion Salarial' and constante.tipo.nombre != 'Aguinaldo' :
                if constante.tipo.porcentaje:
                    detalleliquidacion = DetalleLiquidacion(
                        cantidad=1,
                        monto=0,
                        parametro=Parametro.objects.get(descripcion='Monto'),
                        variable=Variable.objects.get(motivo=constante.tipo.nombre),
                        liquidacion_haber=liq_haber,
                        constante=constante,
                    )
                else:
                    detalleliquidacion = DetalleLiquidacion(
                        cantidad=1,
                        monto=constante.monto,
                        parametro=Parametro.objects.get(descripcion='Monto'),
                        variable=Variable.objects.get(motivo=constante.tipo.nombre),
                        liquidacion_haber=liq_haber,
                        constante=constante,
                    )
                detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                detalleliquidacion.save()
                if detalleliquidacion.variable.tipo == 'D':
                    detalleliquidacion.liquidacion_haber.monto_debito = detalleliquidacion.liquidacion_haber.suma_detalles_debito()
                else:
                    detalleliquidacion.liquidacion_haber.monto_credito = detalleliquidacion.liquidacion_haber.suma_detalles_credito()
                detalleliquidacion.liquidacion_haber.save()
                detalleliquidacion.liquidacion_haber.subTotal = detalleliquidacion.liquidacion_haber.calcular_total()
                detalleliquidacion.liquidacion_haber.save()
                detalleliquidacion.liquidacion_haber.liquidacion.total_credito = detalleliquidacion.liquidacion_haber.liquidacion.calculo_total_credito()
                detalleliquidacion.liquidacion_haber.liquidacion.total_debito = detalleliquidacion.liquidacion_haber.liquidacion.calculo_total_debito()
                detalleliquidacion.liquidacion_haber.liquidacion.total_liquidacion = detalleliquidacion.liquidacion_haber.liquidacion.calcular_total_liquidacion()
                detalleliquidacion.liquidacion_haber.liquidacion.save()

    return redirect(reverse('liquidacion:editar_liquidacionhaber', args=[liq_haber.pk]))


@login_required()
@require_GET
def param_liq_definitiva(request):
    vista = 'param_liq_definitiva'
    if request.GET.get('q'):
        form = LiquidacionDefinitivaForm(request.GET)
        if not form.has_changed():
            sin_datos = 'Ingrese todos los datos solicitados'
            return render(request, 'liquidacionbaja/filtro_liq_definitiva.html',
                          {'form': LiquidacionDefinitivaForm(initial=request.GET),
                           'sin_datos': sin_datos, 'vista': vista})
        if form.is_valid():
            context = {}
            funcionario = form.cleaned_data['funcionario']
            context.update({
                'funcionario': funcionario,
            })
            listado_movimientos = Movimiento.objects.filter(funcionario__cedula=funcionario, estado__name='Activo')

            context.update({
                'form': LiquidacionDefinitivaForm(initial=request.GET),
                'listado_movimientos': listado_movimientos,
            })
            return render(request, 'liquidacionbaja/filtro_liq_definitiva.html', context)
    else:
        return render(request, 'liquidacionbaja/filtro_liq_definitiva.html',
                      {'form': LiquidacionDefinitivaForm(), 'vista': vista})


@login_required
def confirmar_liquidaciones(request):
    context = {}
    vista = 'confirmar_liquidaciones'

    tipos_estado = ['Inicio', 'Pendiente', 'Normal']
    estados_pendientes = State.objects.filter(stateType__name__in=tipos_estado)
    #liquidaciones_list = Liquidacion.objects.filter(tipo__nombre='Mensual', mes__numero=datetime.datetime.now().month,
    #                                                mes__year=datetime.datetime.now().year,
    #                                                estado_actual__in=estados_pendientes)
    liquidaciones_list = Liquidacion.objects.filter(tipo__nombre='Mensual',
                                                    estado_actual__in=estados_pendientes)
    transicion_nuevo = Transition.objects.get(process__name='Liquidacion Mensual', currentState__name='Nuevo')
    for item in liquidaciones_list:
        if item.estado_actual.name == 'Nuevo':
            item.estado_actual = transicion_nuevo.nextState
            item.save()
        transicion = State.objects.get(process__name='Liquidacion Mensual', stateType__name='Completado')
        item.estado_actual = transicion
        item.save()
        # -------------------------------AGUINALDO----------------------------------------------#
        liq_haberes = Liquidacionhaber.objects.filter(liquidacion=item)
        for liq in liq_haberes:
            if liq.editable is True:
                liq.editable = False
                liq.save()
                detalles = DetalleLiquidacion.objects.filter(liquidacion_haber=liq)
                for detalleliquidacion in detalles:
                    if not detalleliquidacion.constante:
                        detalleliquidacion.monto = detalleliquidacion.calcular_monto()
                        detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                        detalleliquidacion.save()

                        if detalleliquidacion.variable.tipo == 'D':
                            detalleliquidacion.liquidacion_haber.monto_debito += detalleliquidacion.total_detalle
                        else:
                            detalleliquidacion.liquidacion_haber.monto_credito += detalleliquidacion.total_detalle
                        detalleliquidacion.liquidacion_haber.save()
                        detalleliquidacion.liquidacion_haber.subTotal = detalleliquidacion.liquidacion_haber.calcular_total()
                        detalleliquidacion.liquidacion_haber.save()

                for detalleliquidacion in detalles:
                    if detalleliquidacion.constante and detalleliquidacion.constante.tipo.porcentaje:
                        detalleliquidacion.monto = detalleliquidacion.calcular_monto_constante()
                        detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                        detalleliquidacion.save()

                liq.monto_credito = liq.suma_detalles_credito()
                liq.monto_debito = liq.suma_detalles_debito()
                liq.save()
                liq.subTotal = liq.calcular_total()
                liq.save()

                liq.liquidacion.total_credito = liq.liquidacion.calculo_total_credito()
                liq.liquidacion.total_debito = liq.liquidacion.calculo_total_debito()
                liq.liquidacion.total_liquidacion = liq.liquidacion.calcular_total_liquidacion()
                liq.liquidacion.save()

                # -------------------------------AGUINALDO----------------------------------------------#
                try:
                    aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                      anho=datetime.datetime.now().year)
                    nuevo_aguinaldo = aguinaldo
                    nuevo_aguinaldo.save()
                except Aguinaldo.DoesNotExist:
                    aguinaldo = None
                if liq.liquidacion.mes.numero == 1:
                    if aguinaldo == None:
                        nuevo_aguinaldo = Aguinaldo(
                            anho=datetime.datetime.today().year,
                            movimiento=liq.haber.movimiento
                        )
                        nuevo_aguinaldo.save()
                    nuevo_aguinaldo.cantidad_meses += 1
                    nuevo_aguinaldo.acumulado += nuevo_aguinaldo.calculo_acumulado(liq.pk)
                    nuevo_aguinaldo.total = nuevo_aguinaldo.calculo_total()
                    nuevo_aguinaldo.save()
                else:
                    if aguinaldo is not None:
                        aguinaldo.cantidad_meses += 1
                        aguinaldo.save()
                        aguinaldo.acumulado += aguinaldo.calculo_acumulado(liq.pk)
                        aguinaldo.total = aguinaldo.calculo_total()
                        aguinaldo.save()

                if liq.haber.movimiento.fechafin:
                    fin_fecha = date(liq.haber.movimiento.fechafin.year, liq.haber.movimiento.fechafin.month,
                                     liq.haber.movimiento.fechafin.day)
                    fin_hora = time(23, 59)
                    fechafin = datetime.datetime.combine(fin_fecha, fin_hora)
                    fin_periodo = liq.liquidacion.fin_periodo + timedelta(days=1)
                    if ((fin_periodo.replace(tzinfo=None)) >= fechafin.replace(
                            tzinfo=None) >= liq.liquidacion.inicio_periodo.replace(tzinfo=None)):
                        estado_inactivo = State.objects.get(process__name='Alta de Movimiento',
                                                            stateType__name='Caducado')
                        liq.haber.movimiento.estado = estado_inactivo
                        liq.haber.movimiento.save()
                        liq.haber.estado = liq.haber.movimiento.estado
                        liq.haber.save()
    # -------------------------------VACACIONES---------------------------------------------#
                vacacion_periodo = Vacaciones.objects.filter(
                    movimiento__funcionario=liq.liquidacion.funcionario).order_by('-inicio')

                if vacacion_periodo.count() > 0:
                    f = ~Q(movimiento__motivo__nombre='Contrato') \
                        & Q(tieneVacaciones=True) \
                        & Q(funcionario=liq.liquidacion.funcionario)

                    lista_movimientos = Movimiento.objects.filter(f).order_by('fechainicio')

                    if lista_movimientos.count() > 0:
                        primera_fecha = lista_movimientos.first().fechainicio
                        past_year = datetime.datetime.today().year - 1
                        f = date(past_year, primera_fecha.month, primera_fecha.day)
                        h = time(23, 59)
                        fechainicio = datetime.datetime.combine(f, h)

                        if (primera_fecha.month == liq.liquidacion.mes.numero) and (primera_fecha.year != liq.liquidacion.mes.year):
                            nueva_vacacion = Vacaciones(
                                anho=datetime.datetime.today().year,
                                inicio=fechainicio,
                                movimiento=lista_movimientos.first()
                            )
                            nueva_vacacion.save()

                    newest = vacacion_periodo.first()
                    newest.diasobtenidos = newest.calculo_diasobtenidos()
                    newest.dias_restantes = newest.calculo_diasrestantes()
                    newest.save()
                    if liq.liquidacion.vacaciones_usadas > 0:
                        vacaciones_funcionario = Vacaciones.objects.filter(movimiento__funcionario=liq.liquidacion.funcionario,
                                                                           dias_restantes__gt=0).order_by('inicio')[:2]
                        first = vacaciones_funcionario.first()
                        if first.dias_restantes > liq.liquidacion.vacaciones_usadas:
                            first.diasusados += liq.liquidacion.vacaciones_usadas
                            first.save()
                            first.dias_restantes = first.calculo_diasrestantes()
                            first.save()
                            vacacion_liquidacion = Vacacionesusadas(
                                diasusados=liq.liquidacion.vacaciones_usadas,
                                vacaciones=first,
                                mes=liq.liquidacion.mes
                            )
                            vacacion_liquidacion.save()
                        else:
                            if vacaciones_funcionario.count() > 1:
                                first = vacaciones_funcionario[0]
                                second = vacaciones_funcionario[1]
                                aux1 = liq.liquidacion.vacaciones_usadas
                                first.diasusados += first.dias_restantes
                                first.save()
                                vacacion_liquidacion = Vacacionesusadas(
                                    diasusados=first.dias_restantes,
                                    vacaciones=first,
                                    mes=liq.liquidacion.mes
                                )
                                vacacion_liquidacion.save()
                                aux2 = aux1 - first.dias_restantes
                                first.dias_restantes = first.calculo_diasrestantes()
                                first.save()
                                second.diasusados += aux2
                                second.save()
                                vacacion_liquidacion2 = Vacacionesusadas(
                                    diasusados=aux2,
                                    vacaciones=second,
                                    mes=liq.liquidacion.mes
                                )
                                vacacion_liquidacion2.save()
                                second.dias_restantes = second.calculo_diasrestantes()
                                second.save()

    return render(request, 'liquidacionmensual/liquidaciones_periodo.html', context)


@login_required
def confirmadas_periodo(request):
    context = {}
    vista = 'confirmadas_periodo'
    if request.method == 'GET':
        #liquidaciones_confirmadas = Liquidacion.objects.filter(tipo__nombre='Mensual',
        #                                                       mes__numero=datetime.datetime.now().month,
        #                                                       mes__year=datetime.datetime.now().year,
        #                                                       estado_actual__name='Confirmado')
        liquidaciones_confirmadas = Liquidacion.objects.filter(tipo__nombre='Mensual',
                                                               estado_actual__name='Confirmado')
        liquidacion_table = LiquidacionMensualTable(liquidaciones_confirmadas)
        context.update({
            'vista': vista,
            'lista': liquidaciones_confirmadas,
            'liquidacion_table': liquidacion_table
        })
    return render(request, 'liquidacionmensual/liquidaciones_periodo.html', context)


@login_required
def liquidaciones_periodo(request):
    context = {}
    vista = 'liquidaciones_periodo'
    tipos_estado = ['Inicio','Pendiente','Normal']
    estados_pendientes = State.objects.filter(stateType__name__in=tipos_estado)
    #liquidaciones_list = Liquidacion.objects.filter(tipo__nombre = 'Mensual', mes__numero = datetime.datetime.now().month,
    #                                                mes__year = datetime.datetime.now().year, estado_actual__in=estados_pendientes)
    liquidaciones_list = Liquidacion.objects.filter(tipo__nombre='Mensual', estado_actual__in=estados_pendientes)
    liquidacion_table = LiquidacionMensualTable(liquidaciones_list)
    context.update({
        'vista': vista,
        'lista': liquidaciones_list,
        'liquidacion_table' : liquidacion_table,
    })

    return render(request, 'liquidacionmensual/liquidaciones_periodo.html', context)


@login_required
def liq_pendientes_filtro(request):
    context = {}
    if request.method == 'POST':
        form = LiqPendientesForm(request.POST)
        if form.is_valid():
            #ToDo ver forma de traer los meses con su año
            cedula = form.cleaned_data['funcionario']
            funcionario = Funcionario.objects.get(cedula=cedula)
            imes = form.cleaned_data['mes']
            lista = Liquidacion.objects.filter(mes__numero=imes, funcionario__cedula=cedula,
                                               estado_actual__stateType__name='Pendiente')

            return redirect(reverse('liquidacion:liq_funcionarios_list', args=[funcionario.pk, imes]))
    else:
        form = LiqPendientesForm()
    return render(request, 'liquidacionmensual/liq_pendientes_filtro.html', {'form': form})


@login_required
def liq_funcionarios_list(request, funcionario, mes):
    tipos = ['Inicio','Pendiente']
    ifuncionario = Funcionario.objects.get(pk=funcionario)
    imes = Mes.objects.get(numero=mes)
    lista = Liquidacion.objects.filter(mes__numero=imes.numero, funcionario=ifuncionario,
                                       estado_actual__stateType__name__in=tipos)
    return render(request, 'liquidacionmensual/liqfuncionario_list.html', {'lista': lista,
                                                                       'funcionario': ifuncionario,
                                                                       'mes': imes})


@login_required
def vacaciones_form(request, idvacaciones):
    vacaciones = Vacaciones.objects.filter(movimiento__funcionario__idFuncionario = 2, dias_restantes__gt = 0)\
        .order_by('-inicio')
    context = {}
    pago = None
    if request.POST:
        vacacionesusadas = Vacacionesusadas(
            vacaciones = vacaciones,
            #vacaciones =
        )
        form = VacacionesusadasForm(request.POST, instance=vacacionesusadas)
        if form.is_valid():
            vacacionesusadas = form.save()
            return redirect(reverse('liquidacion:nuevo_pago', args=[pago.movimiento.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            return render(request, 'vacaciones/vacaciones_form.html', context)
    else:
        if idvacaciones:
            vacacionesusadas = Vacacionesusadas.objects.get(pk=idvacaciones)
            form = VacacionesusadasForm(request.POST, instance=vacacionesusadas)
            context.update({
                'vacacionesusadas': vacacionesusadas,
                'form': form
            })
        else:
            form = VacacionesusadasForm()
            context.update({
                'form': form,
            })
    return render(request, 'vacaciones/vacaciones_form.html', context)


@login_required()
@require_GET
def consulta_vacaciones(request):
    vista = 'consulta_vacaciones'

    if request.GET.get('q'):
        form = VacacionesFuncionarioForm(request.GET)

        if not form.has_changed():
            sin_datos = 'Ingrese todos los datos solicitados'
            return render(request, 'vacaciones/consulta_vacaciones.html',
                          {'form': VacacionesFuncionarioForm(initial=request.GET),
                           'sin_datos': sin_datos, 'vista': vista})
        if form.is_valid():
            context = {}
            funcionario = form.cleaned_data['funcionario']
            context.update({
                'funcionario': funcionario,
            })
            listado_vacaciones = Vacaciones.objects.filter(movimiento__funcionario__cedula=funcionario)

            context.update({
                'form': VacacionesFuncionarioForm(initial=request.GET),
                'listado_vacaciones': listado_vacaciones,
            })
            return render(request, 'vacaciones/consulta_vacaciones.html', context)
    else:
        return render(request, 'vacaciones/consulta_vacaciones.html',
                      {'form': VacacionesFuncionarioForm(), 'vista': vista})


@login_required()
def vista_detalleliquidacion(request, idliquidacionhaber=None, iddetalleliq=None):
    context = {}
    liquidacionhaber = Liquidacionhaber.objects.get(pk=idliquidacionhaber)
    if request.method == "POST":
        if iddetalleliq:
            detalleliquidacion = DetalleLiquidacion.objects.get(pk=iddetalleliq)
            form = DetalleLiquidacionForm(request.POST, instance=detalleliquidacion)
            context.update({
                'detalleliquidacion': detalleliquidacion
            })
        else:
            form = DetalleLiquidacionForm(request.POST)
        if form.is_valid():
            try:
                detalleliquidacion = form.save()
            except IntegrityError:
                messages.error(request, "Ya existe un detalle con la misma descripcion")
                return redirect(reverse('liquidacion:editar_liquidacionhaber', args=[liquidacionhaber.pk]))

            return redirect(reverse('liquidacion:editar_liquidacionhaber', args=[detalleliquidacion.liquidacion_haber.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
            messages.error(request, "Ya existe un detalle con la misma descripcion")
            return redirect(reverse('liquidacion:editar_liquidacionhaber', args=[liquidacionhaber.pk]))
    else:
        if iddetalleliq:
            detalleliquidacion = DetalleLiquidacion.objects.get(pk=iddetalleliq)
            form = DetalleLiquidacionForm(request.POST, instance=detalleliquidacion)
            context.update({
                'detalleliquidacion': detalleliquidacion
            })
        else:
            # TODO Definir valores iniciales
            form = DetalleLiquidacionForm(initial={
                'liquidacion_haber' : liquidacionhaber,
            })
        context.update({
            'liquidacion_haber': liquidacionhaber,
            'form': form
        })
    return render(request, 'liquidacionmensual/detalleliquidacion_form.html', context)


@login_required
def delete_detalleliquidacion(request, pk):
    detalleliquidacion = get_object_or_404(DetalleLiquidacion, pk=pk)
    tipo = detalleliquidacion.variable.tipo
    monto_detalle = detalleliquidacion.total_detalle
    liquidacion_haber = Liquidacionhaber.objects.get(pk=detalleliquidacion.liquidacion_haber.pk)
    detalleliquidacion.delete()
    if tipo == 'D':
        liquidacion_haber.monto_debito -= monto_detalle
    else:
        liquidacion_haber.monto_credito -= monto_detalle
    liquidacion_haber.save()
    liquidacion_haber.subTotal = liquidacion_haber.calcular_total()
    liquidacion_haber.save()
    liquidacion_haber.liquidacion.total_credito = liquidacion_haber.liquidacion.calculo_total_credito()
    liquidacion_haber.liquidacion.total_debito = liquidacion_haber.liquidacion.calculo_total_debito()
    liquidacion_haber.liquidacion.save()
    liquidacion_haber.liquidacion.total_liquidacion = liquidacion_haber.liquidacion.calcular_total_liquidacion()
    liquidacion_haber.liquidacion.save()
    return redirect(reverse('liquidacion:editar_liquidacionhaber', args=[liquidacion_haber.pk]))


@login_required
def vista_liq_mensual(request, idliquidacion):
    context = {}
    advertencia = liquidacion= None
    if request.method == 'POST':
        if idliquidacion:
            liquidacion = get_object_or_404(Liquidacion, pk=idliquidacion)
        form = LiqMensualForm(request.POST, instance=liquidacion)
        if form.is_valid():
            liquidacion = form.save()
            proceso = liquidacion.estado_actual.process
            estado_actual = liquidacion.estado_actual

            if request.POST.get('boton', '') == 'Descartado':
                transicion = Transition.objects.get(process=proceso, currentState=estado_actual, nextState__stateType__name='Cancelado')
                liquidacion.estado_actual = transicion.nextState
                liquidacion.save()
            else:
                if request.POST.get('boton', '')  == 'Confirmado':
                    cantidad_vacaciones = Vacaciones.objects.filter(
                        movimiento__funcionario=liquidacion.funcionario, movimiento__estado__name='Activo')\
                        .aggregate(dias_acumulados=Sum('dias_restantes'))

                    if cantidad_vacaciones['dias_acumulados'] < liquidacion.vacaciones_usadas :
                        messages.error(request, "No posee suficientes dias de vacaciones")
                        return redirect(reverse('liquidacion:editar_liquidacion', args=[liquidacion.pk]))
                    else:
                        transicion = Transition.objects.get(process=proceso, currentState=estado_actual,
                                                            nextState__stateType__name='Completado')
                        liquidacion.estado_actual = transicion.nextState
                        liquidacion.save()
                        # -------------------------------AGUINALDO----------------------------------------------#
                        liq_haberes = Liquidacionhaber.objects.filter(liquidacion = liquidacion)
                        if liquidacion.mes.numero == 1:
                            for liq in liq_haberes:
                                try:
                                    aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                                      anho=datetime.datetime.now().year)
                                    nuevo_aguinaldo = aguinaldo
                                    nuevo_aguinaldo.save()
                                except Aguinaldo.DoesNotExist:
                                    aguinaldo = None
                                if aguinaldo == None:
                                    nuevo_aguinaldo = Aguinaldo(
                                        anho = datetime.datetime.today().year,
                                        movimiento = liq.haber.movimiento
                                    )
                                    nuevo_aguinaldo.save()
                                nuevo_aguinaldo.cantidad_meses += 1
                                nuevo_aguinaldo.acumulado += nuevo_aguinaldo.calculo_acumulado(liq.pk)
                                nuevo_aguinaldo.total = nuevo_aguinaldo.calculo_total()
                                nuevo_aguinaldo.save()
                        else:
                            for liq in liq_haberes:
                                try:
                                    aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                                      anho=datetime.datetime.today().year)
                                except:
                                    aguinaldo = None
                                if aguinaldo is not None:
                                    aguinaldo.cantidad_meses += 1
                                    aguinaldo.save()
                                    aguinaldo.acumulado += aguinaldo.calculo_acumulado(liq.pk)
                                    aguinaldo.total = aguinaldo.calculo_total()
                                    aguinaldo.save()

                                if liq.haber.movimiento.fechafin :
                                    fin_fecha = date(liq.haber.movimiento.fechafin.year, liq.haber.movimiento.fechafin.month, liq.haber.movimiento.fechafin.day)
                                    fin_hora = time(23, 59)
                                    fechafin = datetime.datetime.combine(fin_fecha, fin_hora)
                                    fin_periodo = liquidacion.fin_periodo + timedelta(days=1)
                                    if ((fin_periodo.replace(tzinfo=None)) >= fechafin.replace(tzinfo=None) >= liquidacion.inicio_periodo.replace(tzinfo=None)) :
                                        estado_inactivo = State.objects.get(process__name='Alta de Movimiento', stateType__name='Caducado')
                                        liq.haber.movimiento.estado = estado_inactivo
                                        liq.haber.movimiento.save()
                                        liq.haber.estado = liq.haber.movimiento.estado
                                        liq.haber.save()

                        if liquidacion.mes.numero == 12:
                            for liq in liq_haberes:
                                try:
                                    aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                                      anho=datetime.datetime.today().year)
                                except:
                                    aguinaldo = None
                                if aguinaldo is not None:
                                    try:
                                        aguinaldo_padre = Aguinaldo.objects.get(
                                            movimiento=liq.haber.movimiento.movimiento_padre,
                                            anho=datetime.datetime.today().year)
                                    except:
                                        aguinaldo_padre = None
                                    if aguinaldo_padre is not None and aguinaldo_padre.total > 0:
                                        detalle_aguinaldo = DetalleLiquidacion.objects.get(constante__tipo__nombre='Aguinaldo',
                                                                                           liquidacion_haber=liq)
                                        detalle_aguinaldo.monto = aguinaldo.total
                                        detalle_aguinaldo.save()
                                        detalle_aguinaldo.total_detalle = detalle_aguinaldo.calculo_totaldetalle() + aguinaldo_padre.total
                                        detalle_aguinaldo.save()

                                liq.monto_credito = liq.suma_detalles_credito()
                                liq.save()
                                liq.subTotal = liq.calcular_total()
                                liq.save()

                            liquidacion.total_credito = liquidacion.calculo_total_credito()
                            liquidacion.total_debito = liquidacion.calculo_total_debito()
                            liquidacion.total_liquidacion = liquidacion.calcular_total_liquidacion()
                            liquidacion.save()

                        # -------------------------------VACACIONES---------------------------------------------#
                        vacacion_periodo = Vacaciones.objects.filter(
                            movimiento__funcionario=liquidacion.funcionario).order_by('-inicio')

                        if vacacion_periodo.count() > 0:
                            f = ~Q(movimiento__motivo__nombre = 'Contrato') \
                                & Q(tieneVacaciones = True) \
                                & Q(funcionario = liquidacion.funcionario)

                            lista_movimientos = Movimiento.objects.filter(f).order_by('fechainicio')

                            if lista_movimientos.count() > 0:
                                primera_fecha = lista_movimientos.first().fechainicio
                                past_year = datetime.datetime.today().year - 1
                                f = date(past_year, primera_fecha.month , primera_fecha.day)
                                h = time(23, 59)
                                fechainicio = datetime.datetime.combine(f, h)

                                if (primera_fecha.month == liquidacion.mes.numero) and (primera_fecha.year != liquidacion.mes.year):
                                    nueva_vacacion = Vacaciones(
                                        anho = datetime.datetime.today().year,
                                        inicio = fechainicio,
                                        movimiento = lista_movimientos.first()
                                    )
                                    nueva_vacacion.save()

                            newest = vacacion_periodo.first()
                            newest.diasobtenidos = newest.calculo_diasobtenidos()
                            newest.dias_restantes = newest.calculo_diasrestantes()
                            newest.save()
                            if liquidacion.vacaciones_usadas > 0 :
                                    vacaciones_funcionario = Vacaciones.objects.filter(movimiento__funcionario=liquidacion.funcionario,
                                                                                       dias_restantes__gt=0).order_by('inicio')[:2]
                                    first = vacaciones_funcionario.first()
                                    if first.dias_restantes > liquidacion.vacaciones_usadas:
                                        first.diasusados += liquidacion.vacaciones_usadas
                                        first.save()
                                        first.dias_restantes = first.calculo_diasrestantes()
                                        first.save()
                                        vacacion_liquidacion = Vacacionesusadas(
                                            diasusados = liquidacion.vacaciones_usadas,
                                            vacaciones = first,
                                            mes = liquidacion.mes
                                        )
                                        vacacion_liquidacion.save()
                                    else:
                                        if vacaciones_funcionario.count() > 1:
                                            first =  vacaciones_funcionario[0]
                                            second =  vacaciones_funcionario[1]
                                            aux1 = liquidacion.vacaciones_usadas
                                            first.diasusados += first.dias_restantes
                                            first.save()
                                            vacacion_liquidacion = Vacacionesusadas(
                                                diasusados= first.dias_restantes,
                                                vacaciones=first,
                                                mes=liquidacion.mes
                                            )
                                            vacacion_liquidacion.save()
                                            aux2 = aux1 - first.dias_restantes
                                            first.dias_restantes = first.calculo_diasrestantes()
                                            first.save()
                                            second.diasusados += aux2
                                            second.save()
                                            vacacion_liquidacion2 = Vacacionesusadas(
                                                diasusados = aux2,
                                                vacaciones = second,
                                                mes = liquidacion.mes
                                            )
                                            vacacion_liquidacion2.save()
                                            second.dias_restantes = second.calculo_diasrestantes()
                                            second.save()
                else:
                    if request.POST.get('boton', '') == 'Borrador':
                        transicion = Transition.objects.get(process=proceso, currentState=estado_actual, nextState__stateType__name='Pendiente')
                        liquidacion.estado_actual = transicion.nextState
                        liquidacion.save()
                        return redirect(reverse('liquidacion:index'))
            if request.POST.get('boton', '') == 'Definitiva':
                transicion = Transition.objects.get(process=proceso, currentState=estado_actual,
                                                   nextState__stateType__name='Completado')
                liquidacion.estado_actual = transicion.nextState
                liquidacion.save()

                liq = Liquidacionhaber.objects.get(liquidacion=liquidacion)

                fin_fecha = liquidacion.fin_periodo
                estado_inactivo = State.objects.get(process__name='Alta de Movimiento',
                                                    stateType__name='Caducado')
                liq.haber.movimiento.estado = estado_inactivo
                liq.haber.movimiento.fechafin = fin_fecha
                liq.haber.movimiento.save()
                liq.haber.estado = liq.haber.movimiento.estado
                liq.haber.save()

            #return redirect(reverse('liquidacion:index'))
            return redirect(reverse('liquidacion:editar_liquidacion', args=[liquidacion.pk]))
        else:
            # TODO Implementar sistema de errores
            context.update({
                'errors': form.errors,
                'form': form
            })
        return render(request, 'liquidacionmensual/liqmensual_form.html', context)
    else:
        if idliquidacion:
            liquidacion = get_object_or_404(Liquidacion, pk=idliquidacion)
            if liquidacion.estado_actual.stateType.name == 'Pendiente' or liquidacion.estado_actual.stateType.name == 'Inicio':
                transicion = Transition.objects.get(process=liquidacion.estado_actual.process, currentState=liquidacion.estado_actual)
                liquidacion.estado_actual = transicion.nextState
                liquidacion.save()
            if liquidacion.tipo.nombre == 'Mensual':
                haberes = Haber.objects.filter(movimiento__funcionario=liquidacion.funcionario)
                liq_haberes = Liquidacionhaber.objects.filter(liquidacion=liquidacion).order_by('pk')
                movimientos = Movimiento.objects.filter(pk__in = Subquery(liq_haberes.values('haber__movimiento__idmovimiento')))
                constantes = Constante.objects.filter(movimiento__pk__in=Subquery(movimientos.values('pk')))
                detalles = DetalleLiquidacion.objects.filter(liquidacion_haber__in=liq_haberes)
                form = LiqMensualForm(instance=liquidacion)
                vacaciones_activas = Vacaciones.objects.filter(movimiento__funcionario=liquidacion.funcionario,
                                                           dias_restantes__gt = 0)
                if vacaciones_activas.count() > 0 :
                    tieneVacaciones = True
                    context.update({
                        'tieneVacaciones': tieneVacaciones,
                    })
                context.update({
                    'form': form ,
                    'liquidacion': liquidacion,
                    'liq_haberes': liq_haberes,
                    'constantes': constantes,
                    'detalles': detalles,
                })
                try:
                    transition = Transition.objects.get(process=liquidacion.estado_actual.process, currentState=liquidacion.estado_actual)
                except MultipleObjectsReturned:
                    advertencia = 'Seleccione una accion para continuar'
                    context.update({
                        'advertencia': advertencia,
                    })
            else:
                liq_haber = Liquidacionhaber.objects.filter(liquidacion=liquidacion)
                movimientos = Movimiento.objects.filter(
                    pk__in=Subquery(liq_haber.values('haber__movimiento__idmovimiento')))
                constantes = Constante.objects.filter(movimiento__pk__in=Subquery(movimientos.values('pk')))
                detalles = DetalleLiquidacion.objects.filter(liquidacion_haber__in=liq_haber)
                form = LiqMensualForm(instance=liquidacion)
                vacaciones_activas = Vacaciones.objects.filter(movimiento__funcionario=liquidacion.funcionario,
                                                               dias_restantes__gt=0)
                context.update({
                    'liquidacion': liquidacion,
                    'liq_haberes': liq_haber,
                    'form': form,
                    'constantes': constantes,
                    'detalles': detalles,
                })
    return render(request, 'liquidacionmensual/liqmensual_form.html', context)


@login_required
def parametros_liq_mensual(request):
    context = {}
    if request.method == 'POST':
        form = PreLiqMensualForm(request.POST)
        if form.is_valid():
            depto = form.cleaned_data['departamento']
            fechafin = form.cleaned_data['hasta']
            fechainicio = form.cleaned_data['desde']
            try:
                mes = Mes.objects.get(numero=fechafin.month, year=fechafin.year)
                print(mes)
            except Mes.DoesNotExist:
                mes = None
                messages.warning(request, "El mes correspondiente al periodo aun no fue creado, favor contacte con el administrador del sistema")
                return redirect(reverse('liquidacion:parametros_liq_mensual'))
            if mes is not None:
                funcionarios = Movimiento.objects\
                    .filter(division__departamento=depto, estado__name='Activo')\
                    .values('funcionario__idFuncionario', 'motivo__nombre', 'idmovimiento').distinct('funcionario__idFuncionario')
                print(funcionarios)
                if funcionarios.count() > 0 :
                    for mov in funcionarios:
                        pago = None
                        existe_pago = True
                        try:
                            liquidacion = Liquidacion.objects.get(funcionario__idFuncionario=mov['funcionario__idFuncionario'],
                                                                  mes=mes, tipo__nombre='Mensual')
                        except Liquidacion.DoesNotExist:
                            liquidacion = None
                        if liquidacion == None:
                            tipo = LiquidacionType.objects.get(nombre='Mensual')
                            proceso = Process.objects.get(name='Liquidacion Mensual')
                            initial_state_type = StateType.objects.get(name='Inicio')
                            initial_state = State.objects.get(process=proceso, stateType=initial_state_type)
                            funcionario = Funcionario.objects.get(pk = mov['funcionario__idFuncionario'])
                            print(mov['idmovimiento'])
                            if mov['motivo__nombre'] == 'Contrato':
                                if Pago.objects.filter(mes=mes, movimiento__pk=mov['idmovimiento']).exists():
                                    pago = Pago.objects.get(mes=mes, movimiento__pk=mov['idmovimiento'])
                                    existe_pago = True
                                else:
                                    pago = None
                                    existe_pago = False
                            if existe_pago is True:
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
                                    motivo = LiquidacionMotivo.objects.get(nombre='Mensual')
                                )
                                liquidacion.save()
                        if existe_pago is True:
                            haberes = Haber.objects.filter(movimiento__funcionario=liquidacion.funcionario,
                                                       movimiento__division__departamento__pk=depto, estado__name='Activo')
                            for haber in haberes:
                                if haber.movimiento.motivo.nombre == 'Contrato':
                                    #liq_haber = None
                                    liq_haber = Liquidacionhaber(
                                        haber=haber,
                                        liquidacion=liquidacion,
                                        pago=pago,
                                    )
                                else:
                                    liq_haber = Liquidacionhaber(
                                        haber=haber,
                                        liquidacion=liquidacion,
                                    )
                                liq_haber.monto_debito = liq_haber.suma_detalles_debito()
                                liq_haber.monto_credito = liq_haber.suma_detalles_credito()
                                liq_haber.subTotal = round(liq_haber.monto_credito - liq_haber.monto_debito, 0)
                                try:
                                    liq_haber.save()
                                except IntegrityError:
                                    messages.error(request, "Ya se ha creado las liquidaciones salariales de este departamento "
                                                            "para el mes")
                                    return redirect(reverse('liquidacion:parametros_liq_mensual'))

                                if liq_haber.haber.movimiento.motivo.nombre == 'Contrato':
                                    if liq_haber.pago:
                                        salario_mes = DetalleLiquidacion(
                                            cantidad=1,
                                            monto=Decimal(liq_haber.pago.monto),
                                            total_detalle=Decimal(liq_haber.pago.monto),
                                            parametro=Parametro.objects.get(descripcion='Monto'),
                                            variable=Variable.objects.get(motivo='Asignacion Salarial'),
                                            liquidacion_haber=liq_haber,
                                            constante= Constante.objects.get(tipo__nombre='Asignacion Salarial', movimiento= liq_haber.haber.movimiento)
                                        )
                                else:
                                    salario_mes = DetalleLiquidacion(
                                        cantidad=1,
                                        monto=liq_haber.haber.movimiento.categoria_salarial.asignacion,
                                        total_detalle=liq_haber.haber.movimiento.categoria_salarial.asignacion,
                                        parametro=Parametro.objects.get(descripcion='Monto'),
                                        variable=Variable.objects.get(motivo='Asignacion Salarial'),
                                        liquidacion_haber=liq_haber,
                                        constante=Constante.objects.get(tipo__nombre='Asignacion Salarial', movimiento= liq_haber.haber.movimiento)
                                    )
                                salario_mes.save()
                                salario_mes.liquidacion_haber.monto_credito = salario_mes.liquidacion_haber.suma_detalles_credito()
                                salario_mes.liquidacion_haber.monto_debito = salario_mes.liquidacion_haber.suma_detalles_debito()
                                salario_mes.liquidacion_haber.save()
                                salario_mes.liquidacion_haber.subTotal = salario_mes.liquidacion_haber.calcular_total()
                                salario_mes.liquidacion_haber.save()

                                salario_mes.liquidacion_haber.liquidacion.total_credito = salario_mes.liquidacion_haber.liquidacion.calculo_total_credito()
                                salario_mes.liquidacion_haber.liquidacion.total_debito = salario_mes.liquidacion_haber.liquidacion.calculo_total_debito()
                                salario_mes.liquidacion_haber.liquidacion.total_liquidacion = salario_mes.liquidacion_haber.liquidacion.calcular_total_liquidacion()
                                salario_mes.liquidacion_haber.liquidacion.save()

                                if liquidacion.mes.numero == 12:
                                    aguinaldo_anho = DetalleLiquidacion(
                                        cantidad=1,
                                        monto=0,
                                        parametro=Parametro.objects.get(descripcion='Monto'),
                                        variable=Variable.objects.get(motivo='Aguinaldo'),
                                        liquidacion_haber=liq_haber,
                                        constante=Constante.objects.get(tipo__nombre='Aguinaldo', movimiento= liq_haber.haber.movimiento)
                                    )
                                    aguinaldo_anho.save()

                                constantes_movimiento = Constante.objects.filter(movimiento=liq_haber.haber.movimiento)
                                for constante in constantes_movimiento:
                                    if constante.tipo.nombre != 'Asignacion Salarial' and constante.tipo.nombre != 'Aguinaldo':
                                        if constante.tipo.porcentaje:
                                            detalleliquidacion = DetalleLiquidacion(
                                                cantidad = 1,
                                                monto = 0,
                                                parametro = Parametro.objects.get(descripcion='Monto'),
                                                variable = Variable.objects.get(motivo=constante.tipo.nombre),
                                                liquidacion_haber = liq_haber,
                                                constante=constante,
                                            )
                                        else:
                                            detalleliquidacion = DetalleLiquidacion(
                                                cantidad=1,
                                                monto=constante.monto,
                                                parametro=Parametro.objects.get(descripcion='Monto'),
                                                variable=Variable.objects.get(motivo=constante.tipo.nombre),
                                                liquidacion_haber=liq_haber,
                                                constante=constante,
                                            )
                                        detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                                        detalleliquidacion.save()
                                        if detalleliquidacion.variable.tipo == 'D':
                                            detalleliquidacion.liquidacion_haber.monto_debito = detalleliquidacion.liquidacion_haber.suma_detalles_debito()
                                        else:
                                            detalleliquidacion.liquidacion_haber.monto_credito = detalleliquidacion.liquidacion_haber.suma_detalles_credito()
                                        detalleliquidacion.liquidacion_haber.save()
                                        detalleliquidacion.liquidacion_haber.subTotal = detalleliquidacion.liquidacion_haber.calcular_total()
                                        detalleliquidacion.liquidacion_haber.save()
                                        detalleliquidacion.liquidacion_haber.liquidacion.total_credito = detalleliquidacion.liquidacion_haber.liquidacion.calculo_total_credito()
                                        detalleliquidacion.liquidacion_haber.liquidacion.total_debito = detalleliquidacion.liquidacion_haber.liquidacion.calculo_total_debito()
                                        detalleliquidacion.liquidacion_haber.liquidacion.total_liquidacion = detalleliquidacion.liquidacion_haber.liquidacion.calcular_total_liquidacion()
                                        detalleliquidacion.liquidacion_haber.liquidacion.save()

                    #    else:
                    #        messages.warning(request,
                    #                         "Ya se ha creado una liquidacion salarial al funcionario para este periodo")
                    #        return redirect(reverse('liquidacion:parametros_liq_mensual'))
                    context.update({
                        'lista': True,
                        'form': form,
                    })
                    return redirect(reverse('liquidacion:liq_pendientes_list', args=[depto, mes.numero, mes.year]))
                else:
                    messages.info(request, "No existe funcionarios activos en este departamento")
                    return redirect(reverse('liquidacion:parametros_liq_mensual'))

        else:
            context.update({
                'errors': form.errors,
                'form': form
            })
    else:
        form = PreLiqMensualForm()
    return render(request, 'liquidacionmensual/liqmensual_filtro.html', {'form': form})


@login_required
def liq_pendientes_list(request, iddpto, mes, anho):
    context = {}
    imes = Mes.objects.get(numero=mes, year=anho)
    estado = State.objects.filter(Q(stateType__name='Inicio') | Q(stateType__name='Pendiente')
                                  | Q(stateType__name='Normal') & Q(process__name='Liquidacion Mensual'))
    departamento = Departamento.objects.get(pk=iddpto)
    movimientos = Movimiento.objects.filter(division__departamento=departamento, estado__name='Activo')

    liquidaciones = Liquidacion.objects.filter(mes=imes, tipo__nombre='Mensual', estado_actual__in= estado)
    liquidacion_haberes = Liquidacionhaber.objects.filter(liquidacion__in = liquidaciones,
                                                          editable=True, haber__movimiento__in=movimientos)
    return render(request, 'liquidacionmensual/liqmensual_list.html', {'lista': liquidacion_haberes,
                                                                       'dpto': departamento,
                                                                       'mes': imes })


@login_required
def vista_liquidacionhaber(request, idliquidacionhaber):
    context = {}
    advertencia = liq_haber= None
    if request.method == 'POST':
        if idliquidacionhaber:
            liq = get_object_or_404(Liquidacionhaber, pk=idliquidacionhaber)
            form = LiquidacionhaberForm(request.POST, instance=liq)
            if form.is_valid():
                liq.save()
                if request.POST.get('boton', '') == 'Finalizar':
                    liq.editable = False
                    liq.save()
                    if liq.liquidacion.mes.numero == 1:
                        aguinaldo = Aguinaldo(
                            anho=datetime.datetime.today().year,
                            movimiento=liq.haber.movimiento
                        )
                        aguinaldo.save()
                        aguinaldo.acumulado += aguinaldo.calculo_acumulado(liq.pk)
                        aguinaldo.save()
                        aguinaldo.total = aguinaldo.calculo_total()
                        aguinaldo.save()
                    else:
                        try:
                            aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                              anho=datetime.datetime.today().year)
                        except:
                            aguinaldo = None
                        if aguinaldo is not None:
                            aguinaldo = Aguinaldo.objects.get(movimiento=liq.haber.movimiento,
                                                              anho=datetime.datetime.today().year)
                            aguinaldo.save()
                            aguinaldo.cantidad_meses += 1
                            aguinaldo.acumulado += (liq.salario_proporcional / 12) * 1
                            aguinaldo.save()
                            aguinaldo.total = aguinaldo.calculo_total()
                            aguinaldo.save()

                    detalles = DetalleLiquidacion.objects.filter(liquidacion_haber=liq)
                    for detalleliquidacion in detalles:
                        if not detalleliquidacion.constante:
                            #print('Nombre del detalle: ', detalleliquidacion.variable.motivo)
                            detalleliquidacion.monto = detalleliquidacion.calcular_monto()
                            #print('Monto del detalle: ', detalleliquidacion.monto)
                            detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                            detalleliquidacion.save()

                            if detalleliquidacion.variable.tipo == 'D':
                                detalleliquidacion.liquidacion_haber.monto_debito += detalleliquidacion.total_detalle
                            else:
                                detalleliquidacion.liquidacion_haber.monto_credito += detalleliquidacion.total_detalle
                            detalleliquidacion.liquidacion_haber.save()
                            detalleliquidacion.liquidacion_haber.subTotal = detalleliquidacion.liquidacion_haber.calcular_total()
                            detalleliquidacion.liquidacion_haber.save()

                    for detalleliquidacion in detalles:
                        if detalleliquidacion.constante and detalleliquidacion.constante.tipo.porcentaje:
                            #print('Nombre del detalle: ', detalleliquidacion.variable.motivo)
                            detalleliquidacion.monto = detalleliquidacion.calcular_monto_constante()
                            #print('Monto del detalle: ', detalleliquidacion.monto)
                            detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                            detalleliquidacion.save()
                        if detalleliquidacion.variable.motivo == 'Aguinaldo':
                            detalleliquidacion.monto = aguinaldo.calculo_total()
                            detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                            detalleliquidacion.save()

                    liq.monto_credito = liq.suma_detalles_credito()
                    liq.monto_debito = liq.suma_detalles_debito()
                    liq.save()
                    liq.subTotal = liq.calcular_total()
                    liq.save()

                    liq.liquidacion.total_credito = liq.liquidacion.calculo_total_credito()
                    liq.liquidacion.total_debito = liq.liquidacion.calculo_total_debito()
                    liq.liquidacion.total_liquidacion = liq.liquidacion.calcular_total_liquidacion()
                    liq.liquidacion.save()

                if request.POST.get('boton', '') == 'Guardar':
                    detalles = DetalleLiquidacion.objects.filter(liquidacion_haber=liq)
                    for detalleliquidacion in detalles:
                        if not detalleliquidacion.constante :
                            detalleliquidacion.monto = detalleliquidacion.calcular_monto()
                            detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                            detalleliquidacion.save()

                            if detalleliquidacion.variable.tipo == 'D':
                                detalleliquidacion.liquidacion_haber.monto_debito += detalleliquidacion.total_detalle
                            else:
                                detalleliquidacion.liquidacion_haber.monto_credito += detalleliquidacion.total_detalle
                            detalleliquidacion.liquidacion_haber.save()
                            detalleliquidacion.liquidacion_haber.subTotal = detalleliquidacion.liquidacion_haber.calcular_total()
                            detalleliquidacion.liquidacion_haber.save()

                    for detalleliquidacion in detalles :
                        if detalleliquidacion.constante and detalleliquidacion.constante.tipo.porcentaje:
                            detalleliquidacion.monto = detalleliquidacion.calcular_monto_constante()
                            detalleliquidacion.total_detalle = detalleliquidacion.calculo_totaldetalle()
                            detalleliquidacion.save()

                    liq.monto_credito = liq.suma_detalles_credito()
                    liq.monto_debito = liq.suma_detalles_debito()
                    liq.save()
                    liq.subTotal = liq.calcular_total()
                    liq.save()

                    liq.liquidacion.total_credito = liq.liquidacion.calculo_total_credito()
                    liq.liquidacion.total_debito = liq.liquidacion.calculo_total_debito()
                    liq.liquidacion.total_liquidacion = liq.liquidacion.calcular_total_liquidacion()
                    liq.liquidacion.save()

                return redirect(reverse('liquidacion:editar_liquidacion', args=[liq.liquidacion.pk]))
            else:
                context.update({
                    'errors': form.errors,
                    'form': form
                })
            #return redirect(reverse('liquidacion:editar_liquidacion', args=[liq.liquidacion.pk]))
            return render(request, 'liquidacionmensual/liquidacionhaber_form.html', context)
    else:
        if idliquidacionhaber :
            liq_haber = get_object_or_404(Liquidacionhaber, pk=idliquidacionhaber)
            constantes = Constante.objects.filter(movimiento=liq_haber.haber.movimiento)
            detalles_list = DetalleLiquidacion.objects.filter(liquidacion_haber=liq_haber)
            form = LiquidacionhaberForm(instance=liq_haber)
            if liq_haber.liquidacion.estado_actual.name == 'Nuevo':
                try:
                    transition = Transition.objects.get(process=liq_haber.liquidacion.estado_actual.process,
                                                        currentState=liq_haber.liquidacion.estado_actual)
                    liq_haber.liquidacion.estado_actual = transition.nextState
                    liq_haber.liquidacion.save()
                except MultipleObjectsReturned:
                    advertencia = 'Seleccione una accion para continuar'
                    context.update({
                        'advertencia': advertencia,
                    })
            context.update({
                'form': form ,
                'liq_haber': liq_haber,
                'constantes': constantes,
                'detalles_list': detalles_list,
            })
    return render(request, 'liquidacionmensual/liquidacionhaber_form.html', context)


@login_required
def success_page(request, idmovimiento):
    context = {}
    tipo = Movimiento.objects.get(pk=idmovimiento).motivo.nombre
    context.update({
        'idmovimiento': idmovimiento,
        'tipo' : tipo,
    })
    return render(request, 'success_page.html', context)


@login_required
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


@login_required
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
                if movimiento.motivo.nombre != 'Contrato':
                    if movimiento.movimiento_padre is None:
                        movimiento.familia = movimiento.pk
                    else:
                        movimiento.familia = movimiento.movimiento_padre.familia
                    movimiento.save()
                salario = Constante(
                    finito = False,
                    movimiento = movimiento,
                    tipo = ConstanteType.objects.get(nombre='Asignacion Salarial')
                )
                salario.save()
                #-------------------------------------------------------------------------#
                if movimiento.motivo.nombre != 'Contrato':
                    haber = None
                    if movimiento.movimiento_padre:
                        #----------------------------Haberes----------------------------------#
                        haber = Haber(
                            movimiento = movimiento,
                            estado = movimiento.estado
                        )
                        haber.save()
                        # ---------------------------Vacaciones-------------------------------#
                        try:
                            vacaciones_padre = Vacaciones.objects.filter(movimiento=movimiento_padre).order_by('-inicio').first()
                        except Vacaciones.DoesNotExist:
                            vacaciones_padre = None

                        if vacaciones_padre is not None:
                            vacaciones_padre.fin = movimiento.fechainicio - timedelta(days=1)
                            vacaciones_padre.save()
                        if movimiento.tieneVacaciones is True:
                            vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                            vacaciones.save()
                            vaca = Constante(
                                finito=False,
                                movimiento=movimiento,
                                tipo=ConstanteType.objects.get(nombre='Vacaciones')
                            )
                            vaca.save()
                        if movimiento.tieneAguinaldo is True:
                            aguinaldo = Aguinaldo(movimiento = movimiento)
                            aguinaldo.save()
                            agui = Constante(
                                finito=False,
                                movimiento=movimiento,
                                tipo=ConstanteType.objects.get(nombre='Aguinaldo')
                            )
                            agui.save()
                        movimiento.movimiento_padre.estado = State.objects.get(name='Inactivo', process=proceso)
                        movimiento.movimiento_padre.fechafin = movimiento.fechainicio - timedelta(days=1)
                        movimiento.movimiento_padre.save()
                        haber_padre = Haber.objects.get(movimiento=movimiento.movimiento_padre)
                        haber_padre.estado = movimiento.movimiento_padre.estado
                        haber_padre.save()
                    else:
                        haber = Haber(movimiento = movimiento, estado=movimiento.estado)
                        if movimiento.tieneAguinaldo is True:
                            aguinaldo = Aguinaldo(movimiento = movimiento)
                            aguinaldo.save()
                            agui = Constante(
                                finito=False,
                                movimiento=movimiento,
                                tipo=ConstanteType.objects.get(nombre='Aguinaldo')
                            )
                            agui.save()
                        if movimiento.tieneVacaciones is True:
                            vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                            vacaciones.save()
                            vaca = Constante(
                                finito=False,
                                movimiento=movimiento,
                                tipo=ConstanteType.objects.get(nombre='Vacaciones')
                            )
                            vaca.save()
                        haber.save()
                    return redirect(reverse('liquidacion:nueva_constante', args=[movimiento.pk]))
                else:
                    haber = Haber(movimiento=movimiento, estado=movimiento.estado)
                    haber.save()
                    if movimiento.formapago == 'M' and movimiento.tieneAguinaldo is True:
                        aguinaldo = Aguinaldo(movimiento=movimiento)
                        aguinaldo.save()
                    return redirect(reverse('liquidacion:nuevo_pago', args=[movimiento.pk]))
                #-------------------------------------------------------------------------#
            else:
                context.update({
                    'errors': form.errors,
                    'form': form,
                    'movimiento_padre': movimiento_padre,
                    'funcionario': funcionario,
                })
            return render(request, 'proceso/movimiento_form.html', context)
    else:
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
            try:
                documentos = DocumentoRespaldatorio.objects.get(movimiento=movimiento)
                context.update({
                    'documento': documentos,
                })
            except DocumentoRespaldatorio.DoesNotExist:
                documentos = None
            constantes = Constante.objects.filter(movimiento=movimiento)
            form = MovimientoForm(instance=movimiento)
            context.update({
                'movimiento': movimiento,
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

@login_required
def opciones_proceso(request):
    return render(request, 'proceso/opciones_proceso.html')

@login_required
def opciones_vacaciones(request):
    return render(request, 'vacaciones/opciones_vacaciones.html')

@login_required
def opciones_reportes(request):
    return render(request, 'reportes/opciones_reportes.html')

@login_required
def busqueda_funcionarios(request):
    choice = request.GET.get("q")
    queryset_list = Funcionario.objects.all()
    recibido = request.GET.get("q")
    if recibido:
        queryset_list = queryset_list.filter\
            (Q(nombres__icontains=recibido) | Q(apellidos__icontains=recibido) | Q(cedula__icontains=recibido))

    return render(request, 'proceso/filtro_funcionarios_movimiento.html', {'funcionarios': queryset_list})

@login_required
def busqueda_movimiento_funcionario(request):
    vista = 'busqueda_movimiento_funcionario'
    if request.GET.get('q'):
        form = LiquidacionDefinitivaForm(request.GET)
        if not form.has_changed():
            sin_datos = 'Ingrese todos los datos solicitados'
            return render(request, 'proceso/seleccion_movimiento_funcionario.html',
                          {'form': LiquidacionDefinitivaForm(initial=request.GET),
                           'sin_datos': sin_datos, 'vista': vista})
        if form.is_valid():
            context = {}
            funcionario = form.cleaned_data['funcionario']
            context.update({
                'funcionario': funcionario,
            })
            funcionarios = Movimiento.objects.filter(funcionario__cedula=funcionario, estado__name='Activo')

            context.update({
                'form': LiquidacionDefinitivaForm(initial=request.GET),
                'funcionarios': funcionarios,
            })
            return render(request, 'proceso/seleccion_movimiento_funcionario.html', context)
    else:
        return render(request, 'proceso/seleccion_movimiento_funcionario.html',
                      {'form': LiquidacionDefinitivaForm(), 'vista': vista})

@login_required
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

@login_required
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

@login_required
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

@login_required
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
            try:
                constante = form.save()
            except IntegrityError:
                messages.error(request, "Ya ha agregado una referencia con la misma descripcion")
                return redirect(reverse('liquidacion:nueva_constante', args=[constante.movimiento.pk]))

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

@login_required(login_url='/accounts/login/')
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
            try:
                pago = form.save()
            except IntegrityError:
                messages.error(request, "Ya ha agregado un pago para el mes")
                return redirect(reverse('liquidacion:nuevo_pago', args=[pago.movimiento.pk]))
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
def traer_variables(request):
    if request.is_ajax():
        var = Variable.objects.all()
        con = ConstanteType.objects.all()
        res = []
        for v in var:
            ok = False
            for c in con:
                if v.motivo == c.nombre :
                    ok = True
            if ok is False:
                var_json = {'id': v.pk, 'value': v.motivo}
                res.append(var_json)
        data = json.dumps(res)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@require_GET
def traer_constantes(request):
    if request.is_ajax():
        idmovimiento = request.GET['idmovimiento']
        movimiento = Movimiento.objects.get(pk=idmovimiento)
        tipos = ConstanteType.objects.all()
        con = Constante.objects.filter(movimiento=movimiento)
        res = []
        for t in tipos:
            ok = False
            for c in con:
                if t.nombre == c.tipo.nombre :
                    ok = True
            if ok is False:
                con_json = {'id': t.pk, 'value': t.nombre, 'value2' : Decimal(t.porcentaje)}
                print(con_json)
                res.append(con_json)
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
def traer_mes(request):
    if request.is_ajax():
        meses = Mes.objects.all()
        print(meses)
        res = []
        for mes in meses:
            mes_json = {'id': mes.numero, 'value': mes.nombre}
            res.append(mes_json)
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

            f = (Q(funcionario__cedula = cedula) | Q(funcionario__nombres = nombres) | Q(funcionario__apellidos=apellidos)) & Q(estado__name='Activo')

            movimientos = Movimiento.objects.filter(f)
            print(movimientos)

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
