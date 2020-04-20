from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SignupForm
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import ProfileSerializer
from .models import Profile
from .services import getInfo, postAccount, postMovement, updateBalance, alterBalance
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import requests
import json
from random import randint, uniform,random
# ListView
from django.views.generic.list import ListView
#Login Requerido
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import datetime
from dateutil import parser

#URL y Token del servicio WEB

BASE_URL = 'https://apicuentasbancarias.herokuapp.com/'
headers = {'Authorization': 'Token c6f6ce1b69d275eba8eab1b8cf9795ed26f44624'}

#Formulario de registro de usuario

def signup(request):
    if request.method == 'POST':
        form =SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            SendEmailActivateUser(request, user)
            logout(request)
            return HttpResponseRedirect(reverse("users:emailsent", args=[user.username]))
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

#Enviar rorreo eLectrónica para activar usuario
def SendEmailActivateUser(request, user):
    current_site = get_current_site(request)
    subject = 'Activar cuenta PORTAL BANCARIO REMINGTON'
    html_content = render_to_string('email/account_activation.html',{
         'user': user,
         'domain': current_site.domain,
         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
         'token': account_activation_token.make_token(user),
    })
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(
            subject, text_content, from_email=settings.EMAIL_HOST_USER, to=[user.email]
    )
    msg.attach_alternative(html_content,"text/html")
    msg.send()


