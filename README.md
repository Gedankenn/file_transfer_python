# File Transfer in python using ipv6

This is a simple file transfer program using ipv6 in python. The program uses the socket module to create a connection between the server and the client. The server sends the file to the client using the sendfile() function and the client receives the file using the recv() function embedded in the mainfile.

## Usage
clone this repo 
```bash
git clone git@github.com/Gedankenn/file_transfer_ipv6.git
```

Install the requirements
```bash
pip install -r requirements.txt
```

Run the program
```bash
python file_transfer.py [send] [filename] [ipv6 address]
python file_transfer.py [receive]
```

## Screenshots
![transfer](transfer.png)
