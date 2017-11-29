from hashlib import sha1
import sys
from thread import start_new_thread

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

    def __connection_thread(self):
        print self.tcp.address[0]+":"+str(self.tcp.address[1])+" Connected"
        self.tcp.conn.send("Welcome to Chord")
        while True:
            msg = self.tcp.receive()
            if not msg:
                break
            print "message received"
        self.tcp.conn.close()

    def run(self, root_ip=None, root_prt=None):
        if root_ip is None and root_prt is None:
            self.tcp.start(self.ip, self.port)
            print "Peer started"
        else:
            pass
        self.tcp.listen()
        while True:
            self.tcp.accept()
            start_new_thread(self.__connection_thread, ())


if __name__ == "__main__":
    while True:
        if len(sys.argv) == constants.PEER_CLI_ARGUMENTS:
            peer_host = sys.argv[4]
            peer_port = sys.argv[2]
            root_host = sys.argv[8]
            root_port = sys.argv[6]
            break
        elif len(sys.argv) == constants.PEER_CLI_ARGUMENTS_WITH_MODE:
            peer_host = sys.argv[6]
            peer_port = sys.argv[4]
            root_host = sys.argv[10]
            root_port = sys.argv[8]
            break
        elif len(sys.argv) == constants.ROOT_CLI_ARGUMENTS and sys.argv[2] == "1":
            peer_host = sys.argv[6]
            peer_port = sys.argv[4]
            root_port = None
            root_host = None
            break
        else:
            print "Usage: ./dht_peer <-m mode> <-p port> <-h hostname> <-r root_port>" \
                  "<-R root_hostname>"

    peer = DhtPeer(peer_host, peer_port)
    peer.run(root_host, root_port)
