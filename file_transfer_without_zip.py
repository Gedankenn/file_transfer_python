import socket
import tqdm
import os
import requests
import argparse
import time
import shutil

SERVER_PORT = 5001
BUFFER_SIZE = 1024*4
SEPARATOR = "<SEPARATOR>"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class files:
    name = ""
    is_dir = ""
    path = ""
    size = 0

    def __init__(self, file_name, file_path):
        self.name = file_name
        self.path = file_path
        self.is_dir = os.path.isdir(file_path+'\\'+file_name)
        self.size = os.path.getsize(file_path+"\\"+file_name)

def get_current_ipv6():

    """Get the current external IPv6 address or return None if no connection to the IPify service is possible"""
    try:
        return requests.get("https://api6.ipify.org", timeout=5).text
    except requests.exceptions.ConnectionError as ex:
        return "No IPv6 ENABLED"


def dir_walk(path,osfiles, total_size):
    total_size = 0
    for file_name in os.listdir(path):
        if file_name[0] != ".":
            # print(file_name)
            stfile=files(file_name,path)
            osfiles.append(stfile)
            path2 = path+"\\"+file_name
            if stfile.is_dir == True:
                # print("-->",end='')
                dir_walk(path2,osfiles,total_size)
            else:
                total_size = total_size+os.path.getsize(path2)

def receiv():
    host = get_current_ipv6()
    print("IPV6 = "+host)
    port = SERVER_PORT

    #Create socket server
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    #Bind de socket to ipv6 address
    s.bind((host,port))
    #Listen port
    s.listen(20)
    print(f"[*] Listening as {host}{port}")
    #Accept connection
    client_socket, address = s.accept()
    print(f"[+] {address} is connected")

    #receiv the total number os files and directories that will be transmited
    # send("{total_files}{SEPARATOR}{total_size}")
    received = client_socket.recv(BUFFER_SIZE).decode()
    # received = client_socket.recvfrom(BUFFER_SIZE)
    print(received.split(SEPARATOR))
    total_files, total_size = received.split(SEPARATOR)
    #remove absolute path if there is one
    total_size = int(total_size)
    total_files = int(total_files)

    parent_path = "Receiv"

    if os.path.exists(parent_path):
        shutil.rmtree(parent_path,ignore_errors=True)
    
    os.makedirs(parent_path)
    local_path = os.getcwd()
    files_count = 0
    while(files_count < total_files):
        received = client_socket.recv(BUFFER_SIZE).decode()
        file_name,file_path, file_size, is_dir = received.split(SEPARATOR)
        print(received.split(SEPARATOR))
        file_name = os.path.basename(file_name)
        file_size = int(file_size)
        is_dir = bool(is_dir)
        print(f"File name: {file_name}")
        print(f"File path: {file_path}")
        print(f"File size: {file_size}")
        print(f"Is dir: {is_dir}")
        if is_dir:
            # print(f"{local_path}\\{file_path}\\{parent_path}\\{file_name}")
            os.makedirs(local_path+ "\\" + parent_path+"\\" +file_name)
        else:
            progress2 = tqdm.tqdm(range(file_size),f"Receiving {file_name}",unit="B",unit_scale=True,unit_divisor=1024)
            f = open(local_path + "\\" + parent_path+"\\" +file_name,"wb")
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # Finished receiving bytes from file
                    break
                f.write(bytes_read)
                progress2.update(len(bytes_read))
            f.close()
    
    client_socket.close()
    s.close()
    f.close()

def send_file(file_name,host,port):
    osfiles = []
    # osfiles.append(files(file_name,os.getcwd()))
    total_size = 0
    dir_walk(file_name,osfiles, total_size)

    # Create de cliente socket
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host,port))
    print("[+] Connected")
    #First send total files, and total size to be send
    s.send(f"{len(osfiles)}{SEPARATOR}{total_size}".encode())
    time.sleep(1)
    # Start sending all files and directories
    while len(osfiles) > 0:
        file_to_send = osfiles.pop(0)
        s.send(f"{file_to_send.name}{SEPARATOR}{file_to_send.path}{SEPARATOR}{file_to_send.size}{SEPARATOR}{file_to_send.is_dir}".encode())
        time.sleep(1)
        if file_to_send.is_dir == False:
            progress = tqdm.tqdm(range(file_to_send.size),f"Sending {file_to_send.name}",unit="B",unit_scale=True,unit_divisor=1024)
            f = open(file_to_send.path+"\\"+file_to_send.name,"rb")
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                progress.update(len(bytes_read))

            f.close()

    # Close the socket
    s.close()




def main():
    osfiles = []

    print("\033[1m\033[91m----===== Programa de compartilhamento de arquivos =====----\033[0m")
    print("\033[1m\033[91m--------------------\033[0m")
    print("\033[1m\033[91m|1- Enviar arquivo |\033[0m")
    print("\033[1m\033[91m|2- Receber arquivo|\033[0m")
    print("\033[1m\033[91m--------------------\n\033[0m")
    menu = input("Digite o valor da função que deseja: \n")
    menu = int(menu)

    if(menu == 1):
        filename = input("Nome do arquivo \n")
        host = input("Endereço ipv6 do host")
        port = SERVER_PORT
        send_file(filename, host, port)
    if(menu == 2):
        receiv()


if __name__ == "__main__":
    main()