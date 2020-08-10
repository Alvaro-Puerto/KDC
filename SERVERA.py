import socket
import json
import os
import datetime

from termcolor import colored
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from _thread import *


######################################
#                                    #
# CLAVE PRIVADA DEL SERVER linea 19  #
#                                    #
######################################

KEY = b"ci\x9d\xec\xabU\xc0'\xd2\xc9\xe8\xb8\xea\x02R\x1f" #Clave privada del server 16 bits

def time_color():
    tiempo_actual = datetime.datetime.now()
    tiempo_recibido_color = colored('{}:{}'.format(tiempo_actual.hour, tiempo_actual.minute), 'blue', attrs=['bold'])
    return tiempo_recibido_color


class Conexion(): 
    """Objecto que nos servira para cifrar y descrifar los mensajes"""

    def __init__(self, key, nonce):
        self.kdc_key = key #Clave generada por el KDC
        self.nonce = nonce #Nonce o numero de sesion 

    def cifrando(self, mensaje ):
        bloque = AES.new(self.kdc_key, AES.MODE_CBC) #Bloques de cifrado
        cifrado = bloque.encrypt(pad(mensaje.encode(), AES.block_size))

        iv = b64encode(bloque.iv).decode()
        body = b64encode(cifrado).decode()

        return json.dumps({'iv':iv, 'body':body}).encode()

    def descifranod(self, mensaje):
        mensaje = mensaje.decode()
        data = json.loads(mensaje)
        iv = b64decode(data['iv'])
        body = b64decode(data['body'])
        bloque = AES.new(self.kdc_key, AES.MODE_CBC, iv) #Bloque de decifrado con relleno
        mensaje = unpad(bloque.decrypt(body), AES.block_size)
        tiempo_recibido = datetime.datetime.now()
        tiempo_color = time_color()
        print('{} Recibido -> {}  '.format(tiempo_color,mensaje.decode()))
    

def descifrando_peticiones(data):
    """Funcion de descrifra los mensajes con la clave del Server
    """
    data = data.decode()
    data = json.loads(data)
    iv = b64decode(data['iv'])
    body = b64decode(data['body'])

    bloque = AES.new(KEY, AES.MODE_CBC, iv) #Notese que el bloque de cifrado es 
    mensaje = unpad(bloque.decrypt(body), AES.block_size)#con la clave del server 

    mensaje = json.loads(mensaje.decode())
    key = b64decode(mensaje['key']) # Clave del kdc descifrada
    nonce = mensaje['nonce'] # Numero de sesion

    enlace = Conexion(key, nonce) # Creacion de la instacia del objeto 
    
    return enlace

if __name__ == "__main__":
    print('INICIANDO SERVIDOR ')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion: # Inicio del conexion 
        conexion.bind(('', 5001)) # Parametro variable, dentro de las  '' puede colocar las ip
        conexion.listen()         #correspondiente de la maquina 

        cliente, addrs = conexion.accept()
        while True:
            data = cliente.recv(1024)

            if not data:
                break
            try:
                enlace = descifrando_peticiones(data) 
                cliente.sendall(enlace.cifrando('OK ACEPTO LA CONEXION'))
            except Exception as e:
                enlace.descifranod(data)
                tiempo_color = time_color()
                print('{} Enviando -> : '.format(tiempo_color), end="")
                mensaje = input()
                cliente.sendall(enlace.cifrando(mensaje)) # Enviando mensaje
                
                