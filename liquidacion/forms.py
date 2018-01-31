from django import forms
from django.contrib import admin
from liquidacion.models import *

class CategoriaSalarialForm(forms.ModelForm):
    class Meta:
        model = CategoriaSalarial
        fields = '__all__'
    def clean_asignacion(self):
        asignacion = self.cleaned_data.get('asignacion')
        if asignacion < 1 :
            raise forms.ValidationError("Ingrese un monto valido para la asignacion salarial")
        return self.cleaned_data['asignacion']
    def clean_cargo(self):
        cargo = self.cleaned_data.get('cargo')
        if cargo.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el cargo")
        return self.cleaned_data['cargo']
    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if tipo.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el tipo de categoria")
        return self.cleaned_data['tipo']


class AutoridadFirmanteForm(forms.ModelForm):
    class Meta:
        model = AutoridadFirmante
        fields = '__all__'
    def clean_cargo(self):
        cargo = self.cleaned_data.get('cargo')
        if cargo.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el cargo")
        return self.cleaned_data['cargo']


class Objeto_De_GastoAdminForm(forms.ModelForm):
    class Meta:
        model = Objeto_De_Gasto
        fields = '__all__'
    def clean_concepto(self):
        concepto = self.cleaned_data.get('concepto')
        convertido = concepto.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido para el concepto, sin numeros ni simbolos")
        return self.cleaned_data['concepto']
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
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']

class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = '__all__'
    def clean_nombreciudad(self):
        nombreciudad = self.cleaned_data.get('nombreciudad')
        convertido = nombreciudad.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombreciudad']


class EstadoCivilForm(forms.ModelForm):
    class Meta:
        model = EstadoCivil
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class GradoUniversitarioForm(forms.ModelForm):
    class Meta:
        model = GradoUniversitario
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class ConstanteTypeForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=ConstanteType_OPTIONS, widget=forms.RadioSelect())
    class Meta:
        model = ConstanteType
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class MovimientoTypeForm(forms.ModelForm):
    class Meta:
        model = MovimientoType
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class MovimientoMotivoForm(forms.ModelForm):
    class Meta:
        model = MovimientoMotivo
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class DocumentoTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentoType
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class LiquidacionTypeForm(forms.ModelForm):
    class Meta:
        model = LiquidacionType
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


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
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        convertido = descripcion.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese una descripcion valida, sin numeros ni simbolos")
        return self.cleaned_data['descripcion']


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']


class StateTypeForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=ConstanteType_OPTIONS, widget=forms.RadioSelect())
    class Meta:
        model = StateType
        fields = '__all__'
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        convertido = nombre.replace(" ", "")
        if convertido.isalpha() is False:
            raise forms.ValidationError("Ingrese un nombre valido, sin numeros ni simbolos")
        return self.cleaned_data['nombre']