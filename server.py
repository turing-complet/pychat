import socket
from libchat import ChatSocket, Handler

host = 'localhost'
port = 8080

def init():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serversocket.bind((socket.gethostname(), port))
    serversocket.bind((host, port))
    serversocket.listen(5) # can queue up to 5 connect() requests
    print(f'Created socket on port {port}..')
    return serversocket


def listen(serversocket):
    while True:
        print('Accepting new connections..')
        (clientsocket, address) = serversocket.accept()
        print(f'New connection from {address}')
        chat_sock = ChatSocket(clientsocket)
        Handler(chat_sock) # handle socket in new thread


if __name__=='__main__':
    sock = init()
    listen(sock)