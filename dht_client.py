import sys

import network
import constants


class DhtClient:
    def __init__(self, client_ip, client_port):
        self.ip = client_ip
        self.port = client_port
        self.tcp = network.Tcp()


class TextInterface:
    def __init__(self, ip, port):
        self.client = DhtClient(ip, port)

    def connect_to_root(self, root_ip, root_port):
        self.client.tcp.start(self.client.ip, self.client.port, root_ip, root_port)
        print "Connected to root"

    @staticmethod
    def show_menu():
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

                pass
            else:
                print "Enter correct instruction"


def run():
    if len(sys.argv) == constants.CLIENT_CLI_ARGUMENTS:
        txtint = TextInterface(sys.argv[4], sys.argv[2])
        txtint.connect_to_root(sys.argv[8], sys.argv[6])
        txtint.show_menu()
        pass
    else:
        print "USAGE: ./dht_client <-p client_port> <-h client_hostname>" \
              "<-r root_port> <-R root_hostname>"


if __name__ == "__main__":
    run()
