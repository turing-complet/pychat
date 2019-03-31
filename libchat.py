import socket
from threading import Thread


class Handler(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.sock = socket
        self.start()


    def run(self):
        print('Running client thread')
        while True:
            received = self.sock.myreceive()
            print(f'Client sent: {received.decode()}')
            self.sock.mysend(b'Oi you sent something to me')


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