import socket
import os
import random
import json
import datetime

from termcolor import colored
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

KEY = b'?@\xf2\x86\xccB\xdb\xf3\xba\xaf\x0f%w\x9fk\x9c' # CLAVE DEL CLIENTE

KEY_TEMPO = '' # CLAVE TEMPORALES DEL KDC
NONCE_TEMPO = ''

def borrar_pantalla():
    os.system("clear")

def time_color():
    tiempo_actual = datetime.datetime.now()
    tiempo_recibido_color = colored('{}:{}'.format(tiempo_actual.hour, tiempo_actual.minute), 'blue', attrs=['bold'])
    return tiempo_recibido_color


def cifrado_descifrado(mensaje, KEY_TEMPO):
    """
    Funcion usada para cifrar y descifrar mensajes 
    """
    mensaje = mensaje.decode()
    data = json.loads(mensaje)
    iv = b64decode(data['iv']) #IV es el relleno usado en  AES
    body = b64decode(data['body'])
    try:
        bloque = AES.new(KEY_TEMPO, AES.MODE_CBC, iv) #Blpque descifrado
        mensaje_descifrado = unpad(bloque.decrypt(body), AES.block_size)
    except Exception as e:
        print(e)
    tiempo_color = time_color()
    print('{} Recibido -> {}'.format(tiempo_color, mensaje_descifrado.decode()))

    while True:
        tiempo_color = time_color()
        mensaje_nuevo = input('{} Enviando -> '.format(tiempo_color))
        
        if mensaje_nuevo:
            bloque_cifrado = AES.new(KEY_TEMPO, AES.MODE_CBC)
            try:
                mensaje_cifrado = bloque_cifrado.encrypt(pad(mensaje_nuevo.encode(), AES.block_size)) # Bloque cifrado

                iv_c = b64encode(bloque_cifrado.iv).decode() ############# IMPORTANTE ###################
                body = b64encode(mensaje_cifrado).decode()   # Sintaxis usada para convertir los bytes generado a strings
                mensaje = json.dumps({'iv': iv_c, 'body':body})

                return mensaje.encode()
            except Exception as e:
                print(e)
        else:
            print('No ha escrito ningun mensaje: Desea cerrar la conexion Y OR N (dejar blanco es igual a N)')
            op = input()
            if op == 'Y':
                continue
            else:
                return b'CLOSE'


def conexion_privada(mensaje, destino):
    mensaje = mensaje.decode()
    estructura = json.loads(mensaje)
    ip = estructura['ip']
    NONCE_TEMPO = estructura['nonce']
    KEY_TEMPO = b64decode(estructura['key']) 
    ip, host = ip.split(':') # SEPARANDO LA IP Y EL PUERTO DEL SERVER
    print('ENVIANDo')
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c_privada: # INICIANDO CONEXION CON EL SERVER
        c_privada.connect((ip, int(host)))
        c_privada.sendall(destino.encode()) # Enviando clave del KDC
        while True:
            data = c_privada.recv(1024) #Esperando respuesta del SERVER
            if not data:
                break
            if data.decode() == 'OK':
                print('ERROR')
                break
            else:
                c_privada.sendall(cifrado_descifrado(data,KEY_TEMPO)) # IMPORTANTE, mala practica
        c_privada.close()                                             # PUNTO A MEJORAR 
        

def descifrando_respuesta_kdc(data):
    respuesta = data['request']
    destino = data['destino']
    respuesta = json.loads(respuesta)

    iv = b64decode(respuesta['iv'])     ############### IMPORTANTE ################
    body = b64decode(respuesta['body']) # Sintaxis usada para convertir el texto en tipo byte
                                        #IMPORTANTE MENCIONAR DEBIDO QUE SE VERA MUCHAS VECES
    try:
        bloque = AES.new(KEY, AES.MODE_CBC, iv) # Bloque para descifrar 
        mensaje = unpad(bloque.decrypt(body),AES.block_size)
        conexion_privada(mensaje,destino)

    except Exception as e:
        print('Hubo un error en la decodificacion del mensaje del KDC')
        print(e)
        input()
    

def conectando_kdc(json_request):
    json_request = json_request
 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as kdc_conexion: #CREANDO SOCKET AL KDC !No confundir
        kdc_conexion.connect(('', 5000))
        kdc_conexion.sendall(json_request.encode())
        while True:
            data = kdc_conexion.recv(1024) # Esperando respuesta del KDC
            if not data :
                break
            try:
                data = json.loads(data.decode()) # Sintaxis usada para convertir un json a un dict
                descifrando_respuesta_kdc(data)
                kdc_conexion.close()
                break

            except Exception as e:
                if data == b'404':
                    print('DESTINO NO ENCONTRANDO O FUERA DE LINEA')
                    kdc_conexion.close()
                    break
                else:
                    print(data.decode())

        try:
            kdc_conexion.close()
        except Exception as e:
            pass



def cifrando_mensaje(ip_destino): 
    """
    Funcion que cifra el mensaje de peticion para el
    KDC
    """
    ip_destino = ip_destino
    nonce = random.randint(1,10000)

    body = json.dumps({
        'ip' : ip_destino,
        'nonce': nonce
    })
    
    bloque = AES.new(KEY, AES.MODE_CBC) # Cifrando bloque
    
    cripto = bloque.encrypt(pad(body.encode(), AES.block_size))
    iv = b64encode(bloque.iv).decode()
    body = b64encode(cripto).decode()

    json_request = json.dumps({'iv':iv, 'body':body})
    conectando_kdc(json_request) # Funcion socket


def main():
   
    while True:
        borrar_pantalla()
        print('+++++++++++ PROGRAMANDO UN KDC ++++++++')
        print('Selecciona una opcion ')
        print('1- Establecer una conexion ')
        print('2- Salir ')
        try:
            op = int(input())
            borrar_pantalla()
            if op == 1:
                try:
                    ip_destino = input('Ingrese el ip del servidor a entablar conexion ')
                    cifrando_mensaje(ip_destino) # Funcion que crea un socket entre KDC y el cliente 

                except Exception as e:
                    input()
                    borrar_pantalla()
                    print('Error datos invalidos :', ip_destino)
                    print(e)
                    input()

            elif op == 2:
                break
            else:
                print('Opcion invalida')
        
        except Exception as e:
            print('Debe ingresar una opcion')
            input()


if __name__ == "__main__":
    main()