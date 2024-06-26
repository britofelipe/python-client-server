import threading
import socket

HOST = '127.0.0.1'
PORT = 55122
MAX_USERS = 4

server = socket.socket(socket.AF_INET)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message, sender):
    if not isinstance(message, str):
        message = str(message, 'utf-8')
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error in sending message: {e}")
                close_client(client)

def already_joined(client):
    client.send("You are already in the server! Did you mean '/EXIT'?".encode('utf-8'))

def send_users(client):
    users = 'Connected users: ' + ', '.join(nicknames)
    client.send(users.encode('utf-8'))

def close_client(client):
    message = 'EXITING'
    client.send(message.encode('utf-8'))
    index = clients.index(client)
    clients.remove(client)
    client.close()
    nickname = nicknames[index]
    broadcast(f'{nickname} left the chat'.encode('utf-8'), client)
    nicknames.remove(nickname)

def accept_or_refuse_client(client, nickname):
    if len(clients) >= MAX_USERS:
        client.send("REFUSE SIZE".encode('utf-8'))
        client.close()
        return False
    elif nickname in nicknames:
        client.send("REFUSE NICK".encode('utf-8'))
        client.close()
        return False
    else:
        clients.append(client)
        nicknames.append(nickname)
        broadcast(f'{nickname} joined the chat|'.encode('utf-8'), client)
        return True

def change_nick(client, new_nick):
    if new_nick in nicknames:
        client.send('NICKNAME IN USE|'.encode('utf-8'))
        return

    index = clients.index(client)
    old_nick = nicknames[index]
    nicknames[index] = new_nick
    notification = f'NICKNAME CHANGED TO {new_nick}|'
    client.send(notification.encode('utf-8'))
    broadcast(f'{old_nick} changed their nickname to {new_nick}|', client)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if(message == '/JOIN'):
                already_joined(client)
            elif message == '/USERS':
                send_users(client)
            elif (message.startswith('/NICK')):
                try:
                    new_nick = message.split()[1]
                    change_nick(client, new_nick)
                except Exception as e:
                    print(f"Error in changing client nick: {e}")
            elif (message == '/EXIT'):
                try:
                    close_client(client)
                    break
                except Exception as e:
                    print(f"Error in exiting client: {e}")
            else:
                broadcast(message, client)
        except Exception as e:
            print(f"Error in handling client: {e}")
            close_client(client)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        if accept_or_refuse_client(client, nickname):
            print(f'Nickname of the client is {nickname}')
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

print(f"Server is listening at port {PORT}")
receive()