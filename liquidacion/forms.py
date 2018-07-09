from django import forms
from django.contrib import admin
#from django.forms import *
from django.forms import ModelForm, NumberInput, IntegerField
from django.forms.widgets import SelectDateWidget, DateInput
from django.forms.fields import DateField
from liquidacion.models import *
from sueldos.settings import DATE_INPUT_FORMATS
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.forms.ranges import DateRangeField, RangeWidget
from django.forms.widgets import TimeInput

MES_OPTIONS = (
    (0 , 'Todos'),
    (1 , 'Enero'),
    (2 , 'Febrero'),
    (3 , 'Marzo'),
    (4 , 'Abril'),
    (5 , 'Mayo'),
    (6 , 'Junio'),
    (7 , 'Julio'),
    (8 , 'Agosto'),
    (9 , 'Septiembre'),
    (10 , 'Octubre'),
    (11 , 'Noviembre'),
    (12 , 'Diciembre'),
)

MES2_OPTIONS = (
    (1 , 'Enero'),
    (2 , 'Febrero'),
    (3 , 'Marzo'),
    (4 , 'Abril'),
    (5 , 'Mayo'),
    (6 , 'Junio'),
    (7 , 'Julio'),
    (8 , 'Agosto'),
    (9 , 'Septiembre'),
    (10 , 'Octubre'),
    (11 , 'Noviembre'),
    (12 , 'Diciembre'),
)

MOTIVO_OPTIONS = (
    ('Contrato', 'Contrato'),
    ('Permanente' , 'Permanente'),
)

TIPO_OPTIONS = (
    ('Alta', 'Alta'),
    ('Baja' , 'Baja'),
)


class FilroTipoMovimientoForm(forms.Form):

    desde = forms.DateTimeField(label='Desde', required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control datepicker',
                                                  'id': 'fec_ini',}))

    hasta = forms.DateTimeField(label='Hasta', required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control datepicker',
                                                  'id': 'fec_fin',}))

    tipo = forms.ChoiceField(label='Tipo de Movimiento', required=True, choices=TIPO_OPTIONS, widget=forms.Select(attrs={'class': 'form-control'}))


class FiltroMesForm(forms.Form):

    mes = forms.ChoiceField(label='Mes', required=True, choices=MES_OPTIONS, widget=forms.Select(attrs={'class': 'form-control',
                                                                                          'name': 'mes',
                                                                                          'id': 'mes-select',
                                                                                          }))


class FiltroDepartamentoForm(forms.Form):

    departamento = IntegerField(label='Departamento', required=True, widget=forms.Select(attrs={'class': 'form-control',
                                                                                          'name': 'departamento-select',
                                                                                          'id': 'departamento-select',
                                                                                          }))


class FiltroGastosForm(forms.Form):

    motivo = forms.ChoiceField(label='Tipo de cargo', required=True, choices=MOTIVO_OPTIONS, widget=forms.Select(attrs={'class': 'form-control',
                                                                                          'name': 'motivo',
                                                                                          'id': 'motivo-select',
                                                                                          }))

    anho = forms.IntegerField(label='Año', required=True, widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                          'name': 'anho',
                                                                                          }))


class LiquidacionDefinitivaForm(forms.Form):

    funcionario = IntegerField(label='Nro. de Documento de Identidad', required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder' : "Ingrese el número de documento",}))

class VacacionesFuncionarioForm(forms.Form):

    funcionario = IntegerField(label='Nro. de Documento de Identidad', required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder' : "Ingrese el numero de documento de identidad"}))


class LiqPendientesForm(forms.Form):

    funcionario = forms.CharField(label='Funcionario', required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'name': 'funcionario',
                                                              }))

    mes = forms.ChoiceField(label='Mes', required=True, choices=MES2_OPTIONS, widget=forms.Select(attrs={'class': 'form-control',
                                                                                          'name': 'mes',
                                                                                          'id': 'mes-select',
                                                                                          }))

    anho = forms.IntegerField(label='Año', required=True, widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                          'name': 'anho',
                                                                                          }))

class VacacionesusadasForm(forms.ModelForm):
    class Meta:
        model = Vacacionesusadas
        exclude = ['vacaciones']
        widgets = {
            'diasusados': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }


