import socket
import tqdm
import os
import requests
import argparse
import time
import shutil
import platform
import button
from inputimeout import inputimeout

SERVER_PORT = 5001
BUFFER_SIZE = 1024*4
SEPARATOR = "<>"
user = "th00r"

windows = "\\"
linux = "/"
barra = ""

if platform.system() == "Windows":
    barra = windows
else:
    barra = linux

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
        self.is_dir = os.path.isdir(file_path+barra+file_name)
        self.size = os.path.getsize(file_path+barra+file_name)

def get_current_ipv6():

    hostname = socket.gethostname()
    ipv6 = socket.getaddrinfo(hostname,None, socket.AF_INET6)[0][4][0]
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}IPV6: {ipv6}{bcolors.ENDC}")
    return ipv6


def dir_walk(path,osfiles, total_size):
    if os.path.isdir(path):
        for file_name in os.listdir(path):
            if file_name[0] != ".":
                print(file_name)
                stfile=files(file_name,path)
                osfiles.append(stfile)
                path2 = path+barra+file_name
                if stfile.is_dir == True:
                    print("-->",end='')
                    dir_walk(path2,osfiles,total_size)
                else:
                    total_size = total_size+os.path.getsize(path2)
    else:
        osfiles.append(files(path,"."))

def receiv():
    host = get_current_ipv6()
    port = SERVER_PORT

    #Create socket server
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    #Bind de socket to ipv6 address
    s.bind((host,port))
    #Listen port
    s.listen(20)
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}[*] Listening as {host}{port}{bcolors.ENDC}")
    #Accept connection
    client_socket, address = s.accept()
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}[+] {address} is connected{bcolors.ENDC}")

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
        file_name = os.path.basename(file_name)
        file_size = int(file_size)
        is_dir = is_dir == 'True'
        if is_dir:
            os.makedirs(local_path + barra + parent_path + barra + file_path + barra + file_name)
        else:
            progress2 = tqdm.tqdm(range(file_size),f"Receiving {file_name}",unit="B",unit_scale=True,unit_divisor=1024)
            print(f"{bcolors.BOLD}{bcolors.OKGREEN}open = {local_path}/{parent_path}/{file_path}/{file_name}{bcolors.ENDC}")
            f = open(local_path + barra + parent_path + barra + file_path + barra +file_name,"wb")
            size = 0
            while size < file_size:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                size=size+len(bytes_read)
                if not bytes_read:
                    # Finished receiving bytes from file
                    break
                f.write(bytes_read)
                progress2.update(len(bytes_read))
            f.close()
        files_count = files_count+1
    
    client_socket.close()
    s.close()
    f.close()
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}Transfer Finished{bcolors.ENDC}")

def send_file(file_name,filepath,host,port):
    osfiles = []
    osfiles.append(files(file_name,filepath))
    total_size = 0
    dir_walk(filepath+file_name,osfiles, total_size)
    total_size = os.path.getsize(filepath+file_name)
    # Create de cliente socket
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}[+] Connecting to {host}:{port}")
    s.connect((host,port))
    print("[+] Connected")
    #First send total files, and total size to be send
    s.send(f"{len(osfiles)}{SEPARATOR}{total_size}".encode())
    time.sleep(1)
    # Start sending all files and directories
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}")
    while len(osfiles) > 0:
        file_to_send = osfiles.pop(0)
        s.send(f"{file_to_send.name}{SEPARATOR}{file_to_send.path.split(filepath)[1]}{SEPARATOR}{file_to_send.size}{SEPARATOR}{file_to_send.is_dir}".encode())
        time.sleep(1)
        if file_to_send.is_dir == False:
            progress = tqdm.tqdm(range(file_to_send.size),f"Sending {file_to_send.name}",unit="B",unit_scale=True,unit_divisor=1024)
            f = open(file_to_send.path+barra+file_to_send.name,"rb")
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                progress.update(len(bytes_read))
            time.sleep(1)
            f.close()

    # Close the socket
    s.close()
    print(f"Transfer Finished{bcolors.ENDC}")

def server_communication():
    server_host = "144.22.184.24"
    server_port = 51337
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}[*] Connecting to {server_host}:{server_port}{bcolors.ENDC}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.connect((server_host,server_port))
    msend = user+SEPARATOR+get_current_ipv6()
    s.send(msend.encode())
    mrecv = s.recv(BUFFER_SIZE).decode()
    print(mrecv)
    s.close()




def main():
    server_communication()
    menu = 99
    while menu == 99:
        os.system("clear")
        osfiles = []
        print(f"{bcolors.BOLD}{bcolors.OKGREEN}")
        print("\033[1m\033[91m----===== Programa de compartilhamento de arquivos =====----\033[0m")
        print("\033[1m\033[91m--------------------\033[0m")
        print("\033[1m\033[91m|0- Exit         |\033[0m")
        print("\033[1m\033[91m|1- Send File    |\033[0m")
        print("\033[1m\033[91m|2- Receive File |\033[0m")
        print("\033[1m\033[91m--------------------\n\033[0m")
        print("Digite o valor da função que deseja: ",end='')

        try:
            menu = inputimeout(prompt="", timeout=2)
        except Exception:
            menu = 99

        print(f"{bcolors.ENDC}")
        menu = int(menu)

        if(menu == 1):
            filepath = button.select_file_or_folder()
            if platform.system() == "Windows":
                filepath.strip("\\")
                filepath=filepath.replace("/",barra)
            print(filepath)
            sep = filepath.split(barra)
            filename = sep[len(sep)-1]
            filepath = filepath.strip(filename)
            print(f"Filepath: {filepath}  filename: {filename}")
            host = input("Endereço ipv6 do host")
            port = SERVER_PORT
            send_file(filename,filepath, host, port)
        if(menu == 2):
            receiv()


if __name__ == "__main__":
    main()