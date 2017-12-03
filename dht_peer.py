from hashlib import sha1
import sys
import threading
import json
import time

import network
import constants
from message import MessageParser, Message
import exception


class DhtPeer:
    def __init__(self, ip, port, is_root=False, root_address=None):
        self.tcp = network.Tcp(int(port))
        self.address = (self.tcp.return_host_ip(ip), int(port))
        self.successor = None
        self.predecessor = None
        self.root = is_root
        self.id = sha1(str(self.address[1])).hexdigest()
        self.db = open(constants.DB_FILE, 'ab')
        self.num_peers = 0
        self.root_address = (self.tcp.return_host_ip(root_address[0]), int(root_address[1]))
        self.threads = []

    def run(self):
        self.tcp.start(self.address)
#        print self.id
        try:
            if self.root:
                t = threading.Thread(target=self.__client_handler)
                t.start()
                self.threads.append(t)
                t = threading.Thread(target=self.__successor_handler)
                t.start()
                self.threads.append(t)
                t = threading.Thread(target=self.__predecessor_handler)
                t.start()
                self.threads.append(t)
                # t = threading.Thread(target=self.__printer)
                # t.start()
                # self.threads.append(t)
                self.__test()
            else:
                self.__join()
                # t = threading.Thread(target=self.__printer)
                # t.start()
                # self.threads.append(t)
                self.__test()
            for t in self.threads:
                t.join()
        except Exception as e:
            print str(e)

    def __test(self):
        while True:
            time.sleep(5)
            print self.address, self.successor, self.predecessor
            msg = Message(constants.message_type["test"], address=self.address, data="hello")
            msg = MessageParser.pack_msg(msg)
            print self.tcp.successor_connection, self.tcp.predecessor_socket
            self.tcp.successor_connection.sendall(msg)
            self.tcp.predecessor_socket.sendall(msg)

    # def __printer(self):
    #     while True:
    #         time.sleep(5)
    #         print self.address, self.successor, self.predecessor

    def __client_handler(self):
        self.tcp.socket.listen(constants.BACKLOG_FOR_TCP_SOCKET)
        while True:
            try:
                self.tcp.connection, self.tcp.useless = self.tcp.socket.accept()
                request = self.tcp.connection.recv(constants.BUFFER_SIZE)
                msg_parser = MessageParser()
                request = msg_parser.unpack_msg(request)
#                print request.type
                t = threading.Thread(target=self.__request_handler, args=(request,))
                t.start()
                self.threads.append(t)
            except Exception as e:
                print str(e)

    def __successor_handler(self):
        while self.successor is None:
            pass
        self.tcp.successor_socket.listen(constants.BACKLOG_FOR_TCP_SOCKET)
        while True:
            try:
                self.tcp.successor_connection, self.tcp.useless = self.tcp.successor_socket.accept()
                request = self.tcp.successor_connection.recv(constants.BUFFER_SIZE)
                msg_parser = MessageParser()
                request = msg_parser.unpack_msg(request)
                t = threading.Thread(target=self.__request_handler, args=(request,))
                t.start()
                self.threads.append(t)
            except Exception as e:
                print str(e)

    def __predecessor_handler(self):
        try:
            while self.predecessor is None:
                pass
            self.tcp.predecessor_socket.connect(self.predecessor)
            request = self.tcp.predecessor_socket.recv(constants.BUFFER_SIZE)
            msg_parser = MessageParser()
            request = msg_parser.unpack_msg(request)
            t = threading.Thread(target=self.__request_handler, args=(request,))
            t.start()
            self.threads.append(t)
        except Exception as e:
            print str(e)

    def __request_handler(self, request):
        msg_parser = MessageParser()
        # print "Handling - ", request.type
        msg_parser.validate_message_type(request)
        if request.type == constants.message_type["test"]:
            print request.sender, request.data
        if request.type == constants.message_type["join"]:
            self.__join_handler(request)
        elif request.type == constants.message_type["set_predecessor"]:
            if request.destination == self.address:
                print "setting predecessor to: ", request.data
                self.predecessor = request.data
                self.tcp.predecessor_socket.connect(self.predecessor)
            else:
                request.sender = self.address
                request = msg_parser.pack_msg(request)
                self.tcp.predecessor_socket.sendall(request)
        elif request.type == constants.message_type["set_successor"]:
            if request.destination == self.address:
                print "setting successor to: ", request.data
                self.successor = request.data
            else:
                request.sender = self.address
                request = msg_parser.pack_msg(request)
                self.tcp.predecessor_socket.sendall(request)
        elif request.type == constants.message_type["update_predecessor"]:
            print "Updating predecessor: ", request.data
            #self.tcp.tear_down(constants.PREDECESSOR)
            self.tcp.predecessor_socket.shutdown(constants.SHUT_RDWR)
            self.tcp.predecessor_socket.close()
            self.tcp.restart_socket(constants.PREDECESSOR, self.address)
            self.predecessor = request.data
            try:
                self.tcp.predecessor_socket.connect(self.predecessor)
            except Exception as e:
                print str(e)

    def __join_handler(self, request):
        try:
            msg_parser = MessageParser()
            destination = request.destination
 #           print self.successor, self.predecessor
            if self.successor is None and self.predecessor is None:
                # send msg to request.sender their successor and predecessor
                msg = Message(constants.message_type["set_successor"], self.address,
                              (self.address[0], self.tcp.predecessor_port), destination)
                msg = msg_parser.pack_msg(msg)
                self.tcp.connection.sendall(msg)

                msg = Message(constants.message_type["set_predecessor"], self.address,
                              (self.address[0], self.tcp.successor_port), destination)
