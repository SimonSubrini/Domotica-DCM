import time
import json
from machine import Pin, SPI
from LibNrf24l01 import NRF24
import LibWifi
import ufirebase as firebase

# Configuración de pines
led = Pin(2, Pin.OUT)
Button = Pin(16, Pin.IN)
ce_pin = Pin(4, Pin.OUT)  # Pin CE, debe estar conectado al pin CE del módulo NRF24L01.
csn_pin = Pin(5, Pin.OUT)  # Pin CSN, debe estar conectado al pin CSN del módulo NRF24L01.

# Inicialización de variables
ListSlaves = []
nrf24Module = []


def config():
    init_wifi()
    init_firebase()


# Inicialización de la radio NRF24L01
def init_nrf24l01():
    spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
    nrf = NRF24(Pin(4, Pin.OUT), spi)
    nrf.open_tx_pipe(b'\x01\x02\x03\x04\x05')
    nrf.open_rx_pipe(1, b'\x01\x02\x03\x04\x05')
    nrf.start_listening()
    return nrf


# Inicialización de la conexión Wi-Fi
def init_wifi():
    with open('./Wifi_Pass.txt', 'rt', encoding='utf-8') as file:
        Wifi_Pass = file.read()
    Redes = Wifi_Pass.split('\r\n\r\n')
    for red in Redes:
        WIFI_SSID = red.split('"')[1]
        WIFI_PW = red.split('"')[3]
        if LibWifi.connect_wifi(WIFI_SSID, WIFI_PW) == 1:
            break


def init_firebase():
    with open('./Firebase_Pass.txt', 'rt', encoding='utf-8') as file:
        FireBase_Pass = file.read()
    Firebase_ID = FireBase_Pass.split('"')[1]
    Firebase_Auth = FireBase_Pass.split('"')[3]
    firebase.setURL("https://" + Firebase_ID + ".firebaseio.com/")


def CreateSlave(Type):
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


# Main

config()
nrf = init_nrf24l01()

with open('./Structure.json') as file_object:
    Structure = json.load(file_object)
Cant_Slaves = 0

while True:
    for i in range(5): # testeo de nrf24l01 y firebase
        message = b'Hello123'
        nrf.send(message)
        print("Mensaje enviado:", message)
        if Button.value() == 1:
            Cant_Slaves += 1
            print('\nBotón activado, Creando al esclavo {}'.format(Cant_Slaves))
            if Cant_Slaves / 2 == round(Cant_Slaves / 2, 0):
                Type = "Luces"
            else:
                Type = "Ventiladores"
            CreateSlave(Type)
    break
