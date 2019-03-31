import socket
from threading import Thread

class Broker:

    users = {} # user -> socket
    chats = [] # pairs of users
    queue = {} # user -> messages

    def handle(msg, sock):
        message = Message.from_bytes(msg)
        # add sock to users map
        # send to other end, if initiated, or queue for later


class Message:
    
    def __init__(self, username, command=None, message=None):
        self.username = username
        self.command = command or b''
        self.message = message or b''


    def as_bytes(self):
        msg = bytearray(self.message)
        msg.insert(0, len(msg))

        uname = bytearray(self.username)
        uname.insert(0, len(uname))

        cmd = bytearray(self.command)
        cmd.insert(0, len(cmd))

        result = bytearray()
        result.extend(uname)
        result.extend(cmd)
        result.extend(msg)
        result.insert(0, len(result))
        
        return bytes(result)


    @staticmethod
    def from_bytes(msg):
        userlen = msg[0]
        uname = msg[:userlen+1]

        cmdlen = msg[userlen+1]
        cmd = msg[userlen+1:userlen+1+cmdlen]


class Handler(Thread):
    def __init__(self, socket, broker):
        Thread.__init__(self)
        self.sock = socket
        self.broker = broker
        self.start()


    def run(self):
        while True:
            received = self.sock.myreceive()
            print(f'Received: {received.decode()}')
            # forward message
            # broker.update(received, sock)
            # send messages queued to broker from other participant


class ChatSocket:

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
        bytes_recd = 0
        msg_size = 0
        while msg_size == 0:
            length_header = self.sock.recv(1)[0]
            msg_size = int(length_header)

        print(f'Received msg of len {msg_size}')
        while bytes_recd < msg_size:
            chunk = self.sock.recv(min(msg_size - bytes_recd, msg_size))
            if chunk == b'':
                raise RuntimeError("myreceive: socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)