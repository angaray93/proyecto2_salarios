from django import forms
from django.contrib import admin
from liquidacion.models import *

class CategoriaSalarialForm(forms.ModelForm):

    class Meta:
        model = CategoriaSalarial
        fields = '__all__'

    def clean_asignacion(self):
        asignacion = self.cleaned_data.get('asignacion')
        if asignacion < 0 :
            raise forms.ValidationError("No se puede ingresar numeros negativos")
        return self.cleaned_data['asignacion']