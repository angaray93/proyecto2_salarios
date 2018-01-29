from django import forms
from django.contrib import admin
from liquidacion.forms import CategoriaSalarialForm
from liquidacion.models import *

class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'fechanacimiento', 'direccion', 'email', 'telefono', 'cantHijos')
    search_fields = ('cedula', 'nombres', 'apellidos')
    raw_id_fields = ('usuario',)
admin.site.register(Funcionario, FuncionarioAdmin)

class CategoriaSalarialAdmin(admin.ModelAdmin):
    form = CategoriaSalarialForm
    list_display = ('codigo', 'tipo', 'cargo', 'asignacion')
    search_fields = ('codigo', 'cargo')

#    raw_id_fields = ('usuario')

admin.site.register(CategoriaSalarial, CategoriaSalarialAdmin)


