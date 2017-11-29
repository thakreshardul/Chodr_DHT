class ConnectionException(Exception):
    pass


class RootConnectException(ConnectionException):
    def __str__(self):
        return "Error connecting to root"
