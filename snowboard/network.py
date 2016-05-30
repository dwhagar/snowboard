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
from . import users

'''
Stores all information and functions related to a connection to a particular
network.

///Data///
.config
A Config objet to store all configuration options to do with this network.

.name
The name of the network.

.channels
A list of Channel objects that the bot is configured with.

.nicks
A list of Nick objects, all nicks for which the bot is aware, this is a
global list and encompases all nicks on all channels.

.users
A User object to provide an interface to the user database.  This particular
object interfaces with the global database table and is also used by the
Nick objects within the nicks list.

///Constructor///
Network(cfg)
Acceepts one input, that of a Config object.  The object is required, it
contains all of the configuration options that the bot needs to know what
to do on the network configured within.

///Methods///
.online()
Returns a boolean value for if the bot is currently connected to an IRC
server.

.ready()
Returns a boolean value to see if the connection to the IRC server is ready
to accept commands, constitutes if the bot is authenticated with the IRC
network or not.

.connect()
Instructs the bot to connect to the IRC network.

.quit()
Instructs the bot to send a QUIT command back to the IRC network, the system
should then stay online until the IRC network responds that it is closing the
link.

.disconnect()
Disconnects from the IRC network.  This is a hard disconnect and simply
closes the socket connection without sending a QUIT command, thus the
connection is closed immidiately.  This may result in a "Ping Timeout" or a
"Connection Reset by Peer" error for the bot on the IRC network.

.auth()
Authenticates with the IRC network.  Most networks can only accept
authentication commands once they have sent some data, usually a NOTICE
that the system is looking up either hostname or ident information (or both).

Some servers also send a PING command back to the system to verify that the
connection is live and that a proper IRC client exists on the other end.
Should the server not receive a proper PONG response prior to authentication
commands are sent, the connection will be terminated.

.sendCommands(list)
Sends commands to the IRC server.
Accepts one input
list
A list of commands to be sent to the server.

Some commands are directives intended for the bot and not for the IRC server
itself are surrounded by *'s, the bot will redirect these and call the
appropriate function to translate these directives into a list of commands
for the server.

Current list of directives:
*QUIT*
Instructs the bot to QUIT from the server properly.

.checkMessages()
Instructs the bot to check to see what messages are in the buffer waiting to
be processed.  This method also deals with the PING/PONG call and response
from the server, to keep the connection alive.  Even though the bot responds
to PING's here, it will still send a PING back to the calling function so any
additional tasks can be completed.

.addChannel(chan)
Instructs the bot to add a channel to its list of channels.  Once added if
the channel is not joined, it will get the join command from the object and
sent it to the server.

If the channel is already in the database, the existing Channel object is
instead used.

Accepts one input.
chan
A Channel object.

.removeChannel(chan)
Instructs the bot to remove a channel from its list.  If the bot has joined
the channel, then the commands are sent to the server to part from that
channel.

Accepts one input.
chan
A channel object.

.processJoinPart(reponse)
Processes a JOIN or PART message from the server.  This function is
responsible for telling the network that a channel is joined or a part
command has been successful by the bot as well as processing new people join
or leave the channel.

Takes one input.
response
A list of strings which represents the JOIN response from the server, already
split.

.cleanNicks()
Cleans out nicks from the master list which no longer reside on any channels.

.processQuit(response)
Processes a QUIT message sent from the server.  The function removes the
nick from all channels and from the master list as well.

Takes one input.
response
A list of strings which represents the QUIT response from the server, already
split.

.processWho(response)
Process a WHO response from the server to get the host information for a
particualr Nick object.

Takes one input.
response
A list of strings which represents the WHO response from the server, already
split.

.processNames(response)
Process a NAMES response from the server to fill in the names and basic privs
of everyone in a channel.  This will check to see if a Nick is already in the
master list as well as a channel's members list and add to both when missing
if it finds the Nick object, it will use the existing object.

Takes one input.
response
A list of strings which represents the NAMES response from the server,
already split.

.joinAll()
Instructs the bot to join all channels which it is confiugred for.
'''

