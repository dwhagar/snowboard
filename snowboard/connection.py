# This file is part of snowboard.
# 
# snowboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# snowboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with snowboard.  If not, see <http://www.gnu.org/licenses/>.

import time
import socket
import ssl
import sys

from . import debug
from . import server

'''
Connection object, designed to be the only object to directly interface with
the server.
'''

class Connection:
    def __init__(self, srv):
        self.host = srv.host
        self.port = srv.port
        self.__socket = None
        self.__ssl = None
        self.__connected = False
        self.ssl = False
        self.sslVerify = True
        self.retries = 3           # Numbers of times to retry a connection
        self.delay = 1             # Delay between connection attempts
        
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
        while (not self.__connected) and (attempt < self.retries):
            # Attempt to establish a connection.
            try:
                self.__socket = socket.create_connection((self.host, self.port))
                
                # Handle SSL
                if self.ssl:
                    self.__context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    self.__context.options |= ssl.OP_NO_SSLv2
                    self.__context.options |= ssl.OP_NO_SSLv3
                    if self.sslVerify:
                        self.__context.verify_mode = ssl.CERT_REQUIRED
                    else:
                        self.__context.verify_mode = ssl.CERT_NONE
                    self.__ssl = self.__context.wrap_socket(self.__socket)
                    self.__ssl.setblocking(False)
                # Handle not SSL
                else:
                    self.__socket.setblocking(False)
                
                self.__connected = True
                self.error = ""
            
            # Assume connection errors are no big deal but do display an error.
            except ConnectionAbortedError:
                debug.error("Connection to "  + self.host + " aborted by server.")
            except ConnectionRefusedError:
                debug.error("Connection to " + self.host + " refused by server.")
            except TimeoutError:
                debug.error("Connection to " + self.host + " timed out.")
            except socket.gaierror:
                debug.error("Failed to resolve " + self.host + ".")
                
            attempt += 1
            
            time.sleep(self.delay)
        
        return self.__connected
    
    # Disconnect the socket.
    def disconnect(self):
        if ssl:
            self.__ssl.close()
            self.__ssl = None
        else:
            self.__socket.close()
        self.__socket = None
        self.__connected = False
    
    # Read information from the server, up to a new-line character.
    def read(self):
        # Keep track on if the loop should be done.
        done = False
        received = ""
        
        # Only do something if we're connected.
        if self.__connected:
            while not done:
                try:
                    if self.ssl:
                        data = self.__ssl.recv(1).decode('utf-8')
                    else:
                        data = self.__socket.recv(1).decode('utf-8')
                except (ssl.SSLWantReadError, BlockingIOError):
                    received = False
                    break
                
                # Process the data.
                # socket.recv is supposed to return a False if the connection
                # been broken.
                if not data:
                    self.error = "Disconnected"
                    self.disconnect()
                    done = True
                    received = False
                elif data == '\n':
                    done = True
                else:
                    received += data
        else:
            # Return false if the system is not connected.
            received = False
        
        # Remove the trailing carriage return character (cr/lf pair)
        if not type(received) == bool:
            received = received.strip('\r')
            debug.trace(received)
        
        return received
    
    # Send data to the server.
    def write(self, data):
        # Encode the data for the server.
        debug.trace(data)
        data += '\n'
        data = data.encode('utf-8')
        
        # Prepare to keep track of what is being sent.
        dataSent = 0
        bufferSize = len(data)
        
        if self.__connected:
            # Loop to send the data.
            while dataSent < bufferSize:
                if self.ssl:
                    sentNow = self.__ssl.send(data[dataSent:])
                else:
                    sentNow = self.__socket.send(data[dataSent:])
                
                # If nothing gets sent, we are disconnected from the server.
                if sentNow == 0:
                    self.error = "Disconnected"
                    self.disconnect()
                    sent = False
                
                # Keep track of the data.
                dataSent += sentNow
        else:
            sent = False
        
        # If sending completed, set the flag to true.
        if dataSent == bufferSize:
            sent = True
        
        return sent