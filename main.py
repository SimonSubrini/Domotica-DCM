"""
--------------------------------------------------------------------------------------------------------------------------------------------------

Revisar el archivo "Leer--Proximos pasos" de la carpeta D:\Simon\Programacion\MicroPython\Firebase_V2 para ver como continuar

--------------------------------------------------------------------------------------------------------------------------------------------------
"""

import time
import json

# import pandas as pd
from machine import Pin
import LibWifi
import NRF24L01
import Functions
import ufirebase as firebase

# Inicialización de variables
""" 
Cuando utilice el modulo "machine" el número correspondiente a cada pin
lo tengo que sacar de la imagen "NodeMcu-PinOut". Estos números aparecen
como "GPIO"+Número
"""
led = Pin(2, Pin.OUT)
Button = Pin(16, Pin.IN)
Cant_Slaves = 0
ListSlaves = []
nrf24Module=[]


# ------------------------------------------------------------------------- Configuración -------------------------------------------------------------------------

def Config():
    ConnectWifi()
    ConnectFirebase()
    ConnectNRF24L01()


def ConnectNRF24L01():
    global nrf24Module
    nrf24Module = NRF24L01.initNrf24(15, 16, b'00000')


def ConnectWifi():
    with open('./Wifi_Pass.txt', 'rt', encoding='utf-8') as file:
        Wifi_Pass = file.read()
    Redes = Wifi_Pass.split('\r\n\r\n')
    for i in range(len(Redes)):
        WIFI_SSID = Redes[i].split('"')[1]
        WIFI_PW = Redes[i].split('"')[3]
        if LibWifi.connect_wifi(WIFI_SSID, WIFI_PW) == 1:
            break


def ConnectFirebase():
    with open('./Firebase_Pass.txt', 'rt', encoding='utf-8') as file:
        FireBase_Pass = file.read()
    Firebase_ID = FireBase_Pass.split('"')[1]
    Firebase_Auth = FireBase_Pass.split('"')[3]
    firebase.setURL("https://" + Firebase_ID + ".firebaseio.com/")


# ------------------------------------------------------------------------- Esclavos -------------------------------------------------------------------------

def CreateSlave(Type):
    # Slaves = GetSlaves()

    if Type == "Luces":
        ListSlaves.append(SlLuces(Cant_Slaves))
    elif Type == "Ventiladores":
        ListSlaves.append(SlVentiladores(Cant_Slaves))


class Slave:
    def __init__(self, Address=0, Sl_Type=""):
        self.Address = Address
        self.Sl_Type = Sl_Type
        print('Nuevo esclavo creado\n'
              '     Dirección: {}\n'
              '     Tipo: {}'.format(self.Address, self.Sl_Type))

    def ReadAddress(self):
        return self.Address

    def ReadType(self):
        return self.Sl_Type

    def ChangeWParameters(self, Params={}):
        print("Modificando la información el slave de Address: {}".format(self.Address))
        print('      {}'.format(self.Struct))
        for param in Params:
            self.Struct[self.Address]["Informacion"][param] = Params[param]
        print('----> {}'.format(self.Struct))
        firebase.patch("Dispositivos/Address", self.Struct)

    def ChangeRParameters(self, Params={}):
        print("Modificando las ordenes el slave de Address: {}".format(self.Address))
        print('      {}'.format(self.Struct))
        for param in Params:
            self.Struct[self.Address]["Ordenes"][param] = Params[param]
        print('----> {}'.format(self.Struct))
        firebase.patch("Dispositivos/Address", self.Struct)

    def Description(self):
        return "Address: {}, Type: {}, Parameters: {}".format(self.Address, self.Sl_Type, self.Struct[self.Address])


class SlLuces(Slave):
    def __init__(self, Address):
        super().__init__(Address, "Luces")
        self.Struct = {self.Address: Structure["Luces"]}
        firebase.patch("Dispositivos/Address", self.Struct)


class SlVentiladores(Slave):
    def __init__(self, Address):
        super().__init__(Address, "Ventiladores")
        self.Struct = {self.Address: Structure["Ventiladores"]}
        firebase.patch("Dispositivos/Address", self.Struct)


# ------------------------------------------------------------------------- Main Code -------------------------------------------------------------------------

Config()
with open('./Structure.json') as file_object:
    Structure = json.load(file_object)

while 1:
    print('Enviando numeros...')
    for i in range(10):
        NRF24L01.sendData(nrf24Module, i, b'11011')

    i = 0
    while i < 5:
        i += 1
        if Button.value() == 1:
            Cant_Slaves += 1
            print('\nBotón activado, Creando al esclavo {}'.format(Cant_Slaves))
            if Cant_Slaves / 2 == round(Cant_Slaves / 2, 0):
                Type = "Luces"
            else:
                Type = "Ventiladores"
            CreateSlave(Type)

    # Modificando parametros...
    ListSlaves[0].ChangeWParameters({
        "Consumo": 150
    })
    ListSlaves[0].ChangeRParameters({
        "Temp_Deseada": 30
    })

    ListSlaves[1].ChangeWParameters({
        "Intensidad_Actual": [
            255,
            50,
            10
        ]
    })
    ListSlaves[1].ChangeRParameters({
        "Intensidad_Deseada": [
            150,
            250,
            70
        ]
    })
    ListSlaves[3].ChangeWParameters({
        "Consumo": 10,
        "Intensidad_Actual": [
            0,
            0,
            0
        ]
    })
    ListSlaves[3].ChangeRParameters({
        "Intensidad_Deseada": [
            0,
            0,
            0
        ]
    })
    print(
        "----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Descripciones: ")
    for slave in ListSlaves:
        print(slave.Description())
    print(
        "----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print(ListSlaves[3])
    break
