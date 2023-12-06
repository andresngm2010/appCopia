from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib import messages
from django.contrib.admin.models import LogEntry

from .models import Vehiculo, Multa, Usuario
from .forms import VehiculoForm, MultaForm, UsuarioForm

from appRequisitoPrevioVehicular.encrypt_util import *

import requests
import json


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('vehiculos_list')
    else:
        template = loader.get_template('login.html')
        context = {}
        return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    return redirect('authentication')


def login_intent(request):
    username = request.POST.get('usuario')
    password = request.POST.get('contraseña')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if user.is_superuser:
            # TODO: redirect to admin page
            return redirect('vehiculos_list')
    else:
        template = loader.get_template('login.html')
        context = {
            'error': 'Usuario o contraseña incorrectos'
        }
        return HttpResponse(template.render(context, request))


def vehiculos_list(request):
    lista_vehiculos = requests.get('http://127.0.0.1:8000/vehiculo').json()
    lista_vehiculos2 = []
    for vehiculo in lista_vehiculos:
        auxV = Vehiculo()
        auxV.pk = vehiculo[0]
        auxV.propietario = vehiculo[1]
        auxV.placa = vehiculo[2]
        auxV.marca = vehiculo[3]
        auxV.año = vehiculo[4]
        auxV.modelo = vehiculo[5]
        auxV.chasis = vehiculo[6]
        lista_vehiculos2.append(auxV)
    return render(request, 'vehiculos_list.html', {'lista_vehiculos': lista_vehiculos2})


def registrar_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            aux = str(vehiculo.pk)
            loger = LogEntry(user=request.user, object_id=vehiculo.pk,
                             object_repr='Vehiculo object(' + aux + ')',
                             content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                                  model='vehiculo'), action_flag=1,
                             change_message=[{"added": {'Vehiculo object(' + aux + ')'}}])
            loger.save()
            parametros = { 'propietario': vehiculo.propietario, 'placa':vehiculo.placa, 'marca':vehiculo.marca, 'año':vehiculo.año, 'modelo':vehiculo.modelo, 'chasis':vehiculo.chasis }
            requests.post('http://127.0.0.1:8000/vehiculo', json=parametros)
            return redirect('vehiculos_list')
    else:
        form = VehiculoForm()
    return render(request, 'registrar_vehiculo.html', {'form': form})

def registrar_usuario(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            aux = str(usuario.pk)
            loger = LogEntry(user=request.user, object_id=usuario.pk,
                             object_repr='Usuario object(' + aux + ')',
                             content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                                  model='usuario'), action_flag=1,
                             change_message=[{"added": {'Usuario object(' + aux + ')'}}])
            loger.save()
            parametros = "{\"nombre\":\""+usuario.nombre+"\", \"apellido\":\""+usuario.apellido+"\", \"email\":\""+usuario.email+"\", \"cedula\":\""+usuario.cedula+"\", \"telefono\":\""+usuario.telefono+"\"}"
            requests.post('http://127.0.0.1:8000/usuario', parametros)
            return redirect('vehiculos_list')
    else:
        form = UsuarioForm()
    return render(request, 'registrar_usuario.html', {'form': form})


def editar_vehiculo(request, pk):
    args = {'primary_key': pk}
    response = requests.get('http://127.0.0.1:8000/vehiculo/{pk}', params=args).json()
    vehiculo = Vehiculo()
    vehiculo.pk = response[0][0]
    vehiculo.propietario = response[0][1]
    vehiculo.placa = response[0][2]
    vehiculo.marca = response[0][3]
    vehiculo.año = response[0][4]
    vehiculo.modelo = response[0][5]
    vehiculo.chasis = response[0][6]
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            parametros = { 'propietario': vehiculo.propietario, 'placa':vehiculo.placa, 'marca':vehiculo.marca, 'año':vehiculo.año, 'modelo':vehiculo.modelo, 'chasis':vehiculo.chasis }
            response = requests.post('http://127.0.0.1:8000/vehiculo/{pk}', json = parametros, params=args)
            aux = str(vehiculo.pk)
            loger = LogEntry(user=request.user, object_id=vehiculo.pk,
                             object_repr='Vehiculo object(' + aux + ')',
                             content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                                  model='vehiculo'), action_flag=1,
                             change_message=[{"updated": {'Vehiculo object(' + aux + ')'}}])
            loger.save()
            return redirect('vehiculos_list')
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'editar_vehiculo.html', {'form': form})


