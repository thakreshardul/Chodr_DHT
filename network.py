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
        try:
            self.socket.listen(constants.BACKLOG_FOR_TCP_SOCKET)
            print "Listening for connection"
        except exception.ConnectionListenException as e:
            print str(e)

    def accept(self):
        try:
            self.conn, self.address = self.socket.accept()
        except exception.ConnectionAcceptException as e:
            print str(e)

    def client_receive(self):
        try:
            msg = self.socket.recv(constants.BUFFER_SIZE)
        except exception.ClientReceiveException as e:
            print str(e)

        return msg

    def client_send(self, msg):
        try:
            self.socket.send(msg)
        except exception.ClientSendException as e:
            print str(e)

    def peer_receive(self):
        try:
            msg = self.conn.recv(constants.BUFFER_SIZE)
        except exception.PeerSendException as e:
            print str(e)

        return msg

    def peer_send(self, msg):
        try:
            self.conn.sendall(msg)
        except exception.PeerSendException as e:
            print str(e)

