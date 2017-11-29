import socket

import constants
import exception


class Tcp:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, ip, port, root_ip=None, root_port=None):
        self.socket.bind((socket.gethostbyname(ip), port))
        if root_ip and root_port:
            try:
                self.socket.connect((socket.gethostbyname(root_ip), root_port))
            except exception.RootConnectException as e:
                print str(e)


    def receive(self):
        msg = self.socket.recv(constants.BUFFER_SIZE)
        return msg
