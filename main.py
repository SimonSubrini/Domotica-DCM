import time
import json

import pandas as pd
from machine import Pin
import LibWifi
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


def Config():
    ConnectWifi()
    ConnectFirebase()


def ConnectWifi():
    with open('./Wifi_Pass.txt', 'rt', encoding='utf-8') as file_object:
        Wifi_Pass = file_object.read()
    Redes = Wifi_Pass.split('\r\n\r\n')
    for i in range(len(Redes)):
        WIFI_SSID = Redes[i].split('"')[1]
        WIFI_PW = Redes[i].split('"')[3]
        if LibWifi.connect_wifi(WIFI_SSID, WIFI_PW) == 1:
            break


def ConnectFirebase():
    with open('./Firebase_Pass.txt', 'rt', encoding='utf-8') as file_object:
        FireBase_Pass = file_object.read()
    Firebase_ID = FireBase_Pass.split('"')[1]
    Firebase_Auth = FireBase_Pass.split('"')[3]
    firebase.setURL("https://" + Firebase_ID + ".firebaseio.com/")


def CreateSlave(Type):
    Slaves = GetSlaves()
    if Type == "Luces":
        SlLuces(Cant_Slaves)
    elif Type == "Ventiladores":
        SlVentiladores(Cant_Slaves)


def GetSlaves():
    try:
        Slaves = pd.read_csv('./Slaves.csv')
    except:
        Slaves = pd.DataFrame()
        Slaves.columns = ['Address', 'Type', 'Parameters']  # Renombro las columnas
    Slaves.index = Slaves['Address']
    return Slaves


class Slave:
    def __init__(self, Address=0, Sl_Type=""):
        self.__Address = Address
        self.__Sl_Type = Sl_Type
        self.__Consumption = 0  # En KW/
        print('Nuevo esclavo creado\n'
              'Dirección: {}\n'
              'Tipo: {}'.format(self.__Address, self.__Sl_Type))

    def ReadAddress(self):
        return self.__Address

    def ReadType(self):
        return self.__Sl_Type


class SlLuces(Slave):
    def __init__(self, Address):
        super().__init__(Address, "Luces")
        self.Parameters = {}
        self.Struct = {Cant_Slaves: Structure["Luces"]}
        firebase.patch("Dispositivos/Address", self.Struct)

    def ChangeWParameters(self, Params={}):
        self.Parameters = Params
        self.Struct["Escritura"]["Consumo"] = self.Parameters["Consumo"]
        self.Struct["Escritura"]["Intensidad_Actual"] = self.Parameters["Intensidad_Actual"]
        firebase.patch("Dispositivos/Address", self.Struct)

    def ChangeRParameters(self, Params={}):
        self.Parameters = Params
        self.Struct["Lectura"]["Intensidad_Deseada"] = self.Parameters["Intensidad_Deseada"]


class SlVentiladores(Slave):
    def __init__(self, Address):
        super().__init__(Address, "Ventiladores")
        self.Parameters = {}
        self.Struct = {Cant_Slaves: Structure["Ventiladores"]}
        firebase.patch("Dispositivos/Address", self.Struct)

    def ChangeWParameters(self, Params={}):
        self.Parameters = Params
        self.Struct["Escritura"]["Consumo"] = self.Parameters["Consumo"]
        self.Struct["Escritura"]["Temp_Actual"] = self.Parameters["Temp_Actual"]
        firebase.patch("Dispositivos/Address", self.Struct)

    def ChangeRParameters(self, Params={}):
        self.Parameters = Params
        self.Struct["Lectura"]["Temp_Deseada"] = self.Parameters["Temp_Deseada"]


Config()
with open('./Structure.json') as file_object:
    Structure = json.load(file_object)

while 1:
    if Button.value() == 1:
        Cant_Slaves += 1
        print('Botón activado, Creando al esclavo {}'.format(Cant_Slaves))
        if Cant_Slaves / 2 == round(Cant_Slaves / 2, 0):
            Type = "Luces"
        else:
            Type = "Ventiladores"
        CreateSlave(Type)