class Network:
    def __init__(self, cfg):
        self.config = cfg
        self.name = self.config.network
        self.__connection = None
        self.__authenticated = False
        self.channels = cfg.channels
        self.nicks = []
        self.users = users.Users(cfg.network)
    
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
        while (not self.__authenticated) and (self.__connection.connected()):
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
        result = None
        
        # Find if a channel exists already in the list.
        for chan in self.channels:
            if chan.name.lower() == channel.lower():
                result = chan
                break
        
        return result
    
    # Add a channel to the network.        
    def addChannel(self, chan):
        existing = self.__checkChannels(chan.name)
        if existing == None:
            newChannel = channel.Channel(chan, self.name)
            self.channels.append(newChannel)
            self.sendCommands(newChannel.join())
        else:
            if not existing.joined:
                self.sendCommands(existing.join())
        
    # Remove a channel from the network.
    def removeChannel(self, chan):
        existing = self.__checkChannels(chan.name)
        if not existing == None:
            if existing.joined:
                self.sendCommands(existing.part())
    
    # Split the hostmask into host and nick.
    def __splitHostmask(self, hostmask):
        # Handle the leading ':' on messages, then split at the '!'
        hostmask = hostmask.split('!')
        return (hostmask[0], hostmask[1])
    
    # Process a join message, show channel as joined
    def processJoinPart(self, response):
        nck, host = self.__splitHostmask(response[0])
        if response[2][1] == ':':
            cJoined = response[2][1:]
        else:
            cJoined = response[2]
        
        # If the message is from the bot itself, then it means we need to
        # mark a channel as joined.
        if self.config.botnick.lower() == nck.lower():
            # We can assume that if we're getting a join about the bot, that
            # channel is in the list, so it will be found.
            chan = self.__checkChannels(cJoined)
            if response[1] == "JOIN":
                # Mark the channel as joined.
                debug.message("Successfully joined " + chan.name + ".")
                chan.joined = True
            elif response[1] == "PART":
                # Remove the channel if this is a part message.
                debug.message("Successfully parted from " + chan.name + ".")
                self.channels.remove(chan)
        # If the message is not about the bot, process it for a nick
        else:
            # Find the channel, retrieve the object, could put error check
            # but shouldn't be required, since the bot won't receive a
            # a message from a channel it isn't on (and thus is in its list)
            chanObject = self.__findChannel(cJoined)
            
            # TODO:  Get the bot to pull the hostname out of the join message
            #        and apply it to the Nick object.
            
            # Process a join.
            if response[1] == "JOIN":
                nickObject = self.__addNick(nck)
                cPriv = channel.ChannelPriv(False, False)
                chanObject.addNick(nickObject, cPriv)
                debug.message("Processed a join message on " + cJoined + " from " + nck + ".")
            
            # TODO:  Adjust this so that a nick remains authenticated a
            #        certain amount of time after they have left all
            #        channels.  This will require modifying the loop in main
            #        as well to clear out Nick objects from the master
            #        list on a timer.
            
            # Process a part.
            elif response[1] == "PART":
                nickObject = self.__findNick(nck)
                if not nickObject == None:
                    chanObject.removeNick(nickObject)
                    self.cleanNicks()
                debug.message("Processed a part message on " + cJoined + " from " + nck + ".")
    
    # Clean up the master nicks list, removing nicks no longer in channels.
    def cleanNicks(self):
        # A flag to see if a nick was found.
        found = False
        
        # Search each nick in turn.
        for nickObject in self.nicks:
            # Search for each nick in each channel.
            for chanObject in self.channels:
                chanNick = chanObject.findNick(nickObject)
                
                # If we find it, set the flag, and break
                if not chanNick == None:
                    found = True
                    break
            
            # If the channels are all checked, and nothing found, remove it.
            if not found:
                self.nicks.remove(nickObject)
    
    # If a user quits, remove them from the master list and all other lists.
    def processQuit(self, response):
        # Unpack the nick from the host, the host part isn't required
        nickName, host = self.__splitHostmask(response[0])
        
        # Find the nick in the master list.
        nickObject = self.__findNick(nickName)
        
        # If that nick exists, remove it.
        if not nickObject == None:
        
            # Remove the nick from all channel lists first.
            for chan in self.channels:
                chan.removeNick(nickObject)
                
            # Remove the nick from the master list last.
            self.nicks.remove(nickObject) 
            
        debug.message("Processed a quit message from " + nickName + ".")           
    
    # Find a nick in the list.
    def __findNick(self, nickName):
        result = None
        
        for existing in self.nicks:
            if nickName.lower() == existing.name.lower():
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
            newNick = nick.Nick(nickName, self.users)
            self.nicks.append(newNick)
            return newNick
        else:
            return existing
    
    # Parse out a hostname from a WHO response
    def processWho(self, response):
        nick = self.__findNick(response[4])
        nick.host = response[5]
        debug.message("Processed a WHO response for " + nick.name + "!" + nick.host + ".")
    
    # Parse out the names response.
    def processNames(self, response):
        # Whittle down to just a list of names, with privs still attached
        channelName = response[4]
        names = response[5:]
        names[0] = names[0][1:]
        
        # Go through each name, progressively building its privs and adding
        # each name to the channel list and the master list.
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
            
        debug.message("Processed a list of names on " + channelName + ".")
    
    # Process a nick change, even if the bot itself changes nicks.
    def processNick(self, response):
        # Since the bot processes NAMES and JOINS messages, there should
        # never be a time when a NICK message comes in that it is not already
        # in the list.
        nickName, userHost = self.__splitHostmask(response[0])
        nickObject = self.__findNick(nickName)
        nickObject.name = response[2]
        
        debug.message("Processed a nick change from " + nickName + " to " + response[2] + ".")
    
    # Join all channels.
    def joinAll(self):
        debug.message("Attempting to join all configured channels.")
        for channel in self.config.channels:
            self.addChannel(channel)