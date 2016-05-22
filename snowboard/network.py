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

from . import debug
from . import connection
from . import config
from . import channel
from . import nick

class Network:
    def __init__(self, cfg):
        self.config = cfg
        self.name = self.config.network
        self.__connection = None
        self.__authenticated = False
        self.channels = []
        self.nicks = []
    
    # Let the outside see if the bot is online.
    def online(self):
        if self.__connection == None:
            return False
        elif self.__authenticated == False:
            return False
        else:
            return self.__connection.connected
        
    # Connect to the network.    
    def connect(self):
        attempt = 0
        
        if self.__connection == None:
            connected = False
        else:
            connected = self.__connection.connected
        
        # Retry connecting until either the system is connected or none left
        while (not connected) and (attempt < len(self.config.servers)):
            attempt += 1
            for server in self.config.servers:
                debug.info("Attempting to connect to " + server.host + ":" + str(server.port) + ".")
                # Create the connection object, load settings from config
                self.__connection = connection.Connection(server)
                self.__connection.retries = self.config.retries
                self.__connection.delay = self.config.delay
                self.__connection.sslVerify = self.config.sslVerify
                
                # This setting is per-server, loaded from server object
                self.__connection.ssl = server.ssl
                
                # Try to connect, decide what to do next.
                if self.__connection.connect():
                    debug.message("Connected to " + server.host + ".")
                    continue
                else:
                    time.sleep(self.config.delay)
        
        return self.__connection.connected
    
    # Disconnect from the network.       
    def disconnect(self):
        if self.__connection.connected:
            debug.info("Connecting to server.")
            self.__connection.disconnect()
        else:
            debug.info("Not connected to server.")

        return self.__connection.connected
    
    # Authenticate with the network.
    def auth(self):
        debug.message("Attempting to authenticate.")
        
        # Some servers can be douchebags
        self.__authwait()
        # Begin authentication process.
        self.__connection.write("NICK " + self.config.botnick)
        # Some servers can be douchebags
        self.__authwait()        
        # Send user information.
        self.__connection.write("USER " + self.config.botnick + " 0 * :" + self.config.realname)
        
        # Wait for the server to signal that authentication is complete.
        while not self.__authenticated:
            data = self.__connection.read()
            if not type(data) == bool:
                line = data.split()
                if line[1] == "396":
                    debug.message("Authentication successful.")
                    self.__authenticated = True
    
    # Check for a ping to respond to.
    def __pingpong(self, message):
        line = message.split()
        if line[0] == "PING":
            pong = line[1].strip(':')
            self.connection.write("PONG :" + pong)
    
    # Some servers require that the client receive data before it can
    # authenticate, some even require a ping be responded to before
    # authenticating.  
    def __authwait(self):
        data = self.__connection.read()
        while not type(data) == bool:
            self.__pingpong(data)
            data = self.__connection.read()