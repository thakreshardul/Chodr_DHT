from hashlib import sha1
import sys

import network
import constants


class DhtPeer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.key = None
        self.successor = None
        self.predecessor = None
        self.root = False
        self.tcp = network.Tcp()

    def run(self, root_ip, root_prt):
        self.tcp.start(self.ip, self.port, root_ip, root_prt)


if __name__ == "__main__":
    while True:
        if len(sys.argv) == constants.PEER_CLI_ARGUMENTS:
            peer_host = sys.argv[4]
            peer_port = sys.argv[2]
            root_host = sys.argv[8]
            root_port = sys.argv[6]
        elif len(sys.argv) == constants.PEER_CLI_ARGUMENTS_WITH_MODE:
            peer_host = sys.argv[6]
            peer_port = sys.argv[4]
            root_host = sys.argv[10]
            root_port = sys.argv[8]
        elif len(sys.argv) == constants.ROOT_CLI_ARGUMENTS:
            peer_host = sys.argv[6]
            peer_port = sys.argv[4]
        else:
            print "Usage: ./dht_peer <-m mode> <-p port> <-h hostname> <-r root_port>" \
                  "<-R root_hostname>"
            break

        peer = DhtPeer(peer_host, peer_port)
        if root_host is not None:
            peer.run()