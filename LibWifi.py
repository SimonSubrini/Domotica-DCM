import network
import time as tm

uwlan = None


def connect_wifi(WIFI_SSID, WIFI_PW):
    global uwlan
    uwlan = network.WLAN(network.STA_IF)  # Using ESP8266 as station WiFi interface
    uwlan.active(True)
    if uwlan.isconnected():
        uwlan.disconnect()
    if not uwlan.isconnected():
        print("Tratando de conectar al Wifi: " + WIFI_SSID)
        uwlan.connect(WIFI_SSID, WIFI_PW)
        wifi_delay_counter = 0
        while not uwlan.isconnected():
            tm.sleep_ms(50)
            wifi_delay_counter = wifi_delay_counter + 1
            if wifi_delay_counter > 200:  # It's around 200*0.05 = 10 seconds and wifi is not connected yet!!
                # Better to exit
                print("Error, esta tardando demasiado...")
                return -1
        print("Conexión a la red " + WIFI_SSID + " exitosa")
        return 1


def check_if_all_OK(WIFI_SSID, WIFI_PW):
    global uwlan
    if uwlan is None or not uwlan.isconnected():
        print("Wifi desconectado, reconectando...")
        connect_wifi(WIFI_SSID, WIFI_PW)
        return -1
    else:
        print("Wifi conectado correctamente")
    return 1
