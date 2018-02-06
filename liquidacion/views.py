from django.apps import apps
from django.db.models import *
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from liquidacion.forms import *
from liquidacion.models import *


def index(request):
    return render(request, 'index.html')

def lista_objetos(request, model_name):
    items = model_name.objects.all()
    return render(request, 'index.html', {'items': items})
    #return render(request, 'listado.html', {'books': books})


def categoriasalarial_list(request):
    categorias = CategoriaSalarial.objects.all()
    return render(request, 'categoriasalarial/categorias_list.html', {'categorias': categorias})


def vista_categoriasalarial(request):
    form = CategoriaSalarialForm()
    context = {'form': form}
    html_form = render_to_string('categoriasalarial/partial_categorias_create.html',
                                 context,
                                 request=request,
                                 )
    return JsonResponse({'html_form': html_form})