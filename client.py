import click
import socket
from libchat import ChatSocket, Message, ClientHandler

def prompt(username):
    return f'[{username}]> '


commands = ['/chat', '/leave', '/help', '/style']
port = 8080

@click.command()
@click.option('--server', '-s', default='localhost')
@click.option('--username', '-u')
def chat(server, username):
    
    print('Connecting to server..')
    sock = ChatSocket()
    sock.connect(server, port)
    ClientHandler(handle_send(username, sock))
    ClientHandler(handle_recv(sock))


def handle_recv(sock):
    def _get_message():
        msgbytes = sock.myreceive()
        msg = Message.from_bytes(msgbytes)
        click.secho(f'\n{prompt(msg.from_user)} {msg.body}\n', fg='green')
    return _get_message


def handle_send(username, sock):
    def _send():
        # text = input(prompt(username))
        text = click.prompt(click.style(prompt(username), fg='cyan'))
        if (text == ""):
            return
        msg = build_message(username, text)
        sock.mysend(msg.as_bytes())
    return _send


def build_message(username, user_input):
    parts = user_input.split(' ')
    if parts[0] in commands:
        return Message(from_user=username, command=parts[0], body=parts[1])
    else:
        return Message(from_user=username, body=user_input)


if __name__=='__main__':
    chat()
