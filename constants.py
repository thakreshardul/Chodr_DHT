BUFFER_SIZE = 1000
CLIENT_CLI_ARGUMENTS = 9
ROOT_CLI_ARGUMENTS = 7
PEER_CLI_ARGUMENTS = 9
PEER_CLI_ARGUMENTS_WITH_MODE = PEER_CLI_ARGUMENTS + 2
BACKLOG_FOR_TCP_SOCKET = 10

message_type = {
    "join": 0,
    "leave": 1,
    "store": 2,
    "retrieve": 3
}

message_dictionary = {
    0: "join",
    1: "leave",
    2: "store",
    3: "retreive"
}
