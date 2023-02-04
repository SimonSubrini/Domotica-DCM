import machine
from machine import Pin
import nrf24


def initNrf24(ce_pin, csn_pin, address, channel=0, payload_size=8):
    """
    Inicializa el objeto NRF24L01 y configura los parámetros de comunicación
    """
    spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0)

    # Configurar los pines CE y CSN del NRF24L01
    ce = Pin(ce_pin, Pin.OUT)
    csn = Pin(csn_pin, Pin.OUT)

    # Inicializar el objeto NRF24L01
    radio = nrf24.NRF24(spi, csn, ce, radio_address=address)
    radio.begin(channel, payload_size)
    radio.set_speed_power(nrf24.NRF24.SPEED_1MBPS, nrf24.NRF24.POWER_0DBM)
    return radio


def sendData(radio, data, destAddress):
    """
    Envía un paquete de datos a un dispositivo con la dirección especificada
    """
    radio.send(data, destAddress)


def receiveData(radio):
    """
    Recibe un paquete de datos enviado por un dispositivo
    """
    return radio.recv()

#
# # Inicializar el objeto NRF24L01
#
#
# # Enviar un paquete de datos
# data = b'Hola Mundo'
# sendData(nrf24Module, data, b'simon')
#
# # Recibir un paquete de datos
# receivedData = receiveData(nrf24Module)
# print(receivedData)
