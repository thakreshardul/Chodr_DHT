import socket
import pickle

import constants
import exception


class Tcp:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.address = None

    @staticmethod
    def return_host_ip(ip):
        return socket.gethostbyname(ip)

    def start(self, address):
        try:
            self.socket.bind(address)
        except exception.BindException as e:
            print str(e)

    def connect_to_root(self, root_ip, root_port):
        try:
            self.socket.connect((root_ip, root_port))
        except exception.RootConnectException as e:
            print str(e)

    def tear_down(self):
        if self.conn:
            self.conn.close()
        self.socket.close()

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
            message = pickle.loads(msg)
            return message
        except exception.ClientReceiveException as e:
            print str(e)

    def client_send(self, msg):
        try:
            message = pickle.dumps(msg)
            self.socket.send(message)
        except exception.ClientSendException as e:
            print str(e)

    def peer_receive(self):
        try:
            msg = self.conn.recv(constants.BUFFER_SIZE)
            message = pickle.loads(msg)
            return message
        except exception.PeerSendException as e:
            print str(e)

    def peer_send(self, msg, address):
        try:
            message = pickle.dumps(msg)
            self.conn.sendto(message, address)
        except exception.PeerSendException as e:
            print str(e)
