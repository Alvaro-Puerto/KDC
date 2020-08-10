import socket
import json
import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad, pad
from base64 import b64encode, b64decode
from termcolor import colored, cprint


from _thread import *


CLIENTE_KEY = b'?@\xf2\x86\xccB\xdb\xf3\xba\xaf\x0f%w\x9fk\x9c' ########## IMPORTANTE ############
                                                                # El kdc debe de conocer todas las claves de los cliente
                                                                # ya que con esa misma debera encriptar el mensaje que devolvera
                                                                # el TGT con las nuevas claves generadas 
                                                                # METODO USADO POR ENSEÑANZA, NO GENERA CONFIDENCIALIDAD U PRIVACIDAD
                                                                # DE LAS CLAVES NI EFICIENCIA,  NUNCA PROGRAMARLAS DE ESTA FORMA !!!! 

SERVER_HOST = [
    ['127.0.0.1:5001', b"ci\x9d\xec\xabU\xc0'\xd2\xc9\xe8\xb8\xea\x02R\x1f"],
    #INSERTAR MAS HOST EN FORMA DE LISTA
]

def buscar(ip_destino): 
    """Funcion que busca el SERVER a comunicar"""
    for elementos in SERVER_HOST:
        if elementos[0] == ip_destino:
            return elementos
    return False


def decifrando_peticion(data):
    data = data.decode() 
    data = json.loads(data)
    iv = b64decode(data['iv'])
    body = b64decode(data['body'])

    try:
        bloque = AES.new(CLIENTE_KEY, AES.MODE_CBC, iv)
        json_decrypt = unpad(bloque.decrypt(body),AES.block_size)
        
        json_decrypt = json_decrypt.decode()
        json_decrypt = json.loads(json_decrypt)
        ip_destino = json_decrypt['ip']
        nonce = json_decrypt['nonce']
                                            ############# IMPORTANTE #################
        key_kdc = get_random_bytes(16)      # GENERANDO CLAVE KDC ALEATORIA DE 16 BITS

        destino = buscar(ip_destino) # Verifica si el destino existe

        if destino:
            key_destino = destino[1]
            
            key_kdc = b64encode(key_kdc).decode()

            body_destino = json.dumps({'key':key_kdc, 'nonce':nonce}) # GENERANDO CUERPO DE MENSAJES
            nuevo_bloque = AES.new(key_destino, AES.MODE_CBC) #Bloque cifrado para destino
            decrypt = nuevo_bloque.encrypt(pad(body_destino.encode(), AES.block_size))

            decrypt = b64encode(decrypt).decode()
            iv = b64encode(nuevo_bloque.iv).decode()
            json_destino = json.dumps({'iv':iv, 'body':decrypt}) # mensaje del destino terminado

            body_destino = json.dumps({'key':key_kdc, 'nonce':nonce, 'ip':destino[0]})
            bloque_request = AES.new(CLIENTE_KEY, AES.MODE_CBC) #Bloque cifrado para el cliente
            encrypt = bloque_request.encrypt(pad(body_destino.encode(), AES.block_size))

            iv = b64encode(bloque_request.iv).decode()
            body = b64encode(encrypt).decode()
            json_request = json.dumps({'iv':iv, 'body': body, }) # Cuerpo del mensaje terminado

            json_response = json.dumps({'request':json_request, 'destino':json_destino})# mensaje del solicitante terminado

            return json_response.encode()

        else: # Si no encuentra el destino 
            return b'404'

    except Exception as e: # Si existe algun error, cambiar a pass si no desea verlo
        #pass
        print('error tipo ', e)


def hilos_clientes(cliente,addrs):  # HILO
    cliente.send('Conectando con KDC '.encode())
    while True:
        try:
            data = cliente.recv(1024)
            if not data :
                break
            addrs_color = colored('{}'.format(addrs), 'green')
            print('Se ha iniciado una conexion con  ', addrs_color )
            cliente.sendall(decifrando_peticion(data))
            break

        except ConnectionResetError:
            print('Conexion reiniciada ')

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:  # Iniciando conexion
        conexion.bind(('', 5000)) # IP variable, cambiar por la ip de su maquina
        conexion.listen()
        while True:
            cliente , addrs = conexion.accept()
            start_new_thread(hilos_clientes,(cliente, addrs)) # Iniciando el hilo
        conexion.close()


if __name__ == "__main__":
    main()
