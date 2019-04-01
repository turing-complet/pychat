import socket
from threading import Thread
import pickle
import click
from datetime import datetime

class Broker:

    queue = {} # user -> messages
    conns = {} # { user1 -> { user2: socket } }
    dest = {} # source socket id -> dest user

    def handle(self, sock):
        msg = sock.myreceive()
        Logger.info('Broker recv')
        message = Message.from_bytes(msg)

        if message.command is not None:
            self.handle_command(sock, message)
            return

        self.set_dest(sock, message)
        if self.is_duplex(message.from_user, message.to_user):
                self.flush_queue(message.from_user)

        if message.body is not None:
            self.handle_chat(message)
        

    def handle_chat(self, message):
        Logger.info('Handle chat.. ')
        if self.is_duplex(message.from_user, message.to_user):
            self.forward(message)
        else:
            self.queue_message(message)


    def handle_command(self, sock, message):
        Logger.info('Handle command.. ')
        if message.command == '/help':
            return # TODO

        if message.command == '/chat':
            Logger.info('Adding connection..')
            self.add_connection(sock, message)

        if message.command == '/leave':
            return # TODO


    def set_dest(self, sock, msg):
        if id(sock) in self.dest.keys():
            msg.to_user = self.dest[id(sock)]
            

    def flush_queue(self, to_user):
        Logger.info('Flush.. ')
        if to_user in self.queue.keys():
            for msg in self.queue[to_user]:
                self.forward(msg)
        self.queue[to_user] = []


    def is_duplex(self, from_user, to_user):
        if to_user in self.conns.keys() and from_user in self.conns.keys():
            return from_user in self.conns[to_user].keys() \
                and to_user in self.conns[from_user].keys()
        return False


    def add_connection(self, sock, msg):
        to_user = msg.body # body of /chat command is other user
        from_user = msg.from_user

        if from_user not in self.conns.keys():
            self.conns[from_user] = {}

        if to_user not in self.conns.keys():
            self.conns[to_user] = {}

        self.conns[to_user][from_user] = sock
        self.dest[id(sock)] = to_user
        Logger.info(f'Connections: {self.conns}')
        

    def forward(self, msg):
        Logger.info('Fwd.. ')
        chat_sock = self.conns[msg.from_user][msg.to_user]
        chat_sock.mysend(msg.as_bytes())
        Logger.info(f'Forward from:{msg.from_user}, to:{msg.to_user}, body:{msg.body}')


    def queue_message(self, message):
        to_user = message.to_user
        if to_user is None:
            Logger.warn(f'Message with no destination: {message}')

        if to_user not in self.queue.keys():
            self.queue[to_user] = [message]
        else:
            self.queue[to_user].append(message)
        Logger.info(f'Queued {message}')


def timestamp():
    return datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')


class Logger:

    @staticmethod
    def info(msg):
        click.secho(f'[{timestamp()}][INFO]: {msg}', fg='bright_blue')

    @staticmethod
    def warn(msg):
        click.secho(f'[{timestamp()}][WARN]: {msg}', fg='yellow')


class Message:
    
    def __init__(self, from_user, to_user=None, command=None, body=None):
        self.from_user = from_user
        self.to_user = to_user
        self.command = command
        self.body = body

    def __str__(self):
        return f'From: {self.from_user}, To: {self.to_user}, Cmd: {self.command}, Body: {self.body}'

    def as_bytes(self):
        return pickle.dumps(self)


    @staticmethod
    def from_bytes(msg):
        return pickle.loads(msg)


class ServerHandler(Thread):
    def __init__(self, socket, broker):
        Thread.__init__(self)
        self.sock = socket
        self.broker = broker
        self.start()


    def run(self):
        while True:
            self.broker.handle(self.sock)


class ClientHandler(Thread):
    def __init__(self, handler):
        Thread.__init__(self)
        self.handler = handler
        self.start()


    def run(self):
        while True:
            self.handler()


class ChatSocket:

    MAX_SIZE = 2048

    def __init__(self, sock=None):
        if sock is not None:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect(self, host, port):
        self.sock.connect((host, port))


    def mysend(self, msg):
        arr = bytearray(msg)
        arr.insert(0, len(msg))
        msg = bytes(arr)
        self.sock.sendall(msg)


    def myreceive(self):
        chunks = []

        msg_size = 0
        while msg_size == 0:
            length_header = self.sock.recv(1)[0]
            msg_size = int(length_header)

        bytes_recd = 0
        while bytes_recd < msg_size:
            chunk = self.sock.recv(min(msg_size - bytes_recd, msg_size))
            if chunk == b'':
                raise RuntimeError("myreceive: socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return b''.join(chunks)