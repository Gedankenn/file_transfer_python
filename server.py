import socket

def receiv():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host = "144.22.184.24"
    host = "10.0.0.103"
    port = 51337
    print("host: ", host)
    print("port: ", port)
    s.bind((host, port))
    s.listen(60)
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        c.send('Thank you for connecting'.encode())
        c.close()
        break

def main():
    receiv()

if __name__ == "__main__":
    main()
