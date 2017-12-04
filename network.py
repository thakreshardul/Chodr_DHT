import socket

import constants
import exception


class Tcp:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.successor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.predecessor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = port
        self.successor_port = self.port + 1
        self.predecessor_port = self.port + 2

    def start(self, address):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(constants.SOCKET_TIMEOUT)
            self.socket.bind(address)
            self.successor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.successor_socket.settimeout(constants.SOCKET_TIMEOUT)
            self.successor_socket.bind((address[0], self.successor_port))
            self.predecessor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.predecessor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.predecessor_socket.settimeout(constants.SOCKET_TIMEOUT)
            self.predecessor_socket.bind((address[0], self.predecessor_port))
        except exception.BindException as e:
            print str(e)

    def connect_to_root(self, address):
        try:
            self.socket.connect(address)
        except exception.ConnectionException as e:
            print str(e)

    @staticmethod
    def return_host_ip(ip):
        return socket.gethostbyname(ip)
