# Defines a server connection configuration, does not handle the actual
# connection, but provides settings such as name, port, and ssl options.
class Server:
    # Constructor
    def __init__(self, host, port = 6667):
        self.host = host
        self.port = port
