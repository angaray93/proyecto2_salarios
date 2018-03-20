from datetime import timedelta

from django.apps import apps
from django.db.models import *
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse
from liquidacion.forms import *
from liquidacion.models import *


import json


def index(request):
    return render(request, 'index.html')


def movimiento_vista(request, idmovimiento=None, idpadre=None, idfuncionario=None):
    context = {}
    movimiento = None
    if request.POST:
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
            form = MovimientoForm(request.POST, instance=movimiento)
            if form.is_valid():
                movimiento = form.save()
                return redirect(reverse('liquidacion:ver_movimiento', args=[movimiento.pk]))
            else:
                # TODO Implementar sistema de errores
                context.update({
                    'errors': form.errors,
                    'form': form
                })
                return render(request, 'proceso/movimiento_form.html', context)
        else:
            estado_default = State.objects.get(nombre='Activo')
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
                movimiento = Movimiento(
                    estado=estado_default,
                    movimiento_padre=movimiento_padre,
                    funcionario=funcionario
                )

            form = MovimientoForm(request.POST, instance=movimiento)
            if form.is_valid():
                movimiento = form.save()
                #-------------------------------------------------------------------------#
                haber = None
                if movimiento.movimiento_padre:
                    #----------------------------Haberes----------------------------------#
                    haber = Haber.objects.get(movimiento=movimiento.movimiento_padre)
                    haber.movimiento = movimiento
                    # ---------------------------Vacaciones-------------------------------#
                    vacaciones_padre = Vacaciones.objects.get(movimiento=movimiento_padre)
                    vacaciones_padre.fin = movimiento.fechainicio - timedelta(days=1)
                    vacaciones_padre.save()
                    if movimiento.tieneVacaciones is True:
                        vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                        vacaciones.save()
                        print(vacaciones)
                    if movimiento.tieneAguinaldo is True:
                        aguinaldo = Aguinaldo(movimiento = movimiento)
                        aguinaldo.save()
                    movimiento.movimiento_padre.estado = State.objects.get(nombre='Inactivo')
                    movimiento.movimiento_padre.fechafin = movimiento.fechainicio - timedelta(days=1)
                    #ToDo Dar de baja el haber del viejo movimiento y asignar el del nuevo en su lugar antes de que se guarde
                    movimiento.movimiento_padre.save()

                else:
                    haber = Haber(movimiento = movimiento)
                    if movimiento.tieneAguinaldo is True:
                        aguinaldo = Aguinaldo(movimiento = movimiento)
                        aguinaldo.save()
                    if movimiento.esPrimero is True and movimiento.tieneVacaciones is True:
                        vacaciones = Vacaciones(movimiento=movimiento, inicio=movimiento.fechainicio)
                        vacaciones.save()

                haber.save()

                #-------------------------------------------------------------------------#
                return redirect(reverse('liquidacion:ver_movimiento', args=[movimiento.pk]))
            else:
                # TODO Implementar sistema de errores
                context.update({
                    'errors': form.errors,
                    'form': form
                })
                return render(request, 'proceso/movimiento_form.html', context)
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
            else:
                movimiento_padre = None
                q = request.GET.get('term', '')
                funcionario = Funcionario.objects.get(pk=idfuncionario)
            estado_default = State.objects.get(nombre='Activo')

            form = MovimientoForm(initial={
                'funcionario': funcionario,
                'movimiento_padre': movimiento_padre,
                'estado': estado_default,
            })
            context.update({
                'movimiento_padre': movimiento_padre,
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
        movimientos = Movimiento.objects.filter(funcionario=q)
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
            return redirect(reverse('liquidacion:ver_movimiento', args=[documento.movimiento.pk]))
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
            return redirect(reverse('liquidacion:nueva_constante', args=[movimiento.pk]))
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