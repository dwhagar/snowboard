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
Stores all information and functions related to a connection to a particular
network.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import time
import random
from os.path import isfile

from . import debug
from . import ctcpGlobals
from .connection import Connection
from .channel import Channel
from .nick import Nick
from .users import Users
from .channelPriv import ChannelPriv

class Network:
    def __init__(self, cfg):
        self.config = cfg

        self.botnick = self.config.botnick[:] # Copied, not just a reference
        self.channels = cfg.channels
        self.checkNext = 0
        self.delay = 0.25
        self.lastActivity = 0
        self.missedPings = 0
        self.name = self.config.network
        self.nextSend = 0
        self.nicks = []
        self.orphans = []
        self.pingNext = 0
        self.pingSent = 0
        self.pongReceived = 0
        self.queue = []
        self.quitting = False
        self.reconnect = True
        self.sendBlock = 6
        self.server = None
        self.users = Users(cfg.network)
        self.whoList = []
        self.__authenticated = False
        self.__connection = None
        self.__lastServer = 0  # The index of the last server connected

    def addChannel(self, chan):
        '''Add a channel to the network.'''
        existing = self.__checkChannels(chan.name)
        if existing is None:
            newChannel = Channel(chan, self.name)
            self.channels.append(newChannel)
            self.sendCommands(newChannel.join())
        else:
            if not existing.joined:
                self.sendCommands(existing.join())

    def addNick(self, nickName):
        '''Add a nick to the master list.'''
        existing = self.findNick(nickName)
        if existing is None:
            newNick = Nick(nickName, self.users)
            self.nicks.append(newNick)
            return newNick
        else:
            return existing

    def auth(self):
        '''Authenticate with the network.'''
        debug.message("Attempting to authenticate.")
        stage = 0 # What stage of authentication are we in?

        # Wait for the server to signal that authentication is complete.
        while (not self.__authenticated) and (self.__connection.connected()):
            if stage == 1: # Choose a nick to go by.
                # Begin authentication process.
                self.__connection.write("NICK " + self.botnick)
            elif stage == 2: # Send user information
                # Send user information.
                self.__connection.write("USER " + self.botnick.lower() + " 0 * :" + self.config.realname)

            stage += 1

            data = self.__connection.read()
            if not data is None:
                line = data.split()
                if line[1] == "001":
                    debug.message("Authentication successful.")
                    self.server = line[0]
                    self.__suppressMOTD() # Not really required
                    self.__authenticated = True
                    self.lastActivity = time.time()
                elif line[1] == "433":
                    # The nick we wanted was in use, must choose another one.
                    debug.message("Primary nick was taken, choosing a replacement.")
                    stage = 1
                    random.seed()
                    addition = str(random.randrange(10000,20000))
                    self.botnick += addition
                else:
                    self.__pingpong(data)

    def checkLag(self):
        '''Checks to see how much server lag there is.'''
        lag = self.pongReceived - self.pingSent

        debug.info("Server lag is at " + str(round(lag, 3)) + " seconds.")
        if lag > self.config.maxLag:
            debug.warn("Server lag is " + str(round(lag - self.config.maxLag, 3)) + " seconds longer than acceptable.  Disconnecting.")
            self.disconnect()

    def checkMessages(self):
        '''Check for new messages from the server.'''
        data = self.__connection.read()
        if not (data is None):
            self.__pingpong(data)
            if '\x01' in data:
                data = self.__processCTCP(data)
            self.lastActivity = time.time()

        return data

    def cleanNicks(self):
        '''
        Clean up the mast nick list, removing nicks that are no longer in
        a channel where the bot resides.
        '''
        # If a nick remains with an open who request after it has been
        # requested once (the last round) remove it from our list.
        for nickObject in self.orphans:
            if nickObject.openWHO:
                debug.info("Removing " + nickObject.name + " from the master list.")
                self.nicks.remove(nickObject)

        # Start with a clean list of orphans (nicks who are without channel)
        self.orphans = []

        # A flag to see if a nick was found.
        found = False

        # Search each nick in turn.
        for nickObject in self.nicks:
            # Search for each nick in each channel.
            for chanObject in self.channels:
                chanNick = chanObject.findNick(nickObject)

                # If we find it, set the flag, and break
                if not chanNick is None:
                    found = True
                    break
                else:
                    found = False

            # If the channels are all checked, and nothing found, remove it.
            if not found:
                debug.info("Found that " + nickObject.name + " was orphaned from any channels, checking online status.")
                self.orphans.append(nickObject)
                self.sendCommands(nickObject.sendWHO())

    def cleanTimer(self, time):
        '''Executes the Nick list cleaning every checkInterval seconds.'''
        commands = []

        # When initialized, set next time it will run.
        if self.checkNext == 0:
            debug.message("Initialized master nick cleaning timer.")
            self.checkNext = time + self.config.checkInterval
        elif self.checkNext == time:
            debug.info("Running cleaning routine for the master nicks list.")
            self.cleanNicks()
            self.checkNext = time + self.config.checkInterval

        return commands

    def ctcpPingReply(self, src):
        '''Replies to CTCP Ping Requests'''
        command = "PINGREPLY " + src + " :" + str(time.time())

        return [command]

    def connect(self):
        '''Connect to the network.'''
        if self.__connection is None:
            connected = False
        else:
            connected = self.__connection.connected()
            result = connected

        serverIndex = 0

        # Change the order of the servers so that the system reconnects to
        # the next server on the list if it has to reconnect, assuming there
        # is more than one server in the list.
        if (len(self.config.servers) > 0) and (self.__lastServer > 0):
            servers = self.config.servers[self.__lastServer:] + self.config.servers[:self.__lastServer]
        else:
            servers = self.config.servers[:]

        # Retry connecting until either the system is connected or none left
        while not connected:
            for server in servers:
                # Create the connection object, load settings from config
                self.__connection = Connection(server)
                self.__connection.retries = self.config.retries
                self.__connection.delay = self.config.delay
                self.__connection.sslVerify = self.config.sslVerify

                # Try to connect, decide what to do next.
                result = self.__connection.connect()
                if result:
                    debug.message("Connection to " + server.host + ":" + str(server.port) + " succeeded.")
                    self.__lastServer = serverIndex
                    break
                else:
                    serverIndex += 1
                    debug.message("Connection to " + server.host + ":" + str(server.port) + " failed.")

                time.sleep(self.config.delay)

            # If we aren't connected yet, display a message about it.
            if not result:
                debug.message("Connection failed, trying again in " + str(self.config.delay) + " seconds...")

            connected = result

        return result

    def disconnect(self):
        '''Disconnect from the server.'''
        if self.__connection.connected:
            debug.info("Disconnecting from server.")
            self.__connection.disconnect()
        else:
            debug.info("Cannot disconnect, not currently connected to server.")

        # Return the object to a disconnected state.
        self.__authenticated = False

        # There are no nicks to keep track of when disconnected.
        self.nicks = []
        self.orphans = []
        self.queue = []

        # There are no nicks in any channels while disconnected.
        for chan in self.channels:
            chan.botnick = None
            chan.joined = False
            chan.members = []
            chan.opped = False
            chan.voiced = False

        # Reset timers.
        self.missedPings = 0
        self.lastActivity = 0
        self.pingNext = 0
        self.checkNext = 0

        return self.__connection.connected

    def joinAll(self):
        '''Join all channels the bot is configured it.'''
        debug.message("Attempting to join all configured channels.")
        for channel in self.config.channels:
            self.addChannel(channel)

    def findChannel(self, channel):
        '''Find a channel in the networks channel list.'''
        result = None

        for existing in self.channels:
            if channel.lower() == existing.name.lower():
                result = existing
                break

        return result

    def findNick(self, nickName):
        '''Find a nick in the master list.'''
        result = None

        for existing in self.nicks:
            if nickName.lower() == existing.name.lower():
                result = existing
                break

        return result

    def online(self):
        '''Let the outside see if the bot is online.'''
        if self.__connection is None:
            return False
        else:
            return self.__connection.connected()

    def pingTimer(self, time):
        '''Pings the server to make sure it is still there.'''
        commands = []

        # Check when the last time a message was received by the server.
        timeout = self.lastActivity + self.config.pingInterval
        if time > timeout:
            # Execute the ping when time.
            if self.pingNext < time:
                debug.info("Pinging server " + self.server + " now.")
                commands.append("PING " + self.server)
                # Provide a mechanism to measure server lag as well.
                self.pingSent = time
                self.pingNext += self.config.pingInterval
                # One missed ping, notify the user.
                if self.missedPings > 0:
                    debug.warn("No ping response from server, continuing to try.")
                # Too many missed pings, disconnect.
                if self.missedPings > 2:
                    debug.error("No ping response from server for three consecutive tries, resetting connection.")
                    self.disconnect()
                self.missedPings += 1
        # If the timeout has not been reached, keep resetting the next time
        # a ping should be sent.
        else:
            # Initialize the timer.
            if self.pingNext == 0:
                debug.message("Initialized ping timer.")
                self.pingNext = time + self.config.pingInterval

        return commands

    def processJoinPart(self, response):
        '''Process a join or part message from the server.'''
        nck, host = self.__splitHostmask(response[0])
        if response[2][0] == ':':
            cJoined = response[2][1:]
        else:
            cJoined = response[2]

        # If the message is from the bot itself, then it means we need to
        # mark a channel as joined.
        if self.botnick.lower() == nck.lower():
            # We can assume that if we're getting a join about the bot, that
            # channel is in the list, so it will be found.
            chan = self.__checkChannels(cJoined)
            if response[1] == "JOIN":
                # Mark the channel as joined.
                debug.message("Successfully joined " + chan.name + ".")
                chan.joined = True
                chan.botnick = self.botnick
            elif response[1] == "PART":
                # Remove the channel if this is a part message.
                debug.message("Successfully parted from " + chan.name + ".")
                self.channels.remove(chan)
        # If the message is not about the bot, process it for a nick
        else:
            # Find the channel, retrieve the object, could put error check
            # but shouldn't be required, since the bot won't receive a
            # a message from a channel it isn't on (and thus is in its list)
            chanObject = self.findChannel(cJoined)

            # Process a join.
            if response[1] == "JOIN":
                nickObject = self.addNick(nck)
                nickObject.host = host
                nickObject.getPrivs()
                cPriv = ChannelPriv(False, False)
                chanObject.addNick(nickObject, cPriv)
                debug.message("Processed a join message on " + cJoined + " from " + nck + ".")

            # Process a part.
            elif response[1] == "PART":
                nickObject = self.findNick(nck)
                if not nickObject is None:
                    chanObject.removeNick(nickObject)
                debug.message("Processed a part message on " + cJoined + " from " + nck + ".")

    def processMode(self, response):
        '''Process a mode change.'''
        nickName, userHost = self.__splitHostmask(response[0])
        dest = response[2]
        modeChange = response[3]

        # This is pretty convoluted, but so are all the different ways you
        # can issue a mode change on IRC.
        if dest[0] == '#' and len(response) > 4:
            # Find the channel, prepare a list of targets from the message.
            chan = self.findChannel(dest)
            targets = response[4:]
            targetIndex = 0

            # Set some flags up, so we know if we're adding or subtracting
            # a particular mode, and if we know yet who we're doing it to.
            add = False
            sub = False
            op = False
            voice = False
            haveTarget = False

            # Go through the mode characters one at a time.
            for char in modeChange:
                # Set some flags, if we encounter a + or a - we know what is
                # going to happen to a mode, but have to wait for the mode
                # character to know what mode is being impacted.
                if char == '+':
                    add = True
                    sub = False
                elif char == '-':
                    add = False
                    sub = True
                # Since mode changes can be compounded, we need to look at
                # each character and set what is happening.
                elif char == 'o':
                    target = targets[targetIndex]
                    op = True
                    targetIndex += 1
                    haveTarget = True
                elif char == 'v':
                    target = targets[targetIndex]
                    voice = True
                    targetIndex += 1
                    haveTarget = True

                # If a target has been found, look up the target and access
                # that target channel / nick's privileges to modify.
                if haveTarget:
                    nck = self.findNick(target)
                    chanNick = chan.findNick(nck)

                    # Change the privileges flags for the nick in the channel
                    # since mode changes can be all a single change (add or
                    # subtract, keep the same add/sub flags until changed by
                    # a different mode character.
                    if add and op:
                        debug.info("Processed mode change on " + chan.name + " where " + nck.name + " was opped.")
                        chanNick[1].op = True
                        op = False
                    elif add and voice:
                        debug.info("Processed mode change on " + chan.name + " where " + nck.name + " was voiced.")
                        chanNick[1].voice = True
                        voice = False
                    elif sub and op:
                        debug.info("Processed mode change on " + chan.name + " where " + nck.name + " was deopped.")
                        chanNick[1].op = False
                        op = False
                    elif sub and voice:
                        debug.info("Processed mode change on " + chan.name + " where " + nck.name + " was devoiced.")
                        chanNick[1].voice = False
                        voice = False

                    # The target is no longer valid.
                    haveTarget = False

            # Update the bot itself at every mode change, so it knows where
            # it stands in the channel.
            chan.updateSelf()

    def processNames(self, response):
        '''
        Process a server response to a NAMES command, parse out the names
        for a given channel.
        '''
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
            nick = self.addNick(name)

            if nick.host is None or nick.host == "":
                self.sendCommands(nick.sendWHO())

            # Second, add the nick to the channel's nick list with privileges
            cPriv = ChannelPriv(opped, voiced)
            existing = self.findChannel(channelName)
            existing.addNick(nick, cPriv)

        existing.updateSelf()

        debug.info("Processed a list of names on " + channelName + ".")

    def processNick(self, response):
        '''Process a nick change.'''
        # Since the bot processes NAMES and JOINS messages, there should
        # never be a time when a NICK message comes in that it is not already
        # in the list.

        # If the bot's nick is the one that has changed, keep track.
        nickName, userHost = self.__splitHostmask(response[0])
        if response[2][0] == ':':
            response[2] = response[2][1:]
        if nickName.lower() == self.botnick.lower():
            self.botnick = response[2]
            for chan in self.channels:
                chan.botnick = self.botnick
        elif nickName.lower() == self.config.botnick.lower():
            self.sendCommands(["NICK " + self.config.botnick])
            debug.message("My default nick is no longer in use, changing nicks.")

        nickObject = self.findNick(nickName)
        nickObject.name = response[2]

        debug.info("Processed a nick change from " + nickName + " to " + response[2] + ".")

    def processTopic(self, response):
        '''Process channel topics.'''
        if response[1] == "332":
            chan = self.findChannel(response[3])
            data = response[4:]
        else:
            chan = self.findChannel(response[2])
            data = response[3:]

        if not chan is None:
            if data[0][0] == ":":
                chan.topic = " ".join(data[0:])[1:]
            else:
                chan.topic = " ".join(data[0:])

            debug.message("Processed channel topic for " + chan.name + ".")
        else:
            debug.message("Received a topic for unknown channel, " + response[2] + ".")

    def processQuit(self, response):
        '''
        Processes a quit message from the server to remove said user from
        the master nick list and all other lists.
        '''
        # Unpack the nick from the host, the host part isn't required
        nickName, host = self.__splitHostmask(response[0])

        # Find the nick in the master list.
        nickObject = self.findNick(nickName)

        # If that nick exists, remove it.
        if not nickObject is None:
            # Had to alter this so that the bot didn't think it was supposed
            # to change nicks when it was quitting IRC, mostly cosmetic.
            if nickObject.name == self.config.botnick and (not self.botnick.lower() == self.config.botnick.lower()):
                self.sendCommands(["NICK " + self.config.botnick])
                debug.message("My default nick is no longer in use, changing nicks.")

            # Remove the nick from all channel lists first.
            for chan in self.channels:
                chan.removeNick(nickObject)

            # Remove the nick from the master list last.
            self.nicks.remove(nickObject)

        debug.message("Processed a quit message from " + nickName + ".")

    def processWho(self, response):
        '''Process the server response from the WHO command.'''
        nick = self.findNick(response[7])
        nick.host = response[4] + "@" + response[5]
        nick.openWHO = False
        nick.user.uid = self.users.matchHost(nick.host)
        debug.info("Processed a WHO response for " + nick.name + "!" + nick.host + ".")

    def quit(self):
        '''Properly quit from the server.'''
        self.reconnect = False
        self.quitting = True
        self.sendCommands(["QUIT :" + self.config.quitmsg])

    def ready(self):
        '''Let the outside world see if the connection is ready.'''
        return self.__authenticated

    def removeAccess(self, uid):
        '''Removes access for a uid across all nicks.'''
        for nick in self.nicks:
            if nick.user.uid == uid:
                nick.clearPrivs()
                break

    def removeChannel(self, chan):
        '''Remove a channel from the network.'''
        existing = self.__checkChannels(chan.name)
        if not existing is None:
            if existing.joined:
                self.sendCommands(existing.part())

    def resetPrivs(self, uid):
        '''Resets the privileges of a user once they have changed.'''
        for nick in self.nicks:
            if nick.user.uid == uid:
                nick.getPrivs()

    def send(self):
        '''Actually send a certain number of commands from the queue.'''
        if len(self.queue):
            if time.time() > self.nextSend:
                # Send a couple of lines, then wait.
                for cmd in self.queue[:self.sendBlock]:
                    self.__connection.write(cmd)
                self.queue = self.queue[self.sendBlock:]

                # Set up the next time the Queue will be processed.
                self.delay += 0.25
                self.sendBlock -= 1
                self.nextSend = time.time() + self.delay

                # Once those lines are sent, delay longer before the next.
                if self.delay > 1.5:
                    self.delay = 1.5

                if self.sendBlock < 1:
                    self.sendBlock = 1
        # When there is nothing to send, reset the block size and delay.
        else:
            if time.time() > self.nextSend:
                if self.delay > 0.25:
                    self.delay -= 0.25
                if self.sendBlock < 6:
                    self.sendBlock += 1
                self.nextSend = time.time() + self.delay

    def sendCommands(self, list):
        '''Sends a list of commands to the server.'''
        encodedCommands = []

        for command in list:
            noAppend = False  # Some commands we don't want to actually queue
            cmdList = command.split()

            if len(cmdList) > 0:
                if cmdList[0].upper() in ctcpGlobals.queries:
                    command = "PRIVMSG " + cmdList[1] + " :" + ctcpGlobals.char + cmdList[0].upper() + " " + " ".join(
                        cmdList[2:]).strip(':') + ctcpGlobals.char
                elif cmdList[0].upper() in ctcpGlobals.replies:
                    cmdList[0] = ctcpGlobals.queries[ctcpGlobals.replies.index(cmdList[0]) + 1]
                    command = "NOTICE " + cmdList[1] + " :" + ctcpGlobals.char + cmdList[0].upper() + " " + " ".join(
                        cmdList[2:]).strip(':') + ctcpGlobals.char
                elif cmdList[0].upper() == "WHO":
                    if command in self.queue:
                        noAppend = True

            if not noAppend:
                command = command.replace("::B::", "\x02")
                command = command.replace("::I::", "\x1D")
                command = command.replace("::U::", "\x1F")
                command = command.replace("::R::", "\x16")
                command = command.replace("::P::", "\x0F")
                encodedCommands.append(command)

        # After encoding any CTCP messages, add them to the queue.
        self.queue += encodedCommands

    def sendFile(self, fileName, method, dest):
        '''Sends a file to a destination using a particular method.'''
        commands = []

        # The only valid values for method are PRIVMSG, ACTION, and NOTICE.
        msgPrefix = method.upper() + " " + dest + " :"

        if isfile(fileName):
            file = open(fileName)
            data = file.readlines()

            for message in data:
                message = message.strip('/r')
                message = message.strip('/n')

                if not (message == ""):
                    lines = self.splitMessage(message)
                    for line in lines:
                        commands.append(msgPrefix + line)

            file.close()

            if len(commands) > 0:
                self.sendCommands(commands)
        else:
            debug.error("Could not send file " + fileName + ", the file was not found.")
            self.sendCommands([msgPrefix + "That information could not be located.  Please contact the bot admin."])

    def splitMessage(self, message):
        '''Splits message text into multiple lines for transmission to IRC.'''
        lineList = [message]
        done = False

        while not done:
            newList = []
            for line in lineList:
                done = True
                if len(line) < 350:
                    newList.append(line)
                else:
                    limit = len(line) / 2
                    currLen = 0
                    newLine = ""

                    lineList = line.split()
                    for word in lineList:
                        if currLen <= limit:
                            newLine += word + " "
                        elif currLen > limit:
                            newList.append(newLine[:-1])
                            newLine = word + " "
                        currLen = len(newLine)

                    newList.append(newLine[:-1])

                    done = False

            lineList = newList

        return lineList

    def __authwait(self):
        '''
        Some servers require that clients receive data before it can auth
        with the server.  Some even require a ping be responded to before
        authenticating.  This takes care of that by waiting for the server
        to send something back, and responding to any pings that get sent.
        '''
        time.sleep(0.25) # Give the sever a chance to say something.
        data = self.__connection.read()
        while not data is None:
            self.__pingpong(data)
            data = self.__connection.read()

    def __checkChannels(self, channel):
        '''See if a channel already exists.'''
        result = None

        # Find if a channel exists already in the list.
        for chan in self.channels:
            if chan.name.lower() == channel.lower():
                result = chan
                break

        return result

    def __pingpong(self, message):
        '''Respond to a ping request.'''
        line = message.split()
        if line[0] == "PING":
            self.__connection.write("PONG " + line[1])

    def __processCTCP(self, data):
        '''Correctly handle CTCP message and responses.'''
        data = data.replace(ctcpGlobals.char, '')
        dataList = data.split()

        if dataList[1] == "PRIVMSG":
            ctcpReply = False
        elif dataList[1] == "NOTICE":
            ctcpReply = True

        ctcpCmd = dataList[3].strip(':')

        if ctcpReply and ctcpCmd in ctcpGlobals.queries:
            ctcpCmd = ctcpGlobals.replies[ctcpGlobals.queries.index(ctcpCmd) - 1]

        if len(dataList) > 4:
            data = dataList[0] + " " + ctcpCmd + " :" + " ".join(dataList[4:])
        else:
            data = dataList[0] + " " + ctcpCmd

        return data

    def __splitHostmask(self, hostmask):
        '''Split the hostname into host and nick.'''
        # Handle the leading ':' on messages, then split at the '!'
        hostmask = hostmask.split('!')
        if len(hostmask) < 2:
            hostmask.append("")
        return (hostmask[0], hostmask[1])

    def __suppressMOTD(self):
        '''Waits until the MOTD is done before going further.'''
        stillMOTD = True

        while stillMOTD:
            data = self.__connection.read()
            if not data is None:
                dataList = data.split()
                if len(dataList) > 1:
                    if dataList[1] == "376":
                        stillMOTD = False