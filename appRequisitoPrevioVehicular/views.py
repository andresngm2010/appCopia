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
    lista_vehiculos = Vehiculo.objects.all()
    return render(request, 'vehiculos_list.html', {'lista_vehiculos': lista_vehiculos})


def registrar_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.save()
            aux = str(vehiculo.pk)
            loger = LogEntry(user=request.user, object_id=vehiculo.pk,
                             object_repr='Vehiculo object(' + aux + ')',
                             content_type=ContentType.objects.get(app_label='appRequisitoPrevioVehicular',
                                                                  model='vehiculo'), action_flag=1,
                             change_message=[{"added": {'Vehiculo object(' + aux + ')'}}])
            loger.save()
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
            print(parametros)
            #parsed_json = eval(parametros)
            #print(parsed_json)
            requests.post('http://127.0.0.1:8000/usuario', parametros)
            return redirect('vehiculos_list')
    else:
        form = UsuarioForm()
    return render(request, 'registrar_usuario.html', {'form': form})


def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.save()
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
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    vehiculo.placa = vehiculo.placa
    lista_multas = Multa.objects.filter(vehiculo=vehiculo)
    return render(request, 'multas_list.html', {'lista_multas': lista_multas, 'vehiculo': vehiculo})


def registrar_multa(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        form = MultaForm(request.POST)
        if form.is_valid():
            multa = form.save(commit=False)
            multa.vehiculo = vehiculo
            multa.save()
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
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    aux = str(vehiculo.pk)
    vehiculo.delete()
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