def listar_multas(request, pk):
    args = {'primary_key': pk}
    response = requests.get('http://127.0.0.1:8000/vehiculo/{pk}', params=args).json()
    vehiculo = Vehiculo()
    vehiculo.pk = response[0][0]
    vehiculo.propietario = response[0][1]
    vehiculo.placa = response[0][2]
    vehiculo.marca = response[0][3]
    vehiculo.año = response[0][4]
    vehiculo.modelo = response[0][5]
    vehiculo.chasis = response[0][6]
    lista_multas = requests.get('http://127.0.0.1:8000/multa/{pk}', params=args).json()
    lista_multas2 = []
    for multa in lista_multas:
        auxM = Multa()
        auxM.pk = multa[0]
        auxM.vehiculo = vehiculo
        auxM.valor = multa[2]
        auxM.año = multa[3]
        auxM.descripcion = multa[4]
        lista_multas2.append(auxM)
    return render(request, 'multas_list.html', {'lista_multas': lista_multas2, 'vehiculo': vehiculo})


def registrar_multa(request, pk):
    args = {'primary_key': pk}
    response = requests.get('http://127.0.0.1:8000/vehiculo/{pk}', params=args).json()
    vehiculo = Vehiculo()
    vehiculo.pk = response[0][0]
    vehiculo.propietario = response[0][1]
    vehiculo.placa = response[0][2]
    vehiculo.marca = response[0][3]
    vehiculo.año = response[0][4]
    vehiculo.modelo = response[0][5]
    vehiculo.chasis = response[0][6]
    if request.method == "POST":
        form = MultaForm(request.POST)
        if form.is_valid():
            multa = form.save(commit=False)
            parametros = { 'vehiculo': vehiculo.pk, 'valor':multa.valor, 'año':multa.año, 'descripcion':multa.descripcion}
            response = requests.post('http://127.0.0.1:8000/multa', json = parametros)
            aux = str(multa.pk)
            loger = LogEntry(user=request.user, object_id=multa.pk,
                             object_repr='Multa object(' + aux + ')',
                             content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                                  model='multa'), action_flag=1,
                             change_message=[{"added": {'Multa object(' + aux + ')'}}])
            loger.save()
            return redirect('vehiculos_list')
    else:
        form = MultaForm()
    return render(request, 'registrar_multa.html', {'form': form})


def consultar_vehiculo(request):
    opcion = request.POST.get('opcion')
    dato = request.POST.get('dato')
    if opcion == 'Placa':
        try:
            vehiculo = Vehiculo.get_vehiculo_by_placa(self=Vehiculo(), dato=dato)
        except Vehiculo.DoesNotExist:
            messages.error(request, 'La placa ingresada no existe')
            return redirect('authentication')
    else:
        try:
            vehiculo = Vehiculo.get_vehiculo_by_chasis(self=Vehiculo(), dato=dato)
        except Vehiculo.DoesNotExist:
            messages.error(request, 'El chasis ingresado no existe')
            return redirect('authentication')
    vehiculo.placa = vehiculo.placa
    lista_multas = Multa.objects.filter(vehiculo=vehiculo)
    return render(request, 'consultar_vehiculo.html', {'lista_multas': lista_multas, 'vehiculo': vehiculo})


def eliminar_vehiculo(request, pk):
    args = {'primary_key': pk}
    response = requests.get('http://127.0.0.1:8000/vehiculo/{pk}', params=args).json()
    vehiculo = Vehiculo()
    vehiculo.pk = response[0][0]
    vehiculo.propietario = response[0][1]
    vehiculo.placa = response[0][2]
    vehiculo.marca = response[0][3]
    vehiculo.año = response[0][4]
    vehiculo.modelo = response[0][5]
    vehiculo.chasis = response[0][6]
    aux = str(vehiculo.pk)
    response = requests.delete('http://127.0.0.1:8000/vehiculo', params=args)
    print(response)
    loger = LogEntry(user=request.user, object_id=vehiculo.pk,
                     object_repr='Vehiculo object(' + aux + ')',
                     content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                          model='vehiculo'), action_flag=1,
                     change_message=[{"delete": {'Vehiculo object(' + aux + ')'}}])
    loger.save()
    return redirect('vehiculos_list')


def logs_list(request):
    lista_logs = LogEntry.objects.all()
    return render(request, 'logs.html', {'lista_logs': lista_logs})
