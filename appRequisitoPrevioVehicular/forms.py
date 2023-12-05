from django import forms

from .models import Vehiculo, Multa, Usuario

class UsuarioForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'email', 'cedula', 'telefono' )

class VehiculoForm(forms.ModelForm):

    class Meta:
        model = Vehiculo
        fields = ('propietario', 'placa', 'marca', 'año', 'modelo', 'chasis')


class MultaForm(forms.ModelForm):

    class Meta:
        model = Multa
        fields = ('valor', 'año', 'descripcion')
