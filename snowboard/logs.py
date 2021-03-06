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
Provides a method for the bot to log information to individual files.
'''
import time
from . import ctcpGlobals
from . import debug
from .logFile import LogFile

messages = ["PRIVMSG", "NOTICE"] + ctcpGlobals.queries + ctcpGlobals.replies
nonMessages = ["MODE", "JOIN", "PART", "QUIT", "NICK"]


class Logs:
    def __init__(self, network, nick):
        self.channels = []
        self.messages = []
        self.network = network
        self.server = []
        self.nick = nick
        self.cycled = False

    def addChannel(self, channel):
        return self.__addList(self.channels, channel, True)

    def addMessage(self, source):
        return self.__addList(self.messages, source, False, True)

    def addServer(self, kind):
        return self.__addList(self.server, kind)

    def clearAll(self):
        self.channels = []
        self.messages = []
        self.server = []

    def cycle(self):
        self.clearAll()
        self.cycled = True

    def delChannel(self, channel):
        self.__delList(self.channels, channel)

    def delMessage(self, source):
        self.__delList(self.messages, source)

    def delServer(self, kind):
        self.__delList(self.server, kind)

    def findChannel(self, channel):
        return self.__findList(self.channels, channel)

    def findMessage(self, source):
        return self.__findList(self.messages, source)

    def findServer(self, kind):
        return self.__findList(self.messages, kind)

    def write(self, logData, name = "status", channel = False, private = False):
        if channel:
            log = self.addChannel(name)
        elif private:
            log = self.addMessage(name)
        else:
            log = self.addServer(name)

        t = time.time()
        s = time.localtime(t)
        ms = format(t - int(t), '1.3f')[1:]
        timePrefix = "[" + time.strftime("%y/%m/%d %H:%M:%S", s) + ms + "] "

        if name == "motd":
            log.writeLog(logData)
        else:
            log.writeLog(timePrefix + logData)

    def writeRecv(self, message):
        global messages
        global nonMessages

        msgList = message.split()
        msgListLen = len(msgList)

        name = "status"
        channel = False
        private = False
        logData = ""

        if msgList[0].find("!") >= 0:
            source = msgList[0].split("!")[0]
        else:
            source = msgList[0]

        if source[0] == ":":
            source = source[1:]

        if msgListLen > 2:
            if msgList[2][0] == "#":
                channel = True
                name = msgList[2]

            if msgList[1] in messages:
                messageData = " ".join(msgList[3:])
                if messageData[0] == ":":
                    messageData = messageData[1:]

                if not channel:
                    private = True
                    name = source

                if msgList[1] == "PRIVMSG":
                    logData = "<" + source + "> " + messageData
                elif msgList[1] == "NOTICE":
                    if msgList[0].find("!") < 0:
                        name = "status"
                        private = False
                    logData = "[NOTICE from " + source + "] " + messageData
                elif msgList[1] == "ACTION":
                    logData = " * " + source + " " + messageData
                elif (msgList[1] in ctcpGlobals.queries) or (msgList[1] in ctcpGlobals.replies):
                    logData = "[CTCP " + msgList[1] + " from " + source + "] " + messageData
            elif msgList[1] in nonMessages:
                if msgList[2][0] == ":":
                    msgList[2] = msgList[2][1:]
                if msgList[1] == "NICK":
                    logData = source + " changed their nick to " + msgList[2]
                elif msgList[1] == "MODE":
                    modeData = " ".join(msgList[3:])
                    logData = source + " changed modes " + modeData
                elif msgList[1] == "JOIN":
                    logData = source + " has joined " + msgList[2]
                elif msgList[1] == "PART":
                    logData = source + " has left " + msgList[2]
                    if msgListLen > 3:
                        partMsg = " ".join(msgList[3:])
                        if partMsg[0] == ":":
                            partMsg = partMsg[1:]
                        logData += " with message '" + partMsg + "'"
                elif msgList[1] == "QUIT":
                    quitMsg = " ".join(msgList[2:])
                    logData = source + " has quit IRC  with message '" + quitMsg + "'"
            else:
                if message[0] == ":":
                    message = message[1:]

                if msgList[1] == "375" or msgList[1] == "372" or msgList[1] == "376":
                    name = "motd"

                    motdStart = message.find(':')

                    if motdStart >= 0:
                        logData = message[motdStart + 1:]
                    else:
                        logData = message
                else:
                    logData = message

        elif msgListLen == 2:
            logData = message

        elif msgListLen == 1:
            debug.warn("I got a strange message from the server, not sure what it means: " + message)
            return

        if len(logData) > 0:
            self.write(logData, name, channel, private)

    def writeSent(self, message):
        global messages
        global nonMessages

        msgList = message.split()
        msgListLen = len(msgList)
        prefix = ">> "
        logData = ""
        dest = "status"
        channel = False
        private = False

        if msgListLen > 2:
            if msgList[1][0] == "#":
                channel = True
                dest = msgList[1]

            data = " ".join(msgList[2:])
            if data[0] == ":":
                data = data[1:]

            if msgList[0].upper() in messages:
                if not channel:
                    private = True
                    dest = msgList[1]

                if msgList[0].upper() == "PRIVMSG":
                    logData = prefix + "<" + self.nick + "> " + data
                elif msgList[0].upper() == "ACTION":
                    logData = prefix + "* " + self.nick + " " + data
                elif msgList[0].upper() == "NOTICE":
                    logData = prefix + "[NOTICE to" + dest + "] " + data
                elif msgList[0].upper() in ctcpGlobals.queries or msgList[0].upper() in ctcpGlobals.replies:
                    logData = prefix + "[" + msgList[0].upper() + " to " + dest + "] " + data
            else:
                logData = prefix + message

        elif msgListLen > 0:
            logData = prefix + message

        if len(logData) > 0:
            self.write(logData, dest, channel, private)

    def __addList(self, lst, item, channel = False, message = False):
        found = self.__findList(lst, item)

        if found is None:
            newLog = LogFile(self.network, item, channel, message)
            lst.append(newLog)
            return newLog
        else:
            return found

    def __delList(self, lst, item):
        found = self.__findList(lst, item)

        if not (found is None):
            lst.remove(found)

    def __findList(self, lst, item):
        found = None
        for listItem in lst:
            if listItem.name == item.lower():
                found = listItem
                break

        return found
