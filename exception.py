class ConnectionException(Exception):
    pass


class BindException(ConnectionException):
    def __str__(self):
        return "Error in Bind call"


class RootConnectException(ConnectionException):
    def __str__(self):
        return "Error connecting to root"


class ClientReceiveException(ConnectionException):
    def __str__(self):
        return "Error reading data"


class ClientSendException(ConnectionException):
    def __str__(self):
        return "Error sending data"


class PeerReceiveException(ConnectionException):
    def __str__(self):
        return "Error receiving data"


class PeerSendException(ConnectionException):
    def __str__(self):
        return "Error sending data"


class ConnectionAcceptException(ConnectionException):
    def __str__(self):
        return "Error Accepting connection request"


class ConnectionListenException(ConnectionException):
    def __str__(self):
        return "Error listening for conncection"


class TypeException(ConnectionException):
    def __str__(self):
        return "Error in message type"


class DataException(ConnectionException):
    def __str__(self):
        return "Error in extracting data"