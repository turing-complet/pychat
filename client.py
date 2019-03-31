import click
import socket
from libchat import ChatSocket, Message

def prompt(username):
    return f'[{username}]> '


@click.command()
@click.option('--server', '-s', default='localhost')
@click.option('--username', default=None)
def chat(server, username):
    
    print('Connecting to server..')
    sock = ChatSocket()
    sock.connect(server, 8080)

#     sock.mysend(Message(username, b'/join'))

    while True:
        msg = input(prompt(username)).encode()
        sock.mysend(msg)
        
        resp = sock.myreceive()
        print(f'Received {resp}')
        

if __name__=='__main__':
    chat()
