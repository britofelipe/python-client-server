import socket
import threading

entry = ''
while(entry != "/JOIN"):
    entry = input("Please write /JOIN to enter the chat: ")
    if(entry == "/JOIN"):
        break

host = '127.0.0.1'
port = 55122

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

nickname = input("Enter a nickname to start talking: ")
stop_thread = False
prompt = True

def receive():
    global nickname
    global prompt
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif message.startswith('NICKNAME CHANGED TO '):
                new_nick = message[len('NICKNAME CHANGED TO '):].strip('| ')
                nickname = new_nick
                print(f"Your nickname has been changed to {new_nick}")
                prompt = True
            elif message == 'EXITING':
                print("You have left the chat.")
                client.close()
                break
            elif message == 'REFUSE SIZE':
                print('Connection refused, too many users on the server.')
                client.close()
                break
            elif message == 'REFUSE NICK':
                print('Connection refused, nickname is already in use.')
                client.close()
                break
            else:
                print(message)
                prompt = True
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

def write():
    global nickname
    global prompt
    while True:
        if stop_thread:
            client.close()
            break

        if prompt:
            text = input("-- ")
        else:
            text = input()

        if text == '/JOIN':
            prompt = False
            message = '/JOIN'
            client.send(message.encode('utf-8'))
        elif text.startswith('/NICK'):
            prompt = False
            client.send(text.encode('utf-8'))
        elif text == '/USERS':
            prompt = False
            message = '/USERS'
            client.send(message.encode('utf-8'))
        elif text == '/EXIT':
            try:
                prompt = False
                client.send(text.encode('utf-8'))
                break
            except:
                print('ERROR: Connection went wrong')
        else:
            prompt = True
            message = f'{nickname}: {text}'
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()