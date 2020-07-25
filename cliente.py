import socket
import os
import random
import json

from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes



KEY = b'?@\xf2\x86\xccB\xdb\xf3\xba\xaf\x0f%w\x9fk\x9c'

def borrar_pantalla():
    os.system("clear")

def conectando_kdc(json_request):
    json_request = json_request

    #CREANDO SOCKET
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as kdc_conexion:
        kdc_conexion.connect(('', 5000))
        while True:
            kdc_conexion.sendall(json_request.encode())
            data = kdc_conexion.recv(1024)
            if not data :
                break
            try:
                print(json.loads(data.decode()))
                break
            except Exception as e:
                print(data.decode())

            break
        kdc_conexion.close()
        input()


def cifrando_mensaje(ip_destino):
    ip_destino = ip_destino
    nonce = random.randint(1,10000)

    body = json.dumps({
        'ip' : ip_destino,
        'nonce': nonce
    })
    
    bloque = AES.new(KEY, AES.MODE_CBC)
    
    cripto = bloque.encrypt(pad(body.encode(), AES.block_size))
    iv = b64encode(bloque.iv).decode()
    body = b64encode(cripto).decode()

    json_request = json.dumps({'iv':iv, 'body':body})
    conectando_kdc(json_request)


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
            if op == 2:
                try:
                    ip_destino = input('Ingrese el ip del servidor a entablar conexion ')
                    cifrando_mensaje(ip_destino) # Funcion que crea un socket entre KDC y el cliente 

                except Exception as e:
                    input()
                    borrar_pantalla()
                    print('Error datos invalidos :', ip_destino)
                    print(e)
                    input()

            elif op == 1:
                break
            else:
                print('Opcion invalida')
        
        except Exception as e:
            print('Debe ingresar una opcion')
            input()



if __name__ == "__main__":
    main()