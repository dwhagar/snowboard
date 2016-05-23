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
        else:
            return self.__connection.connected()
            
    # Let the outside world see if the connection is ready.
    def ready(self):
        return self.__authenticated
        
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
                # Create the connection object, load settings from config
                self.__connection = connection.Connection(server)
                self.__connection.retries = self.config.retries
                self.__connection.delay = self.config.delay
                self.__connection.sslVerify = self.config.sslVerify
                
                # This setting is per-server, loaded from server object
                self.__connection.ssl = server.ssl
                
                # Try to connect, decide what to do next.
                result = self.__connection.connect()
                
                if result:
                    debug.message("Connected to " + server.host + ".")
                    continue
                else:
                    time.sleep(self.config.delay)
        
        return result
    
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
                self.__pingpong(data)
                line = data.split()
                if line[1] == "396":
                    debug.message("Authentication successful.")
                    self.__authenticated = True
    
    # Respond to a ping.
    def __pingpong(self, message):
        line = message.split()
        print(line)
        if line[0] == "PING":
            self.__connection.write("PONG " + line[1])
    
    # Some servers require that the client receive data before it can
    # authenticate, some even require a ping be responded to before
    # authenticating.  
    def __authwait(self):
        data = self.__connection.read()
        while not type(data) == bool:
            self.__pingpong(data)
            data = self.__connection.read()
    
    # Send a list of commands to the server.
    def sendCommands(self, list):
        for cmd in list:
            self.__connection.send(cmd)
    
    # Check for new messages from server.
    def checkMessages(self):
        data = self.__connection.read()
        if type(data) == bool:
            return False
        else:
            self.__pingpong(data)
            return data
    
    # See if a channel already exists.
    def __checkChannels(self, channel):
        # Return False if no channel is found.
        result = False
        
        # Find if a channel exists already in the list.
        for chan in self.channels:
            if chan.name.lower() == channel.lower():
                result = chan
                break
        
        return result
    
    # Add a channel to the network.        
    def addChannel(self, chan):
        existing = self.__checkChannels(chan)
        if type(existing) == bool:
            newChannel = channel.Channel(chan)
            self.sendCommands(newChannel.join())
            self.channels.append(newChannel)
        else:
            if not existing.joined:
                self.sendCommands(existing.join())
        
    # Remove a channel from the network.
    def removeChannel(self, chan):
        existing = self.__checkChannels(channel)
        if not (type(existing) == bool):
            if existing.joined:
                self.sendCommands(existing.part())
    
    # Process a join message, show channel as joined
    def processJoinPart(self, response):
        # Get the hostmask, then from that get the nick for the join
        hostmask = response[0].split('!')
        nick = hostmask[0]
        
        # If the message is from the bot itself, then it means we need to
        # mark a channel as joined.
        if botnick.lower() == nick.lower():
            # We can assume that if we're getting a join about the bot, that
            # channel is in the list, so it will be found.
            chan = self.__checkChannels(response[2])
            if response[1] == "JOIN":
                # Mark the channel as joined.
                debug.message("Successfully joined " + chan.name + ".")
                chan.joined = True
            elif response[1] == "PART":
                # Remove the channel if this is a part message.
                debug.message("Successfully parted from " + chan.name + ".")
                self.channels.remove(chan)
        else:
            # TODO: Write code to process other nicks and reference
            #       the nick and channel lists.
            pass

    # Join all channels.
    def joinAll(self):
        for channel in self.config.channels:
            self.addChannel(channel)