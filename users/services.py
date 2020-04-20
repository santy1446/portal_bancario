import requests

#URL y Token del servicio WEB

BASE_URL = 'https://apicuentasbancarias.herokuapp.com/'
headers = {'Authorization': 'Token c6f6ce1b69d275eba8eab1b8cf9795ed26f44624'}

#Obtener informacion de la API

def getInfo(url):
	response = requests.get(url, headers=headers)
	return response

#Agregar una cuenta

def postAccount(account_number, pk_user, activate, type_account):
	url = BASE_URL+'account/'
	newReg = {
        "account_number": account_number,
        "user_id": pk_user,
        "activate": activate,
        "type_account": type_account,
        "state_account": 1
        }
	response = requests.post(url, json = newReg, headers=headers)

#Agregar un movimiento
def postMovement (id_account, id_balance, id_category, typ, monto, date):
        url = BASE_URL+'movement/'
        newReg = {
        "id_account" : id_account, 
        "id_balance" : id_balance, 
        "categoria" : id_category, 
        "tipo" : typ, 
        "monto" : monto, 
        "fecha" : date
        }
        response = requests.post(url, json = newReg, headers=headers)

#Actualizar balance
def updateBalance(pk, tipo, monto, user, account):
        url = BASE_URL+"balance/"
        monto = int(monto)
        response = getInfo(url)
        payload = response.json()
        balance = {}
        if response:
            for data in payload:
                if data['id'] == pk:
                    balance = data

                    if tipo == "Gasto":
                        saldo = int(balance['saldo'])
                        saldo -= monto
                        balance['saldo'] = str(saldo)
                        balance['gastos'] += monto
                    else:
                        saldo = int(balance['saldo'])
                        saldo += monto
                        balance['saldo'] =str(saldo)
                        balance['ingresos'] += monto
   
        pk = str(pk)
        url_update = url + pk
        payload = {
        "id_user": user,
        "id_account": account,
        "saldo": balance['saldo'],
        "ingresos": balance['ingresos'],
        "gastos": balance['gastos']
        }

        response = requests.put(url_update, json = payload, headers=headers)

        if response:
                print(response.content)
        return

#Alterar el balance
def alterBalance(pk, tipo, monto, user, account):
    url = BASE_URL+"balance/"
    monto = int(monto)
    pk = int(pk)
    response = getInfo(url)
    payload = response.json()
    balance = {}
    print(pk)
    print(payload)
    if response:
        for data in payload:
            if data['id'] == pk:
                balance = data
                print("balance en condicion: ",balance)

                if tipo == "Gasto":
                    saldo = int(balance['saldo'])
                    saldo += monto
                    balance['saldo'] = str(saldo)
                    balance['gastos'] -= monto
                else:
                    saldo = int(balance['saldo'])
                    saldo -= monto
                    balance['saldo'] =str(saldo)
                    balance['ingresos'] -= monto

    pk = str(pk)
    url_update = url + pk
    print("Fuera dee condicion: ",balance)
    payload = {
    "id_user": user,
    "id_account": account,
    "saldo": balance['saldo'],
    "ingresos": balance['ingresos'],
    "gastos": balance['gastos']
    }

    response = requests.put(url_update, json = payload, headers=headers)

    if response:
        print(response.content)
    return



