import socket
from threading import Thread
import pickle

class Broker:

    users = {} # user -> socket
    queue = {} # user -> messages
    sessions = [] # pairs of users

    def handle(self, sock):
        msg = sock.myreceive()
        print('Broker recv')
        message = Message.from_bytes(msg)
        print('Broker deserialized')
        self.users[message.from_user] = sock

        self.flush_queue(message.from_user)

        if message.body is not None:
            self.handle_chat(message)

        if message.command is not None:
            self.handle_command(message)
        

    def handle_chat(self, message):
        print('Handle chat.. ')
        if message.to_user not in self.users.keys():
            self.queue_message(message)
        else:
            self.forward(message)


    def handle_command(self, message):
        print('Handle command.. ')
        if message.command == '/help':
            return # TODO
        if message.command == '/chat':
            self.sessions.append(set([message.from_user, message.to_user]))
        if message.command == '/leave':
            self.users.keys().remove(message.from_user)
            

    def flush_queue(self, to_user):
        print('Flush.. ')
        if to_user in self.queue.keys():
            for msg in self.queue[to_user]:
                self.forward(msg)


    def forward(self, msg):
        print('Fwd.. ')
        chat_sock = self.users[msg.to_user]
        chat_sock.mysend(msg.as_bytes())
        print(f'Forward from:{msg.from_user}, to:{msg.to_user}, body:{msg.body}')


    def queue_message(self, message):
        to_user = message.to_user
        if to_user is None:
            return

        if self.queue[to_user] == None:
            self.queue[to_user] = [message]
        else:
            self.queue[to_user].append(message)
        print(f'Queued from:{message.from_user}, to:{message.to_user}, body:{message.body}')


class Message:
    
    def __init__(self, from_user, to_user=None, command=None, body=None):
        self.from_user = from_user
        self.to_user = to_user
        self.command = command
        self.body = body


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