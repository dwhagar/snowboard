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

'''
Connection object, designed to be the only object to directly interface with
the server.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import time
import socket
import ssl
import sys

from . import debug
from . import server

class Connection:
    def __init__(self, srv):
        self.host = srv.host
        self.port = srv.port
        self.__socket = None
        self.__ssl = None
        self.__connected = False
        self.ssl = srv.ssl
        self.sslVerify = True
        self.retries = 3           # Numbers of times to retry a connection
        self.delay = 1             # Delay between connection attempts

    def connected(self):
        '''Returns the state of the connection.'''
        return self.__connected

    def connect(self):
        '''Connect to the configured server.'''
        # Keep track of attempts.
        attempt = 0

        # Try until the connection succeeds or no more tries are left.
        while (not self.__connected) and (attempt < self.retries):
            # Attempt to establish a connection.
            debug.message("Attempting connection to " + self.host + ":" + str(self.port) + ".")
            try:
                self.__socket = socket.setdefaulttimeout(30)
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

            # Assume connection errors are no big deal but do display an error.
            except ConnectionAbortedError:
                debug.error("Connection to " + self.host + " aborted by server.")
            except ConnectionRefusedError:
                debug.error("Connection to " + self.host + " refused by server.")
            except TimeoutError:
                debug.error("Connection to " + self.host + " timed out.")
            except socket.gaierror:
                debug.error("Failed to resolve " + self.host + ".")
            except OSError as err:
                debug.error("Failed to connect '" + err.errno + "' " + err.strerror + ".")

            attempt += 1

            time.sleep(self.delay)

        return self.__connected

    def disconnect(self):
        '''Disconnect from the server.'''
        debug.message("Disconnected from " + self.host + ":" + str(self.port) + ".")
        if ssl:
            if not self.__ssl is None:
                self.__ssl.close()
                self.__ssl = None
        else:
            if not self.__socket is None:
                self.__socket.close()
        self.__socket = None
        self.__connected = False

    def read(self):
        '''Read a line of data from the server, if any.'''
        # Only do something if we're connected.
        if self.__connected:
            done = False
            received = ""

            while not done:
                try:
                    if self.ssl:
                        data = self.__ssl.recv(1)
                    else:
                        data = self.__socket.recv(1)
                except (ssl.SSLWantReadError, BlockingIOError):
                    received = None
                    break
                except OSError as err:
                    debug.error("Error #" + str(err.errno) + ": '" + err.strerror + "' disconnecting.")
                    data = False

                # Process the data.
                # socket.recv is supposed to return a False if the connection
                # been broken.
                if not data:
                    self.disconnect()
                    done = True
                    received = None
                else:
                    text = data.decode('utf-8','replace')
                    if text == '\n':
                        done = True
                    else:
                        received += text

        else:
            received = None

        # Remove the trailing carriage return character (cr/lf pair)
        if not received is None:
            received = received.strip('\r')
            if len(received) > 0:
                if received[0] == ':':
                    received = received[1:]

        # Bug fix for Issue #18, do not return blank lines.
        if received == "":
            received = None

        return received

    def write(self, data):
        '''Sends data to the server.'''
        # Encode the data for the server.
        data += '\n'
        data = data.encode('utf-8')

        # Prepare to keep track of what is being sent.
        dataSent = 0
        bufferSize = len(data)

        if self.__connected:
            # Loop to send the data.
            while dataSent < bufferSize:
                try:
                    if self.ssl:
                        sentNow = self.__ssl.send(data[dataSent:])
                    else:
                        sentNow = self.__socket.send(data[dataSent:])
                except OSError as err:
                    debug.error("Error #" + str(err.errno) + ": '" + err.strerror + "' disconnecting.")
                    self.disconnect()
                    return False

                # If nothing gets sent, we are disconnected from the server.
                if sentNow == 0:
                    debug.error("Data could not be sent for an unknown reason, disconnecting.")
                    self.disconnect()
                    return False

                # Keep track of the data.
                dataSent += sentNow
        else:
            sent = False

        # If sending completed, set the flag to true.
        if dataSent == bufferSize:
            sent = True

        return sent