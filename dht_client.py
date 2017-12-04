import sys
import json
import time

import network
import constants
from message import Message, MessageParser
import exception


class DhtClient:
    def __init__(self, address):
        self.tcp = network.Tcp(int(address[1]))
        self.address = (self.tcp.return_host_ip(address[0]), int(address[1]))


class TextInterface:
    def __init__(self, ip, port, root_ip, root_port):
        self.client = DhtClient((ip, port))
        self.root = (self.client.tcp.return_host_ip(root_ip), int(root_port))

    def connect_to_root(self):
        self.client.tcp.start(self.client.address)
        msg = Message(msg_type=constants.message_type["client_connect"], destination=self.client.address)
        msg_parser = MessageParser()
        msg = msg_parser.pack_msg(msg)
        self.client.tcp.socket.sendto(msg, self.root)

        response, addr = self.client.tcp.socket.recvfrom(constants.BUFFER_SIZE)
        response = msg_parser.unpack_msg(response)
        msg_parser.validate_message_type(response)
        print response.data

    def show_menu(self):
        print "Enter a command:\ns --> Store\ni --> Iterative Search\n" \
              "r --> Recursive Search\ne --> exit\n"
        msg_parser = MessageParser()
        while True:
            command = raw_input()
            if command == "s":
                data = dict()
                print "Enter key:"
                key = raw_input()
                print "Enter value:"
                val = raw_input()
                data = (key, val)
                msg = Message(constants.message_type["store"], self.client.address, str(data), self.root)
                msg = msg_parser.pack_msg(msg)
                self.client.tcp.socket.sendto(msg, self.root)
                pass
            elif command == "i":
                print "You have selected Iterative retrieve. Enter the key:"
                key = raw_input()
                msg = Message(constants.message_type["iterative_retrieve"], self.client.address, str(key), self.client.address)
                msg = msg_parser.pack_msg(msg)
                self.client.tcp.socket.sendto(msg, self.root)

                response, addr = self.client.tcp.socket.recvfrom(constants.BUFFER_SIZE)
                response = msg_parser.unpack_msg(response)
                msg_parser.validate_message_type(response)
                print response.data
                pass
            elif command == "r":
                print "You have selected Iterative retrieve. Enter the key:"
                key = raw_input()
                msg = Message(constants.message_type["recursive_retrieve"], self.client.address, str(key), self.client.address)
                msg = msg_parser.pack_msg(msg)
                self.client.tcp.socket.sendto(msg, self.root)

                response, addr = self.client.tcp.socket.recvfrom(constants.BUFFER_SIZE)
                response = msg_parser.unpack_msg(response)
                msg_parser.validate_message_type(response)
                print response.data
                pass
            elif command == "e":
                sys.exit(0)
            else:
                print "Enter correct instruction"


def run():
    if len(sys.argv) == constants.CLIENT_CLI_ARGUMENTS:
        txtint = TextInterface(sys.argv[4], sys.argv[2], sys.argv[8], sys.argv[6])
        txtint.connect_to_root()
        txtint.show_menu()
    else:
        print "USAGE: ./dht_client <-p client_port> <-h client_hostname>" \
              "<-r root_port> <-R root_hostname>"


if __name__ == "__main__":
    run()