#                print self.tcp.predecessor_port
                msg = msg_parser.pack_msg(msg)
                self.tcp.connection.sendall(msg)

                self.tcp.connection.close()

                self.successor = (request.data[0], request.data[1]+2)
                self.predecessor = (request.data[0], request.data[1]+1)

 #               print self.successor, self.predecessor
            else:
                peer_id = sha1(str(request.data[1])).hexdigest()
                successor_id = sha1(str(self.successor[1])).hexdigest()
                if self.id > successor_id:
                    if peer_id > successor_id and self.successor[0] != self.root_address[0]:
                            # send the request to successor
                            # print "sending to successor"
                            request.sender = self.address
  #                          print request
                            request = msg_parser.pack_msg(request)

                            self.tcp.successor_connection.sendall(request)

                            response = self.tcp.successor_connection.recv(constants.BUFFER_SIZE)
                            response = msg_parser.unpack_msg(response)
                            self.__request_handler(response)

                            response = self.tcp.successor_connection.recv(constants.BUFFER_SIZE)
                            response = msg_parser.unpack_msg(response)
                            self.__request_handler(response)
                    else:
                            # add the node in between self and successor
                            # print "Adding node"
                            msg = Message(constants.message_type["set_predecessor"], self.address,
                                          (self.address[0], self.address[1] + 1), destination)
                            msg = msg_parser.pack_msg(msg)

                            if self.root:
                                self.tcp.connection.sendall(msg)
                            else:
                                self.tcp.predecessor_socket.sendall(msg)

                            msg = Message(constants.message_type["set_successor"], self.address,
                                          (self.successor[0], self.successor[1] + 2), destination)
                            msg = msg_parser.pack_msg(msg)

                            if self.root:
                                self.tcp.connection.sendall(msg)
                            else:
                                self.tcp.predecessor_socket.sendall(msg)

                            msg = Message(msg_type=constants.message_type["update_predecessor"], data=(request.data[0], request.data[1] + 1))
                            msg = msg_parser.pack_msg(msg)

                            self.tcp.successor_connection.sendall(msg)

                            self.successor = (request.data[0], request.data[1] + 2)
                            #self.tcp.successor_connection.shutdown(network.socket.SHUT_RDWR)
                            #self.tcp.successor_connection.close()
                else:
                    if peer_id < successor_id or self.successor[0] == self.root_address[0]:
                        # add node in between self and successor
                        print "Adding node"
                        msg = Message(constants.message_type["set_predecessor"], self.address,
                                      (self.address[0], self.address[1] + 1), destination)
                        msg = msg_parser.pack_msg(msg)

                        if self.root:
                            self.tcp.connection.sendall(msg)
                        else:
                            self.tcp.predecessor_socket.sendall(msg)
   #                     print "here"
                        msg = Message(constants.message_type["set_successor"], self.address,
                                      (self.successor[0], self.successor[1] + 2), destination)
                        msg = msg_parser.pack_msg(msg)

                        if self.root:
                            self.tcp.connection.sendall(msg)
                        else:
                            self.tcp.predecessor_socket.sendall(msg)
    #                    print "here"
                        msg = Message(constants.message_type["update_predecessor"], self.address,
                                      (request.data[0], request.data[1] + 1), self.successor)
     #                   print msg.data
                        msg = msg_parser.pack_msg(msg)
                        # time.sleep(2)

                        self.tcp.successor_connection.sendall(msg)
      #                  print "here"
                        self.successor = (request.data[0], request.data[1] + 2)
                        self.tcp.successor_connection.close()
                    else:
                        # send the request to successor
       #                 print "sending to successor"
                        request.sender = self.address
                        request = msg_parser.pack_msg(request)

                        self.tcp.successor_connection.sendall(request)

                        response = self.tcp.successor_connection.recv(constants.BUFFER_SIZE)
                        response = msg_parser.unpack_msg(response)
                        self.__request_handler(response)

                        response = self.tcp.successor_connection.recv(constants.BUFFER_SIZE)
                        response = msg_parser.unpack_msg(response)
                        self.__request_handler(response)
        except Exception as e:
            print "Join handler failed"+str(e)

    def __join(self):
        try:
            self.tcp.connect_to_root(self.root_address)
        #    print self.successor, self.predecessor
            msg = Message(constants.message_type["join"], self.address, self.address, self.address)
            msg_parser = MessageParser()
            msg = msg_parser.pack_msg(msg)
            self.tcp.socket.sendall(msg)
            response = self.tcp.socket.recv(constants.BUFFER_SIZE)
            response = msg_parser.unpack_msg(response)
            self.__request_handler(response)
            response = self.tcp.socket.recv(constants.BUFFER_SIZE)
            response = msg_parser.unpack_msg(response)
            self.__request_handler(response)
            print "Node joined successfully at: ", self.successor, self.predecessor
            self.tcp.tear_down(constants.CLIENT)
            t = threading.Thread(target=self.__successor_handler)
            t.start()
            self.threads.append(t)
            t = threading.Thread(target=self.__predecessor_handler)
            t.start()
            self.threads.append(t)

        #     t = threading.Thread(target=self.__heartbeat)
        #     self.threads.append(t)
        #     t.start()
        except Exception as e:
            print str(e)

    # def __heartbeat(self):
    #     msg = Message(constants.message_type["heartbeat"], self.address, constants.HEARTBEAT)
    #     msg_parser = MessageParser()
    #     msg = msg_parser.pack_msg(msg)
    #     self.tcp.predecessor_socket.send(msg)
    #
    #     pass


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
            root_port = sys.argv[4]
            root_host = sys.argv[6]
            root = True
            break
        else:
            print "Usage: ./dht_peer <-m mode> <-p port> <-h hostname> <-r root_port>" \
                  "<-R root_hostname>"

    peer = DhtPeer(peer_host, peer_port, root, (root_host, root_port))
    peer.run()
