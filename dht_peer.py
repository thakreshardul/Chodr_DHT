from hashlib import sha1
import sys
import threading
import time

import network
import constants
from message import MessageParser, Message
import exception


tcp = None
address = None
successor = None
predecessor = None
root = bool
id = None
db = None
root_address = None
successor_thread = None
predecessor_thread = None
heartbeat = None
heartbeat_listen = None
predecessor_dead_flag = bool
successor_dead_flag = bool
client_threads = []


class ClientThread(threading.Thread):
    def __init__(self):
        super(ClientThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        try:
            while not self.stopped():
                request, addr = tcp.socket.recvfrom(constants.BUFFER_SIZE)
                msg_parser = MessageParser()
                request = msg_parser.unpack_msg(request)
                request_handler(request)
        except Exception as e:
            print str(e)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class SuccessorThread(threading.Thread):
    def __init__(self):
        super(SuccessorThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            try:
                # tcp.successor_socket.listen(constants.BACKLOG_FOR_TCP_SOCKET)
                print "Waiting for new successor at: ", tcp.successor_port
                # tcp.successor_connection, tcp.useless = tcp.successor_socket.accept()
                # print "New successor connected: ", successor
                while True:
                    request, addr = tcp.successor_socket.recvfrom(constants.BUFFER_SIZE)
                    print "recd from ", addr
                    msg_parser = MessageParser()
                    request = msg_parser.unpack_msg(request)
                    if request.type != constants.message_type["heartbeat"]:
                        request_handler(request)
            except Exception as e:
                print str(e)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class PredecessorThread(threading.Thread):
    def __init__(self):
        super(PredecessorThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        print "Predecessor thread started"
        while not self.stopped():
            try:
                print "Waiting for new predecessor at: ", tcp.predecessor_port
                while True:
                    request, addr = tcp.predecessor_socket.recvfrom(constants.BUFFER_SIZE)
                    print "recd from ",addr
                    msg_parser = MessageParser()
                    request = msg_parser.unpack_msg(request)
                    if request.type != constants.message_type["heartbeat"]:
                        request_handler(request)
            except Exception as e:
                print str(e)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class HeartBeatSendThread(threading.Thread):
    def __init__(self):
        super(HeartBeatSendThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        msg_parser = MessageParser()
        while not self.stopped():
            time.sleep(constants.SOCKET_TIMEOUT)
            msg = Message(constants.message_type["heartbeat"], (address[0], tcp.successor_port))
            msg = msg_parser.pack_msg(msg)
            tcp.successor_socket.sendto(msg, successor)

            msg = Message(constants.message_type["heartbeat"], (address[0], tcp.predecessor_port))
            msg = msg_parser.pack_msg(msg)
            tcp.predecessor_socket.sendto(msg, predecessor)
        pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class HeartBeatListenThread(threading.Thread):
    def __init__(self):
        super(HeartBeatListenThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        global predecessor_dead_flag
        global successor_dead_flag
        msg_parser = MessageParser()
        timer_p = 0
        timer_s = 0
        while not self.stopped():
            time.sleep(constants.SOCKET_TIMEOUT - 2)
            msg, addr = tcp.predecessor_socket.recvfrom(constants.BUFFER_SIZE)
            msg = msg_parser.unpack_msg(msg)
            msg_parser.validate_message_type(msg)
            if msg.type == constants.message_type["heartbeat"]:
                timer_p = 0
                pass
            if timer_p >= 2:
                predecessor_dead_flag = True
                predecessor_dead()

            msg, addr = tcp.successor_socket.recvfrom(constants.BUFFER_SIZE)
            msg = msg_parser.unpack_msg(msg)
            msg_parser.validate_message_type(msg)
            if msg.type == constants.message_type["heartbeat"]:
                timer_s = 0
                pass
            if timer_s >= 2:
                successor_dead_flag = True
            timer_p += 1
            timer_s += 1
        pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def predecessor_dead():
    msg = Message(constants.message_type["survival"], (address[0], tcp.predecessor_port))
    msg_parser = MessageParser()
    msg = msg_parser.pack_msg(msg)
    tcp.predecessor_socket.sendto(msg, ('', tcp.predecessor_port))
    pass


def send_req_to_successor(request, msg_parser):
    request.sender = address
    request = msg_parser.pack_msg(request)
    tcp.successor_socket.sendto(request, successor)

    response = tcp.successor_socket.recvfrom(constants.BUFFER_SIZE)
    response = msg_parser.unpack_msg(response)
    request_handler(response)

    response = tcp.successor_socket.recvfrom(constants.BUFFER_SIZE)
    response = msg_parser.unpack_msg(response)
    request_handler(response)


def add_peer(request, msg_parser, destination):
    global successor
    msg = Message(constants.message_type["set_predecessor"], address, (address[0], address[1] + 1), destination)
    msg = msg_parser.pack_msg(msg)
    if root:
        tcp.socket.sendto(msg, destination)
    else:
        tcp.predecessor_socket.sendto(msg, predecessor)

    msg = Message(constants.message_type["set_successor"], address, successor, destination)
    msg = msg_parser.pack_msg(msg)
    if root:
        tcp.socket.sendto(msg, destination)
    else:
        tcp.predecessor_socket.sendto(msg, predecessor)

    msg = Message(constants.message_type["update_predecessor"], data=(request.data[0], request.data[1] + 1))
    msg = msg_parser.pack_msg(msg)
    tcp.successor_socket.sendto(msg, successor)

    successor_thread.stop()
    successor = (request.data[0], request.data[1] + 2)
    successor_thread._stop_event.clear()
    successor_thread.run()

    heartbeat = HeartBeatSendThread()
    heartbeat.start()
    heartbeat_listen = HeartBeatListenThread()
    heartbeat_listen.start()


def join_handler(request):
    try:
        global successor
        global predecessor
        msg_parser = MessageParser()
        destination = request.destination
        if successor is None and predecessor is None:
            # send msg to request.sender their successor and predecessor
            msg = Message(constants.message_type["set_predecessor"], address,(address[0], tcp.successor_port), destination)
            msg = msg_parser.pack_msg(msg)
            tcp.socket.sendto(msg, destination)

            msg = Message(constants.message_type["set_successor"], address, (address[0], tcp.predecessor_port), destination)
            msg = msg_parser.pack_msg(msg)
            tcp.socket.sendto(msg, destination)

            successor = (request.data[0], request.data[1] + 2)
            predecessor = (request.data[0], request.data[1] + 1)

            successor_thread.start()
            predecessor_thread.start()

            heartbeat = HeartBeatSendThread()
            heartbeat.start()
            heartbeat_listen = HeartBeatListenThread()
            heartbeat_listen.start()
        else:
            peer_id = sha1(str(request.data[1])).hexdigest()
            successor_id = sha1(str(successor[1])).hexdigest()
            if id > successor_id:
                if peer_id > successor_id and successor[0] != root_address[0]:
                        # send the request to successor
                        send_req_to_successor(request, msg_parser)
                else:
                        # add the node in between self and successor
                        add_peer(request, msg_parser, destination)
            else:
                if peer_id < successor_id or successor[0] == root_address[0]:
                    # add node in between self and successor
                    add_peer(request, msg_parser, destination)
                else:
                    # send the request to successor
                    send_req_to_successor(request, msg_parser)
        pass
    except Exception as e:
        print "Join handler failed"+str(e)


def store(request):
    global db
    data = request.data
    data_id = sha1(data.split(',')[0].lstrip('(').strip("'")).hexdigest()
    if successor is None:
        with open(constants.DB_FILE, "w+") as db:
            data = str(data)+'\n'
            print data
            db.write(data)
            db.close()
        print "Data stored"
    else:
        print "here"
        successor_id = sha1(str(successor[1])).hexdigest()
        msg_parser = MessageParser()
        if id < data_id < successor_id or successor == (root_address[0],root_address[1] + 2):
            # store on self node
            print "Storing ",id, data_id, successor_id
            with open(constants.DB_FILE, "w+") as db:
                data = str(data) + '\n'
                db.write(data)
                db.close()
            print "Data stored"
        else:
            request.sender = address
            request = msg_parser.pack_msg(request)
            tcp.successor_socket.sendto(request, successor)


def iterative_retrieve(request):
    global db
    data = request.data
    print data
    data_id = sha1(data).hexdigest()
    if successor is None:
        with open(constants.DB_FILE, "r") as db:
            for line in db:
                key = line.split(',')[0].lstrip('(').strip("'")
                key_id = sha1(key).hexdigest()
                if data_id == key_id:
                    db.close()
                    return line
            db.close()
        return -1
    else:
        successor_id = sha1(str(successor[1])).hexdigest()
        msg_parser = MessageParser()
        if id < data_id < successor_id or successor == (root_address[0],root_address[1] + 2):
            with open(constants.DB_FILE, "r") as db:
                for line in db:
                    key = line.split(',')[0].lstrip('(').strip("'")
                    key_id = sha1(key).hexdigest()
                    if data_id == key_id:
                        db.close()
                        return line
                db.close()
            return -1
        else:
            temp_successor = successor
            print temp_successor
            while temp_successor != (address[0], address[1] + 2):
                msg = Message(constants.message_type["exist"], address, data)
                msg = msg_parser.pack_msg(msg)
                tcp.successor_socket.sendto(msg, (temp_successor[0], temp_successor[1]))

                response, addr = tcp.socket.recvfrom(constants.BUFFER_SIZE)
                response = msg_parser.unpack_msg(response)
                msg_parser.validate_message_type(response)
                print constants.message_dictionary[response.type]
                if response.type == constants.message_type["ack"]:
                    return response.data
                    pass
                elif response.type == constants.message_type["nack"]:
                    temp_successor = response.data
                elif response.type == constants.message_type["not_found"]:
                    print "Not Found"
                    return -1

    pass


def recursive_retrieve(request):
    global db
    data = request.data
    data_id = sha1(data).hexdigest()
    if successor is None:
        with open(constants.DB_FILE, "r") as db:
            for line in db:
                key = line.split(',')[0].lstrip('(').strip("'")
                key_id = sha1(key).hexdigest()
                if data_id == key_id:
                    db.close()
                    return line
            db.close()
        return -1
    else:
        successor_id = sha1(str(successor[1])).hexdigest()
        msg_parser = MessageParser()
        if id < data_id < successor_id or successor == (root_address[0], root_address[1] + 2):
            with open(constants.DB_FILE, "r") as db:
                for line in db:
                    key = line.split(',')[0].lstrip('(').strip("'")
                    key_id = sha1(key).hexdigest()
                    if data_id == key_id:
                        if root:
                            db.close()
                            return line
                        else:
                            msg = Message(constants.message_type["ack"], address, line)
                            msg = msg_parser.pack_msg(msg)
                            tcp.predecessor_socket.sendto(msg, request.sender)
                            db.close()
            if root:
                return -1
            else:
                msg = Message(constants.message_type["not_found"])
                msg = msg_parser.pack_msg(msg)
                tcp.predocessor_socket.sendto(msg, request.sender)
        else:
            msg = Message(constants.message_type["recursive_retrieve"], address, data)
            msg = msg_parser.pack_msg(msg)
            tcp.successor_socket.sendto(msg, successor)

            response, addr = tcp.socket.recvfrom(constants.BUFFER_SIZE)
            response = msg_parser.unpack_msg(response)
            msg_parser.validate_message_type(response)
            if root:
                return response.data
            else:
                tcp.predecessor_socket.sendto(response, request.sender)


def distribute_keys():
    global db
    msg_parser = MessageParser()
    successor_id = sha1(str(successor[1])).hexdigest()
    with open(constants.DB_FILE, "r") as db:
        for line in db:
            key = line.split(',')[0].lstrip('(').strip("'")
            key_id = sha1(key).hexdigest()
            print key, key_id, successor_id
            if key_id >= successor_id:
                msg = Message(constants.message_type["save"], address, line)
                msg = msg_parser.pack_msg(msg)
                tcp.successor_socket.sendto(msg, successor)
        db.close()


def request_handler(request):
    global predecessor
    global successor
    global db

    msg_parser = MessageParser()
    msg_parser.validate_message_type(request)
    destination = request.destination
    if request.type == constants.message_type["join"]:
        join_handler(request)
    elif request.type == constants.message_type["set_predecessor"]:
        if request.destination == address:
            print "setting predecessor to: ", request.data
            predecessor = request.data
        else:
            request.sender = address
            request = msg_parser.pack_msg(request)
            tcp.predecessor_socket.sendto(request, predecessor)
    elif request.type == constants.message_type["set_successor"]:
        if request.destination == address:
            print "setting successor to: ", request.data
            successor = request.data
        else:
            request.sender = address
            request = msg_parser.pack_msg(request)
            tcp.predecessor_socket.sendto(request, predecessor)
    elif request.type == constants.message_type["update_predecessor"]:
        print "Updating predecessor: ", request.data
        predecessor_thread.stop()
        heartbeat_listen.stop()
        heartbeat.stop()
        predecessor = request.data
        predecessor_thread._stop_event.clear()
        heartbeat_listen._stop_event.clear()
        heartbeat._stop_event.clear()
        predecessor_thread.run()
        heartbeat.run()
        heartbeat_listen.run()
    elif request.type == constants.message_type["store"]:
        store(request)
    elif request.type == constants.message_type["client_connect"]:
        print "Client connecting"
        msg = Message(constants.message_type["greeting"], address, constants.GREETING_MESSAGE)
        msg = msg_parser.pack_msg(msg)
        tcp.socket.sendto(msg, destination)
    elif request.type == constants.message_type["iterative_retrieve"]:
        data = iterative_retrieve(request)
        msg = Message(constants.message_type["iterative_retrieve"], address, data, destination)
        msg = msg_parser.pack_msg(msg)
        tcp.socket.sendto(msg, destination)
        pass
    elif request.type == constants.message_type["recursive_retrieve"]:
        data = recursive_retrieve(request)
        msg = Message(constants.message_type["recursive_retrieve"], address, data, destination)
        msg = msg_parser.pack_msg(msg)
        if root:
            tcp.socket.sendto(msg, destination)
        else:
            tcp.predecessor_socket.sendto(msg, predecessor)
        pass
    elif request.type == constants.message_type["exist"]:
        data_id = request.data
        data_id = sha1(data_id).hexdigest()
        successor_id = sha1(str(successor[1])).hexdigest()
        if id < data_id < successor_id or (root_address[0], root_address[1] + 2) == successor:
            with open(constants.DB_FILE, "r") as db:
                for line in db:
                    key = line.split(',')[0].lstrip('(').strip("'")
                    key_id = sha1(key).hexdigest()
                    print key, key_id, data_id
                    if data_id == key_id:
                        msg = Message(constants.message_type["ack"], address, line)
                        msg = msg_parser.pack_msg(msg)
                        tcp.predecessor_socket.sendto(msg, request.sender)
                        db.close()
                        break
                db.close()
            msg = Message(constants.message_type["not_found"], address)
            msg = msg_parser.pack_msg(msg)
            tcp.predecessor_socket.sendto(msg, request.sender)
        else:
            msg = Message(constants.message_type["nack"], address, successor)
            msg = msg_parser.pack_msg(msg)
            tcp.predecessor_socket.sendto(msg, request.sender)
    elif request.type == constants.message_type["distribute_keys"]:
        distribute_keys()
    elif request.type == constants.message_type["save"]:
        with open(constants.DB_FILE, "w+") as db:
            print "writing to db: ", request.data
            db.write(str(request.data) + '\n')
            db.close()
    elif request.type == constants.message_type["survival"]:
        if successor_dead_flag:
            msg = Message(constants.message_type["update_predecessor"], data=(address[0], tcp.successor_port))
            msg = msg_parser.pack_msg(msg)
            tcp.successor_socket.sendto(msg, request.sender)

            heartbeat_listen.stop()
            heartbeat.stop()
            successor_thread.stop()

            successor = request.sender
            successor_thread._stop_event.clear()

            successor_thread.run()
            heartbeat.run()
            heartbeat_listen.run()


def join():
    try:
        msg = Message(constants.message_type["join"], address, address, address)
        msg_parser = MessageParser()
        msg = msg_parser.pack_msg(msg)
        tcp.socket.sendto(msg, root_address)

        response, addr = tcp.socket.recvfrom(constants.BUFFER_SIZE)
        response = msg_parser.unpack_msg(response)
        request_handler(response)

        response, addr = tcp.socket.recvfrom(constants.BUFFER_SIZE)
        response = msg_parser.unpack_msg(response)
        request_handler(response)

        print "Node joined successfully at: ", successor, predecessor

        successor_thread.start()
        predecessor_thread.start()

        msg = Message(constants.message_type["distribute_keys"], (address[0], tcp.predecessor_port), str(address[1]))
        msg = msg_parser.pack_msg(msg)
        tcp.predecessor_socket.sendto(msg, predecessor)

        heartbeat.start()
        heartbeat_listen.start()

    except Exception as e:
        print str(e)


def run():
    tcp.start(address)
    try:
        if root:
            t = ClientThread()
            t.start()
            client_threads.append(t)
        else:
            join()
            t = ClientThread()
            t.start()
            client_threads.append(t)
        for t in client_threads:
            t.join()
    except Exception as e:
        print str(e)


def init(ip, port, is_root=False, root_addr=None):
    global tcp
    tcp = network.Tcp(int(port))
    global address
    address = (tcp.return_host_ip(ip), int(port))
    global root
    root = is_root
    global id
    id = sha1(str(address[1])).hexdigest()                  ###########################
    global root_address
    root_address = (tcp.return_host_ip(root_addr[0]), int(root_addr[1]))
    global successor_thread
    successor_thread = SuccessorThread()
    global predecessor_thread
    predecessor_thread = PredecessorThread()
    global heartbeat
    heartbeat = HeartBeatSendThread()
    global heartbeat_listen
    heartbeat_listen = HeartBeatListenThread()


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

    init(peer_host, peer_port, root, (root_host, root_port))
    run()
