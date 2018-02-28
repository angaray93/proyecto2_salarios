from django.apps import apps
from django.db.models import *
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from liquidacion.forms import *
from liquidacion.models import *


def index(request):
    return render(request, 'index.html')


def movimiento_vista(request, idmovimiento=None, idfuncionario=None):
    context = {}
    movimiento = None
    if request.POST:
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
        else:
            movimiento = Movimiento()
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
        if idmovimiento:
            movimiento = get_object_or_404(Movimiento, pk=idmovimiento)
            form = MovimientoForm(instance=movimiento)
            context.update({
                'movimiento': movimiento,
                'form': form
            })
        else:
            funcionario = Funcionario.objects.get(pk=idfuncionario)
            form = MovimientoForm(initial={
                'funcionario': funcionario,
            })
            context.update({
                'funcionario': funcionario,
                'form': form,
            })
        return render(request, 'proceso/movimiento_form.html', context)


def opciones_proceso(request):
    return render(request, 'proceso/opciones_proceso.html')


def busqueda_funcionarios(request):
    queryset_list = Funcionario.objects.all()
    recibido = request.GET.get("q")
    if recibido:
        queryset_list = queryset_list.filter\
            (Q(nombres__icontains=recibido) | Q(apellidos__icontains=recibido) | Q(cedula__icontains=recibido))

    return render(request, 'proceso/filtro_funcionarios_movimiento.html', {'funcionarios': queryset_list})
