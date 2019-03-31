import click
import socket
from libchat import ChatSocket, Message, ClientHandler

def prompt(username):
    return f'[{username}]> '


commands = ['/chat', '/leave', '/help']
port = 8081

@click.command()
@click.option('--server', '-s', default='localhost')
@click.option('--username', default=None)
def chat(server, username):
    
    print('Connecting to server..')
    sock = ChatSocket()
    sock.connect(server, port)
    ClientHandler(handle_send(username, sock))
    ClientHandler(handle_recv(sock))


def handle_recv(sock):
    def _recv_loop():
        msgbytes = sock.myreceive()
        msg = Message.from_bytes(msgbytes)
        print(f'{prompt(msg.from_user)} {msg.body}')
    return _recv_loop


def handle_send(username, sock):
    def _send_loop():
        while True:
            text = input(prompt(username))
            msg = build_message(username, text)
            sock.mysend(msg.as_bytes())
    return _send_loop


def build_message(username, user_input):
    parts = user_input.split(' ')
    if parts[0] in commands:
        return Message(from_user=username, command=parts[0], body=parts[1])
    else:
        return Message(from_user=username, body=user_input)


if __name__=='__main__':
    chat()
