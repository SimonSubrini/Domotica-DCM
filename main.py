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


class Slave:
    def __init__(self):
        self.__Address = 0
        self.__Consumption = 0  # En KW/H
        self.__Type = ""

    def ChangeAddress(self, NewAddress):
        self.__Address = NewAddress
        return "New Address: {}".format(self.__Address)

    def ChangeType(self, NewType):
        self.__Type = NewType
        return "New Type: {}".format(self.__Type)

    def ChangeConsumption(self, NewConsumption):
        self.__Type = NewConsumption
        return "New Consumption: {}".format(self.__Consumption)


Config()
with open('./Structure.json') as file_object:
    Structure = json.load(file_object)
firebase.put("Dispositivos", Structure)

while 1:
    print('Estado boton: {}'.format(Button.value()))
    led.value(not led.value())
    time.sleep_ms(500)
