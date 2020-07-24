import socket



def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        conexion.bind(('192.168.1.1', 5000))
        conexion.listen()

        conn, addr = conexion.accept()

        with conn:
            print('Conectado a : ', addr)
            while True:
                data = conn.recv(1024)

                if not data:
                    break

                print(data)


if __name__ == "__main__":
    main()