#Activar un usuario que previamente se ha registrado
def ActivateUser(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=none

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = 1
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')
    else:
        return render(request,'registration/account_activation_invalid.html')

#Vista de activacion de usuario

def templateEmailSent(request, username):
    return render(request,'registration/account_activation.html', {'username': username})

#Listar usuarios (Empleado)
class UserList(PermissionRequiredMixin, ListView):
    permission_required = 'users.listarusuarios'
    model = User

#Funcion de administrar cuentas
@login_required
def UserApp(request, pk):
    pk_user = pk
    #Get accounts
    response = getInfo(BASE_URL+'account/')
    if response.status_code == 200:
        payload = response.json()
        context = []
        pk_to_compare = int(pk)
        if response:
            for data in payload:
                #Filter accounts by pk
                if data['user_id'] == pk_to_compare:
                    pk = data['id']
                    account_number = data['account_number']
                    #dt = parser.parse(data['creation_day'])
                    creation_day = parser.parse(data['creation_day'])
                    type_account = data['type_account']
                    state_account = data['state_account']

                    context.append({
                        'id':pk,
                        'account_number':account_number,
                        'creation_day': creation_day,
                        'type_account': type_account,
                        'state_account': state_account
                    })

    #Get state Acounts
    response = getInfo(BASE_URL+'stateAccount/')
    if response.status_code == 200:
        payload = response.json()
        state = []
        if response:
            for data in payload:
                pk = data['id']
                name = data['name']
                state.append({
                    'id':pk,
                    'name':name
                })
    #Get state Acounts
    response = getInfo(BASE_URL+'typeAccount/')
    if response.status_code == 200:
        payload = response.json()
        types = []
        if response:
            for data in payload:
                pk = data['id']
                name = data['name']
                types.append({
                    'id':pk,
                    'name':name
                })

    return render(request, "auth/user_app.html", {'context': context, 'state': state, 'types': types, 'identification' : pk_user})

#crear una nueva cuenta
@login_required
def newAccount(request, pk):
    option = request.GET.get('option')
    pk_user = int(pk)
    account_number = randint(0,999999999)
    activate = True
    state_account = 1
    #Get state Acounts
    response = getInfo(BASE_URL+'typeAccount/')
    if response.status_code == 200:
        payload = response.json()
        types = []
        if response:
            for data in payload:
                if data['name'] == option:
                    type_account = data['id']

    #POST new account
    postAccount(account_number, pk_user, activate, type_account)
    return redirect('/users/userapp/%s'%pk_user)

#Observar balance y moviminetos de una cuenta 
@login_required
def getBadget(request, pk, pk_user):
    #Get state Acounts
    url = BASE_URL+'balance/'
    response = getInfo(BASE_URL+'balance/')
    flag = False

    if response.status_code == 200:
        payload = response.json()
        BalanceObj = {}
        balance = {}
        if response:
            for data in payload:

                if data['id_account'] == pk:
                    flag = True
                    balance = data
                    BalanceObj = {
                        'id' : data['id'],
                        'saldo':data['saldo'],
                        'ingresos':data['ingresos'], 
                        'gastos':data['gastos']
                    }

            if flag == False:
                BalanceObj = {
                    "id_account": pk,
                    "id_user": pk_user,
                    "saldo": "0",
                    "ingresos": 0,
                    "gastos": 0      
                }

                response = requests.post(url, json = BalanceObj, headers=headers) 

    response = getInfo(BASE_URL+'movement/')
    if response.status_code == 200:
        payload = response.json()
        movementList = []
        for data in payload:
            if data['id_account'] == pk and data['id_balance'] == balance['id']:
                movementList.append(data)

    response = getInfo(BASE_URL+'category/')
    if response.status_code == 200:
        payload = response.json()
        categoryList = []
        for data in payload:
            categoryList.append(data)


    return render(request, 'auth/user_movement.html', {'BalanceObj' : BalanceObj, 'account_id': pk, 'movementList' : movementList, 'categoryList' : categoryList, 'pk_user' : pk_user})

#Creacion de movimiento
@login_required
def Movement(request, pk):
    response = getInfo(BASE_URL+'balance/')
    pk_account = int(pk)
    payload = response.json()
    for data in payload:
        if data['id_account'] == pk_account:
            pk_balance = data['id']

    #Get Categories
    response = getInfo(BASE_URL+'category/')
    if response.status_code == 200:
        payload = response.json()
        categories = []
        if response:
            for data in payload:
                pk = data['id']
                name = data['descripcion']
                categories.append({
                    'id':pk,
                    'name':name
                })

    return render(request, 'auth/create_movement.html',{"pk_account":pk_account, "pk_balance":pk_balance, "categories": categories})

#Crear nuevo movimiento
@login_required
def newMovement(request, pk_account, pk_balance, pk_user):

    rest_url = pk_account + '/' + pk_user
    pk_account = int(pk_account)
    pk_balance = int(pk_balance)
    pk_user = int(pk_user)
    category = request.GET.get('category')
    typeMovement = request.GET.get('typeMovement')
    monto = request.GET.get('monto')
    date = request.GET.get('date')
    postMovement(pk_account, pk_balance, category, typeMovement, monto, date)
    updateBalance(pk_balance, typeMovement, monto, pk_user, pk_account)
    return redirect('/users/getBadget/' + rest_url)

#Eliminar movimiento
def deleteMovement(request, pk_account, pk_balance, pk_user, pk_movement):
    rest_url = pk_account + '/' + pk_user
    response = getInfo(BASE_URL+'movement/')
    payload = response.json()
    pk_movement = int(pk_movement)

    for data in payload:
        if data['id'] == pk_movement:
            typeMovement = data['tipo']
            monto = data['monto']

    
    url = BASE_URL+"movement/%s"%pk_movement
    response = requests.delete(url, headers=headers)
    alterBalance(pk_balance, typeMovement, monto, pk_user, pk_account)
    return redirect('/users/getBadget/' + rest_url)

#Desactivar una cuenta (Empleado)
def disableStateAccount(request, pk, account_number, creation_day, type_account, state_account, pk_user):
    url = BASE_URL+'account/'
    account_number = int(account_number)
    type_account = int(type_account)
    state_account = int(state_account)
    pk_user = int(pk_user)

    payload = {
    "account_number" : int(account_number),
    "user_id" : int(pk_user),
    "creation_day" : creation_day,
    "activate" : True,
    "type_account" : int(type_account),
    "state_account" : 1
    }

    if state_account == 1:
        payload['state_account'] = 2
        payload['activate'] = False

    response = requests.put(url + pk, json = payload, headers=headers)
    return redirect('/users/userapp/%s'%pk_user)


# Create your views here.
class ProfileAPI(APIView):

    def get(self, request):
        profile = User.objects.all()
        serializer = ProfileSerializer(profile, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        profile = User.objects.get(pk=pk)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = User.objects.get(pk=pk)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