class DetalleLiquidacionForm(forms.ModelForm):
    class Meta:
        model = DetalleLiquidacion
        exclude = ['liquidacion','total', 'salario_proporcional', 'pago']
        widgets = {
            'variable': forms.Select(attrs={
                'class': 'form-control',
            }),
            'parametro': forms.Select(attrs={
                'class': 'form-control',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }


class LiquidacionhaberForm(forms.ModelForm):
    class Meta:
        model = Liquidacionhaber
        fields = '__all__'


class LiqMensualForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        exclude = ['ultimamodificacion' ,'propietario', 'tipo', 'haberes']
        widgets = {
            'vacaciones_usadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'size' : "30",
            }),
            'motivo': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class PreLiqMensualForm(forms.Form):

    desde = forms.DateTimeField(label='Desde', required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control datepicker',
                                                  'id': 'fec_ini',}))

    hasta = forms.DateTimeField(label='Hasta', required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control datepicker',
                                                  'id': 'fec_fin',}))

    departamento = forms.IntegerField(label='Departamento', required=True, widget=forms.Select(attrs={'class': 'form-control',
                                                                                          'name': 'departamento',
                                                                                          'id': 'departamento-select',
                                                                                          }))

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        exclude = ['movimiento_padre','funcionario','estado','esPrimero', 'familia']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'categoria_salarial': forms.TextInput(attrs={
                'type': 'hidden',
                'class': 'form-control'
            }),
            'og': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'motivo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'formapago': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ffinanciamiento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'division': forms.Select(attrs={
                'class': 'form-control'
            }),
            'funcion': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fechainicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'fechafin': forms.DateInput(attrs={
                'type' : 'date',
                'class': 'form-control',
                'readonly': True
            }),
            'horaEntrada': forms.TimeInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'horaSalida': forms.TimeInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'tieneAguinaldo': forms.CheckboxInput(attrs={
                'class': 'form-control'
            }),
            'tieneVacaciones': forms.CheckboxInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_fechainicio(self):
        fechainicio = self.cleaned_data.get('fechainicio')
        if fechainicio is None :
            raise forms.ValidationError("Este campo es lolo")
        return self.cleaned_data['fechainicio']
    def clean_categoria_salarial(self):
        categoria_salarial = self.cleaned_data.get('categoria_salarial')
        if categoria_salarial is None :
            raise forms.ValidationError("lololo")
        return self.cleaned_data['categoria_salarial']
    '''def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if tipo.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el tipo de categoria")
        return self.cleaned_data['tipo']'''


class ConstanteForm(ModelForm):

    class Meta:
        model = Constante
        exclude = ['movimiento']
        widgets = {
            'cantidad_veces': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class PagoForm(ModelForm):

    class Meta:
        model = Pago
        exclude = ['movimiento']
        widgets = {
            'mes': forms.Select(attrs={
                'class': 'form-control',
                'name': 'mes-select',
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }


class CategoriaSalarialForm(forms.ModelForm):

    class Meta:
        model = CategoriaSalarial
        fields = '__all__'
    def clean_asignacion(self):
        asignacion = self.cleaned_data.get('asignacion')
        if asignacion < 1 :
            raise forms.ValidationError("Ingrese un monto valido para la asignacion salarial")
        return self.cleaned_data['asignacion']
    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if tipo.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el tipo de categoria")
        return self.cleaned_data['tipo']


class AutoridadFirmanteForm(forms.ModelForm):
    class Meta:
        model = AutoridadFirmante
        fields = '__all__'
        widgets = {
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class DocumentoRespaldatorioForm(forms.ModelForm):

    class Meta:
        model = DocumentoRespaldatorio
        exclude = ['movimiento']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'fechaemision': forms.DateInput(attrs={
                'class': 'form-control',
            }),
            'autoridadfirmante': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quienfirma': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

class Objeto_De_GastoAdminForm(forms.ModelForm):
    class Meta:
        model = Objeto_De_Gasto
        fields = '__all__'
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'concepto': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        convertido = len(str(abs(numero)))
        if convertido > 3 :
            raise forms.ValidationError("Ingrese un numero de 3 digitos o menos")
        return self.cleaned_data['numero']

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = '__all__'

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = '__all__'

class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = '__all__'

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = '__all__'

class EstadoCivilForm(forms.ModelForm):
    class Meta:
        model = EstadoCivil
        fields = '__all__'

class GradoUniversitarioForm(forms.ModelForm):
    class Meta:
        model = GradoUniversitario
        fields = '__all__'


class ConstanteTypeForm(forms.ModelForm):
    #tipo = forms.ChoiceField(choices=ConstanteType_OPTIONS, widget=forms.RadioSelect())

    class Meta:
        model = ConstanteType
        fields = '__all__'

class MovimientoTypeForm(forms.ModelForm):
    class Meta:
        model = MovimientoType
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

class MovimientoMotivoForm(forms.ModelForm):
    class Meta:
        model = MovimientoMotivo
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

class DocumentoTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentoType
        fields = '__all__'


class LiquidacionTypeForm(forms.ModelForm):
    class Meta:
        model = LiquidacionType
        fields = '__all__'


class VariableForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=ConstanteType_OPTIONS, widget=forms.RadioSelect())
    class Meta:
        model = Variable
        fields = '__all__'
    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo')
        convertido = motivo.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un motivo valido, sin numeros ni simbolos")
        return self.cleaned_data['motivo']


class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = '__all__'
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        convertido = len(codigo)
        if convertido != 3 or codigo.isupper() is False:
            raise forms.ValidationError("Ingrese un numero de 3 letras en mayusculas, Ejemplo: 'JOR','HOR'")
        return self.cleaned_data['codigo']
    '''def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        convertido = descripcion.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese una descripcion valida, sin numeros ni simbolos")
        return self.cleaned_data['descripcion']'''


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = '__all__'


class StateTypeForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=ConstanteType_OPTIONS, widget=forms.RadioSelect())
    class Meta:
        model = StateType
        fields = '__all__'


class BusquedaMovimientoFuncionarioForm(forms.Form):

    cedula = forms.IntegerField(label='Nro. de Cedula', required=False, widget=forms.TextInput(attrs={'class': 'form-control',}))

    nombres = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',}))

    apellidos = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', }))