BUFFER_SIZE = 100000
CLIENT_CLI_ARGUMENTS = 9
ROOT_CLI_ARGUMENTS = 7
PEER_CLI_ARGUMENTS = 9
PEER_CLI_ARGUMENTS_WITH_MODE = PEER_CLI_ARGUMENTS + 2
BACKLOG_FOR_TCP_SOCKET = 20
SOCKET_TIMEOUT = 10
GREETING_MESSAGE = "Hello"
DB_FILE = "index"
ACK = "Success"
NACK = "Failure"
CLIENT = "client"
SUCCESSOR = "successor"
PREDECESSOR = "predecessor"
HEARTBEAT = "heartbeat"
SHUT_RDWR = 2

message_type = {
    "join": 0,
    "set_successor": 1,
    "set_predecessor": 2,
    "update_predecessor": 3,
    "join_to_peer": 4,
    "store": 5,
    "retrieve": 6,
    "ack": 7,
    "heartbeat": 8,
    "close":9,
    "test": 20
}

message_dictionary = {
    0: "join",
    1: "set_successor",
    2: "set_predecessor",
    3: "update_predecessor",
    4: "join_to_peer",
    5: "store",
    6: "retrieve",
    7: "ack",
    8: "heartbeat",
    9: "close",
    20: "test"
}

