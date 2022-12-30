"""
Server receiver of the file
"""
import socket
import tqdm
import os
import requests
import argparse
from zipfile import ZipFile
from os.path import basename

port = 5001

def get_current_ipv6():

    """Get the current external IPv6 address or return None if no connection to the IPify service is possible"""
    try:
        return requests.get("https://api6.ipify.org", timeout=5).text
    except requests.exceptions.ConnectionError as ex:
        return None

def receiv():
    # device's IP address
    SERVER_HOST = get_current_ipv6()
    SERVER_PORT = port

    ### Printa na tela o endereco ip para poder ser copiado
    print(SERVER_HOST)

    # receive 4096 bytes each time
    BUFFER_SIZE = 1024 * 4 #4KB
    SEPARATOR = "<SEPARATOR>"
    # create the server socket
    # TCP socket

    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)

    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    s.listen(5)

    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")

    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open("unzip.zip", "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()
    f.close()

    with ZipFile("unzip.zip", 'r') as file:
        print('Extracting all files...')
        file.extractall(filename)
        print('Done!') # check your directory of zip file to see the extracted files\

    os.remove("unzip.zip")


def send_file(filename, host, port):
    # get the file size
    BUFFER_SIZE = 1024 * 4 #4KB
    SEPARATOR = "<SEPARATOR>"
    filesize = os.path.getsize(filename)
    # create the client socket
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")

    #Create a zip file
    with ZipFile('send.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        dirName = filename
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename_zip in filenames:
                #create complete filepath of file in directory
                filePath = os.path.join(folderName, filename_zip)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))

    # send the filename and filesize
    filesize = os.path.getsize("send.zip")
    s.send(f"{dirName}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open("send.zip", "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    os.remove("send.zip")

    # close the socket
    s.close()

if __name__ == "__main__":
    print("\033[1m\033[91m----===== Programa de compartilhamento de arquivos =====----\033[0m")
    print("\033[1m\033[91m--------------------\033[0m")
    print("\033[1m\033[91m|1- Enviar arquivo |\033[0m")
    print("\033[1m\033[91m|2- Receber arquivo|\033[0m")
    print("\033[1m\033[91m--------------------\n\033[0m")
    menu = input("Digite o valor da função que deseja: \n")
    menu = int(menu)

    if(menu == 1):
#        import argparse
#        parser = argparse.ArgumentParser(description="Simple File Sender")
#        parser.add_argument("file", help="File name to send")
#        parser.add_argument("host", help="The host/IP address of the receiver")
#        parser.add_argument("-p", "--port", help="Port to use, default is 5001", default=5001)
#        args = parser.parse_args()
#        filename = args.file
#        host = args.host
#        port = args.port
        filename = input("Nome do arquivo \n")
        host = input("Endereço ipv6 do host")

        send_file(filename, host, port)
    if(menu == 2):
        receiv()