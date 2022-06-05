import time
import json
from machine import Pin
import LibWifi
import Functions
import ufirebase as firebase

# Inicialización de variables
led = Pin(2, Pin.OUT)


def Config():
    for i in range(5):
        led.value(False)
        time.sleep_ms(150)
        led.value(not led.value())
    Functions.Prints()
    ConnectWifi()
    ConnectFirebase()


def ConnectWifi():
    with open('./Wifi_Pass.txt', 'rt', encoding='utf-8') as file_object:
        Wifi_Pass = file_object.read()
    Redes = Wifi_Pass.split('\r\n\r\n')
    for i in range(5):
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

    # firebase.put('Bool', False)
    # firebase.put('Str', 'Simon')
    # firebase.put('Int', 18)
    # firebase.put('Float', 10.25)
    # firebase.put('Strs', 'Hola')


Config()
while 1:
    with open('./Structure.json') as file_object:
        Structure = json.load(file_object)
    firebase.put("Dispositivos", Structure)
