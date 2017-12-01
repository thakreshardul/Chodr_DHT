import sys
import time

import network
import constants
import message
import exception


class DhtClient:
    def __init__(self, address):
        self.tcp = network.Tcp()
        self.address = (self.tcp.return_host_ip(address[0]), int(address[1]))


class TextInterface:
    def __init__(self, ip, port):
        self.client = DhtClient((ip, port))

    def connect_to_root(self, root_ip, root_port):
        self.client.tcp.start(self.client.address)
        msg = message.Message(constants.message_type["client_connect"], constants.GREETING_MESSAGE)
        self.client.tcp.connect_to_root(self.client.tcp.return_host_ip(root_ip), int(root_port))
        self.client.tcp.client_send(msg)
        reply = self.client.tcp.client_receive()
        msg_parser = message.MessageParser()
        msg_parser.validate_message_type(reply)
        print "Connected to root"

    def show_menu(self):
        print "Enter a command:\n1. s --> Store\n2. i --> Iterative Search\n" \
              "3. r --> Recursive Search\n4. e --> exit\n"
        while True:
            command = raw_input()
            if command == "s":
                pass
            elif command == "i":
                pass
            elif command == "r":
                pass
            elif command == "e":
                self.client.tcp.tear_down()
                sys.exit(0)
            else:
                print "Enter correct instruction"


def run():
    if len(sys.argv) == constants.CLIENT_CLI_ARGUMENTS:
        txtint = TextInterface(sys.argv[4], sys.argv[2])
        txtint.connect_to_root(sys.argv[8], sys.argv[6])
        txtint.show_menu()
    else:
        print "USAGE: ./dht_client <-p client_port> <-h client_hostname>" \
              "<-r root_port> <-R root_hostname>"


if __name__ == "__main__":
    run()
