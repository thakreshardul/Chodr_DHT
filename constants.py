#!/usr/bin/env python

BUFFER_SIZE = 100000
CLIENT_CLI_ARGUMENTS = 9
ROOT_CLI_ARGUMENTS = 7
PEER_CLI_ARGUMENTS = 9
PEER_CLI_ARGUMENTS_WITH_MODE = PEER_CLI_ARGUMENTS + 2
BACKLOG_FOR_TCP_SOCKET = 20
SOCKET_TIMEOUT = 10
GREETING_MESSAGE = "Welcome to CHORD"
DB_FILE = "index.txt"
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
    "store": 4,
    "iterative_retrieve": 5,
    "recursive_retrieve": 6,
    "exist": 7,
    "client_connect": 8,
    "greeting": 9,
    "ack": 10,
    "nack": 11,
    "not_found": 12,
    "distribute_keys": 13,
    "save": 14,
    "heartbeat": 15,
    "survival": 16,
    "update_successor": 17
}

message_dictionary = {
    0: "join",
    1: "set_successor",
    2: "set_predecessor",
    3: "update_predecessor",
    4: "store",
    5: "iterative_retrieve",
    6: "recursive_retrieve",
    7: "exist",
    8: "client_connect",
    9: "greeting",
    10: "ack",
    11: "nack",
    12: "not_found",
    13: "distribute_keys",
    14: "save",
    15: "heartbeat",
    16: "survival",
    17: "update_successor"
}

