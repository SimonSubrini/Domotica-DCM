import time
import json
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
Slaves = []


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


def CreateSlave(Slaves):
    if len(Slaves) == 0:
        Slaves = [Slave(Cant_Slaves, Type)]
    else:
        Slaves.append(Slave(Cant_Slaves, Type))


class Slave:
    def __init__(self, Address=0, Type=""):
        self.__Address = Address
        self.__Type = Type
        self.__Consumption = 0  # En KW/
        print('Nuevo esclavo creado\n'
              'Dirección: {}\n'
              'Tipo: {}'.format(self.__Address, self.__Type))
        if Type == "Luces":
            Struct = {Cant_Slaves: Structure["Luces"]}
        elif Type == "Ventiladores":
            Struct = {Cant_Slaves: Structure["Ventiladores"]}
        firebase.patch("Dispositivos/Address", Struct)

    def ChangeConsumption(self, NewConsumption):
        self.__Consumption = NewConsumption
        return "New Consumption: {}".format(self.__Consumption)

    def ReadAddress(self):
        return self.__Address

    def ReadType(self):
        return self.__Type

    def ReadConsumption(self):
        return self.__Consumption


Config()
with open('./Structure.json') as file_object:
    Structure = json.load(file_object)

while 1:
    if Button.value() == 1:
        Cant_Slaves += 1
        print('Boton activado, Creando al escavo {}'.format(Cant_Slaves))
        if Cant_Slaves / 2 == round(Cant_Slaves / 2, 0):
            Type = "Luces"
        else:
            Type = "Ventiladores"
        CreateSlave(Slaves)

    led.value(not led.value())
    time.sleep_ms(500)
