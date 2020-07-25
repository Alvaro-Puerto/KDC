import socket
import json
import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad, pad

from _thread import *


def decifrando_peticion(data):
    


def hilos_clientes(cliente,addrs):
    cliente.send('Conectando con KDC '.encode())
    while True:
        try:
            data = cliente.recv(1024)
            if not data :
                break

            print('Se ha iniciado una conexion con  ',addrs )
            cliente.sendall('response'.encode())
            decifrando_peticion(data)

            break
        except ConnectionResetError:
            print('Conexion reiniciada ')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        conexion.bind(('', 5000))
        conexion.listen()

        while True:
            cliente , addrs = conexion.accept()
            
            start_new_thread(hilos_clientes,(cliente, addrs))
        
        conexion.close()

if __name__ == "__main__":
    main()
    