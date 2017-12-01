from hashlib import sha1
import sys
from thread import start_new_thread

import network
import constants
import message
import exception


class DhtPeer:
    def __init__(self, ip, port, is_root=False):
        self.tcp = network.Tcp()
        self.address = (self.tcp.return_host_ip(ip), int(port))
        self.successor = None
        self.predecessor = None
        self.root = is_root
        self.id = sha1(self.address).hexdigest()
        self.db = open(constants.DB_FILE, 'a')
        self.num_peers = 0

    def __heartbeat(self):
        pass

    def __request_handler(self, request):
        msg_parser = message.MessageParser()
        msg_parser.validate_message_type(request)
        if request.type == constants.message_type["join"]:
            if self.successor is None:
                self.successor = msg_parser.extract_data(request)
                self.predecessor = msg_parser.extract_data(request)
                response = message.Message(constants.message_type["successor"], self.address)
                self.tcp.peer_send(response, msg_parser.extract_data(request))
                response = message.Message(constants.message_type["predecessor"], self.address)
                self.tcp.peer_send(response, msg_parser.extract_data(request))
            else:
                peer_address = msg_parser.extract_data(request)
                peer_id = sha1(peer_address).hexdigest()
                successor_id = sha1(self.successor).hexdigest()
                if self.id < peer_id < successor_id:
                    response = message.Message(constants.message_type["successor"], self.successor)
                    self.tcp.peer_send(response, )
                    notification = message.Message(constants.message_type["update_predecessor"], peer_address)
                    self.tcp.peer_send(notification, self.successor)
                    self.successor = msg_parser.extract_data(request)
                    response = message.Message(constants.message_type["predecessor"], self.address)
                    self.tcp.peer_send(response, None)

    def __join(self):
        # send message to root to find successor and predecessor
        # receive successor and predecessor
        # update self values accordingly
        # tcp connect to successor and predecessor
        msg = message.Message(constants.message_type["join"], self.address)
        self.tcp.client_send(msg)
        successor = self.tcp.client_receive()
        predecessor = self.tcp.client_receive()
        msg_parser = message.MessageParser()
        msg_parser.validate_message_type(successor)
        msg_parser.validate_message_type(predecessor)
        self.successor = successor
        self.predecessor = predecessor
        # start_new_thread(self.__heartbeat, ())

    def run(self, root_ip, root_prt):
        self.tcp.start(self.address)
        if self.root:
            self.tcp.listen()
            while True:
                self.tcp.accept()
                request = self.tcp.peer_receive()
                start_new_thread(self.__request_handler, (request,))
        else:
            root_address = (self.tcp.return_host_ip(root_ip), int(root_prt))
            self.tcp.connect_to_root(root_address)
            self.__join()
                # self.tcp.listen()
            while True:
                # request = self.tcp.client_receive()
                # self.__process_request()              set/get
                break


if __name__ == "__main__":
    while True:
        root = False
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
            root = True
            break
        else:
            print "Usage: ./dht_peer <-m mode> <-p port> <-h hostname> <-r root_port>" \
                  "<-R root_hostname>"

    peer = DhtPeer(peer_host, peer_port, root)
    peer.run(root_host, root_port)
