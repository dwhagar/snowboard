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

from . import connection
from . import config
from . import channel
from . import nick

class Network:
    def __init__(self, cfg):
        self.config = cfg
        self.name = self.config.network
        self.__connection = None
        self.channels = []
        self.nicks = []
    
    # Let the outside see if the bot is online.
    def online(self):
        # TODO: Add exception handling for if the object has not yet been
        #       defined so that it will just return false.
        
        return self.__connection.connected

    
    # Connect to the network.    
    def connect(self):
        attempts = 0
        
        # Retry connecting until either the system is connected or none left
        while (not self.__connection.connected) and (attempts < len(self.config.servers)):
            attempt += 1
            
            for server in self.config.servers:
                # Create the connection object, load settings from config
                self.__connection = connection.Connection(server)
                self.__connection.retries = self.config.retries
                self.__connection.delay = self.config.delay
                self.__connection.sslVerify = self.config.sslVerify
                
                # This setting is per-server, loaded from server object
                self.__connection.ssl = server.ssl
                
                # Try to connect, decide what to do next.
                if self.__connection.connect():
                    continue
                else:
                    time.sleep(self.config.delay)
        
        return self.__connection.connected
    
    # Disconnect from the network.       
    def disconnect(self):
        if self.__connection.connected:
            self.__connection.disconnect()
                
        return self.__connection.connected