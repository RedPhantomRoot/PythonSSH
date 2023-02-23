import paramiko

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        whoami = ssh_session.recv(1024).decode().strip()
        # print(ssh_session.recv(1024).decode())
        try:
            while True:
                command = input(f"{whoami}@ssh_server> ")
                if command == "exit":
                    ssh_session.send(command)
                    print("Exiting..")
                    ssh_session.close()
                    client.close()
                    break
                else:
                    ssh_session.send(command)
                    data_length = 1
                    response = ""
                    while data_length:
                        res = ssh_session.recv(4096)
                        data_length = len(res)
                        response += res.decode().strip()
                        if data_length < 4096:
                            break
                    if response:
                        print(response)
        except KeyboardInterrupt:
            client.close()
    return

if __name__ == '__main__':
    import getpass
    user = input('Username: ')
    password = getpass.getpass()

    ip = input('Enter server IP: ')
    port = input('Enter port: ')
    ssh_command(ip, port, user, password, 'ClientConnected')
