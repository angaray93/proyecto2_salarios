from django import forms
from django.contrib import admin
from liquidacion.forms import *
from liquidacion.models import *

#-----------Modelos del workflow-------------------#

admin.site.register(Process)
admin.site.register(DefaultProcess)
admin.site.register(StateType)
admin.site.register(State)
admin.site.register(ActionType)
admin.site.register(Action)
admin.site.register(Transition)

#--------------------------------------------------#

class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'fechanacimiento', 'direccion', 'email', 'telefono', 'cantHijos')
    search_fields = ('cedula', 'nombres', 'apellidos')
    raw_id_fields = ('usuario',)

admin.site.register(Funcionario, FuncionarioAdmin)


class CategoriaSalarialAdmin(admin.ModelAdmin):
    form = CategoriaSalarialForm
    list_display = ('codigo', 'tipo', 'cargo', 'asignacion')
    search_fields = ('codigo', 'cargo',)

admin.site.register(CategoriaSalarial, CategoriaSalarialAdmin)


class Objeto_De_GastoAdmin(admin.ModelAdmin):
    form = Objeto_De_GastoAdminForm
    list_display = ('concepto', 'numero',)
    search_fields = ('concepto', 'numero',)

admin.site.register(Objeto_De_Gasto, Objeto_De_GastoAdmin)


class DepartamentoAdmin(admin.ModelAdmin):
    form = DepartamentoForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(Departamento, DepartamentoAdmin)

class DivisionAdmin(admin.ModelAdmin):

    form = DivisionForm
    list_display = ('nombre', 'jefe', 'departamento',)
    search_fields = ('nombre', 'departamento',)

admin.site.register(Division, DivisionAdmin)

class PaisAdmin(admin.ModelAdmin):
    form = PaisForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(Pais, PaisAdmin)

class CiudadAdmin(admin.ModelAdmin):
    form = CiudadForm
    list_display = ('nombreciudad', 'pais',)
    search_fields = ('nombreciudad', 'pais',)

admin.site.register(Ciudad, CiudadAdmin)

class EstadoCivilAdmin(admin.ModelAdmin):
    form = EstadoCivilForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(EstadoCivil, EstadoCivilAdmin)

class GradoUniversitarioAdmin(admin.ModelAdmin):
    form = GradoUniversitarioForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(GradoUniversitario, GradoUniversitarioAdmin)

class ConstanteTypeAdmin(admin.ModelAdmin):
    form = ConstanteTypeForm
    list_display = ('nombre', 'tipo',)
    search_fields = ('nombre', 'tipo',)

admin.site.register(ConstanteType, ConstanteTypeAdmin)


class MovimientoTypeAdmin(admin.ModelAdmin):
    form = MovimientoTypeForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(MovimientoType, MovimientoTypeAdmin)


class MovimientoMotivoAdmin(admin.ModelAdmin):
    form = MovimientoMotivoForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(MovimientoMotivo, MovimientoMotivoAdmin)


class DocumentoRespaldatorioAdmin(admin.ModelAdmin):
    #form = CategoriaSalarialForm
    list_display = ('codigo', 'fechaemision','quienfirma',)
    search_fields = ('codigo', 'fechaemision','quienfirma',)

admin.site.register(DocumentoRespaldatorio, DocumentoRespaldatorioAdmin)


class DocumentoTypeAdmin(admin.ModelAdmin):
    form = DocumentoTypeForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(DocumentoType, DocumentoTypeAdmin)


class AutoridadFirmanteAdmin(admin.ModelAdmin):
    form = AutoridadFirmanteForm
    list_display = ('cargo',)
    search_fields = ('cargo',)

admin.site.register(AutoridadFirmante, AutoridadFirmanteAdmin)


class LiquidacionTypeAdmin(admin.ModelAdmin):
    form = LiquidacionTypeForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(LiquidacionType, LiquidacionTypeAdmin)


class VariableAdmin(admin.ModelAdmin):
    form = VariableForm
    list_display = ('motivo','tipo',)
    search_fields = ('motivo','tipo',)

admin.site.register(Variable, VariableAdmin)


class ParametroAdmin(admin.ModelAdmin):
    form = ParametroForm
    list_display = ('codigo','descripcion',)
    search_fields = ('codigo','descripcion',)

admin.site.register(Parametro, ParametroAdmin)


'''class StateAdmin(admin.ModelAdmin):
    form = StateForm
    list_display = ('nombre','tipo',)
    search_fields = ('nombre','tipo',)

admin.site.register(State, StateAdmin)


class StateTypeAdmin(admin.ModelAdmin):
    form = StateTypeForm
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(StateType, StateTypeAdmin)'''