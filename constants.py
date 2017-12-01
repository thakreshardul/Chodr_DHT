BUFFER_SIZE = 1000
CLIENT_CLI_ARGUMENTS = 9
ROOT_CLI_ARGUMENTS = 7
PEER_CLI_ARGUMENTS = 9
PEER_CLI_ARGUMENTS_WITH_MODE = PEER_CLI_ARGUMENTS + 2
BACKLOG_FOR_TCP_SOCKET = 10
SOCKET_TIMEOUT = 10
GREETING_MESSAGE = "Hello"
DB_FILE = "index"

message_type = {
    "join": 0,
    "successor": 1,
    "predecessor": 2,
    "update_predecessor": 3
}

message_dictionary = {
    0: "join",
    1: "successor",
    2: "predecessor",
    3: "update_predecessor"
}
