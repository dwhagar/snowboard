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
        self.channels = cfg.channels
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
    
    # Properly quit from the server.
    def quit(self):
        self.sendCommands(["QUIT " + self.config.quitmsg])
    
    # Disconnect from the network.       
    def disconnect(self):
        if self.__connection.connected:
            debug.info("Disconnecting from server.")
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
            if not data == None:
                self.__pingpong(data)
                line = data.split()
                if line[1] == "396":
                    debug.message("Authentication successful.")
                    self.__authenticated = True
    
    # Respond to a ping.
    def __pingpong(self, message):
        line = message.split()
        if line[0] == "PING":
            self.__connection.write("PONG " + line[1])
    
    # Some servers require that the client receive data before it can
    # authenticate, some even require a ping be responded to before
    # authenticating.  
    def __authwait(self):
        time.sleep(0.25) # Give the sever a chance to say something.
        data = self.__connection.read()
        while not data == None:
            self.__pingpong(data)
            data = self.__connection.read()
    
    # Send a list of commands to the server.
    def sendCommands(self, list):
        for cmd in list:
            if cmd == "*QUIT*":
                self.quit()
            else:
                self.__connection.write(cmd)
    
    # Check for new messages from server.
    def checkMessages(self):
        data = self.__connection.read()
        if not (data == None):
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
        existing = self.__checkChannels(chan.name)
        if type(existing) == bool:
            newChannel = channel.Channel(chan)
            self.sendCommands(newChannel.join())
            self.channels.append(newChannel)
        else:
            if not existing.joined:
                self.sendCommands(existing.join())
        
    # Remove a channel from the network.
    def removeChannel(self, chan):
        existing = self.__checkChannels(chan.name)
        if not (type(existing) == bool):
            if existing.joined:
                self.sendCommands(existing.part())
    
    # Process a join message, show channel as joined
    def processJoinPart(self, response):
        # Get the hostmask, then from that get the nick for the join
        hostmask = response[0].split('!')
        nck = hostmask[0] # the name nick will conflict with the object
        
        # If the message is from the bot itself, then it means we need to
        # mark a channel as joined.
        if self.config.botnick.lower() == nck.lower():
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
            if response[1] == "JOIN":
                nickObject = self.__addNick(nck)
                cPriv = channel.ChannelPriv(False, False)
                cJoined = response[2]
                chanObject = self.__findChannel(cJoined)
                chanObject.addNick(nickObject, cPriv)
            elif response[1] == "PART":
                nickObject = self.__findNick(nick)
                if not nickObject == None:
                    pass # Bookmark
    
    # Find a nick in the list.
    def __findNick(self, nick):
        result = None
        
        for existing in self.nicks:
            if nick.lower() == existing.name.lower():
                result = existing
                break
        
        return result
        
    def __findChannel(self, channel):
        result = None
        
        for existing in self.channels:
            if channel.lower() == existing.name.lower():
                result = existing
                break
                
        return existing
    
    # Add a nick to the list.
    def __addNick(self, nickName):
        existing = self.__findNick(nickName)
        if existing == None:
            newNick = nick.Nick(nickName)
            self.nicks.append(newNick)
            return newNick
        else:
            return existing
    
    # Parse out a hostname from a WHO response
    def processWho(self, response):
        nick = self.__findNick(response[4])
        nick.host = response[5]
    
    # Parse out the names response.
    def processNames(self, response):
        # Whittle down to just a list of names, with privs still attached
        channelName = response[4]
        names = response[5:]
        names[0] = names[0][1:]
        for name in names:
            # Recognized channel privileges
            opped = False
            voiced = False
            
            if name[0] == '@':
                opped = True
                name = name[1:]
            elif name[0] == '+':
                voiced = True
                name = name[1:]
            
            # First, add the nick to the master list.
            nick = self.__addNick(name)
            if nick.host == "":
                self.sendCommands(nick.getHost())
            
            # Second, add the nick to the channel's nick list with privileges
            cPriv = channel.ChannelPriv(opped, voiced)
            existing = self.__findChannel(channelName)
            existing.addNick(nick, cPriv)
    
    # Join all channels.
    def joinAll(self):
        for channel in self.config.channels:
            self.addChannel(channel)