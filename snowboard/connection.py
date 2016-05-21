import time
import socket

'''
Connection object, designed to be the only object to directly interface with
the server.
'''

class Connection:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = Socket()
        self.__connected = False
        self.error = ""            # Later this will contain the laste error
        self.retries = 3           # Numbers of times to retry a connection
        self.delay = 0.5           # Delay between connection attempts
    
    # Read-only, these should be set when the connection is created.
    def host(self):
        return self.__host
    
    def port(self):
        return self.__port
    
    # The connection object should be the only one to change if it is in a
    # connected state.
    def connected(self):
        return self.__connected
    
    # Connect to the perscribed host and the proper port, retries with a pause
    # until the configured limit is reached.
    def connect(self):
        # Keep track of attempts.
        attempt = 0
        
        # Try until the connection succeeds or no more tries are left.
        while self.__connected == False and attempt <= self.retries:
            try:
                self.__socket.create_connection((self.__host, self.__port))
                self.__connected = True
            except:
                pass # TODO:  Put code here to identify unrecoverable
                     #        conneciton problems.
            # Delay a certain amount of time between attempts.
            time.sleep(self.delay)
        
        return self.__connected
    
    def disconnect(self):
        self.__socket.close()
        self.__connected = False
    