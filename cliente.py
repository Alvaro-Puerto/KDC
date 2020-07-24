import socket
import os


def borrar_pantalla():
    os.system("clear")

def conectando_kdc(*args):
    ip_destino = args

    #CREANDO SOCKET
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as kdc_conexion:
        kdc_conexion.connect(('192.168.1.1', 5000))
        kdc_conexion.sendall(b'Hola es mi primer mensaje')
        data = kdc_conexion.recv(1024)


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
                    conectando_kdc(ip_destino) # Funcion que crea un socket entre KDC y el cliente 

                except Exception as e:
                    borrar_pantalla()
                    print('Error datos invalidos :', ip_destino)
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