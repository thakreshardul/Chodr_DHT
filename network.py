import socket

import constants
import exception


class Tcp:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.address = None

    def start(self, ip, port, root_ip=None, root_port=None):
        self.socket.bind((socket.gethostbyname(ip), int(port)))
        if root_ip and root_port:
            try:
                self.socket.connect((socket.gethostbyname(root_ip), int(root_port)))
            except exception.RootConnectException as e:
                print str(e)

    def listen(self):
        self.socket.listen(constants.BACKLOG_FOR_TCP_SOCKET)
        print "Listening for connection"

    def accept(self):
        self.conn, self.address = self.socket.accept()

    def send(self, msg):
        self.conn.send(msg)

    def receive(self):
        msg = self.conn.recv(constants.BUFFER_SIZE)
        return msg
