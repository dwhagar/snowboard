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

from . import ctcpGlobals
from . import debug
from .logFile import LogFile

messages = ["PRIVMSG", "NOTICE"] + ctcpGlobals.queries + ctcpGlobals.replies
nonMessages = ["MODE", "JOIN", "PART", "QUIT", "NICK"]


class Logs:
    def __init__(self, network):
        self.channels = []
        self.messages = []
        self.network = network
        self.server = []

    def addChannel(self, channel):
        return self.__addList(self.channels, channel, True)

    def addMessage(self, source):
        return self.__addList(self.messages, source, False, True)

    def addServer(self, kind):
        return self.__addList(self.server, kind)

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

    def writeLog(self, message):
        global messages
        global nonMessages

        msgList = message.split()
        msgListLen = len(msgList)

        channel = False
        private = False

        if msgList[0].find("!") > 0:
            source = msgList[0].split("!")[0]
        else:
            source = msgList[0]

        if source[0] == ":":
            source = source[1:]

        if msgListLen > 2:
            if msgList[2][0] == "#":
                channel = True

            if msgList[1] in messages:
                messageData = " ".join(msgList[3:])
                if messageData[0] == ":":
                    messageData = messageData[1:]

                if not channel:
                    private = True

                if msgList[1] == "PRIVMSG":
                    logData = "<" + source + "> " + messageData
                elif msgList[1] == "NOTICE":
                    logData = "[NOTICE from " + source + "] " + messageData
                elif msgList[1] == "ACTION":
                    logData = " * " + source + " " + messageData
                elif (msgList[1] in ctcpGlobals.queries) or (msgList[1] in ctcpGlobals.replies):
                    logData = "[CTCP " + msgList[1] + " from " + source + "] " + messageData
            elif msgList[1] in nonMessages:
                if msgList[1] == "NICK":
                    logData = source + " changed their nick to " + msgList[3]
                elif msgList[1] == "MODE":
                    modeData = " ".join(msgList[3:])
                    logData = source + " changed modes " + modeData
                elif msgList[1] == "JOIN":
                    logData = source + " has joined " + msgList[2]
                elif msgList[1] == "PART":
                    logData = source + " has left " + msgList[2]
                    if msgListLen > 3:
                        partMsg = " ".join(msgList[3:])
                        logData += " with message '" + partMsg + "'"
                elif msgList[1] == "QUIT":
                    logData = source + " has quit IRC " + msgList[2]
                    if msgListLen > 3:
                        quitMsg = " ".join(msgList[3:])
                        logData += " with message '" + quitMsg + "'"
        elif msgListLen == 2:
            source = msgList[0]

            if source[0] == ":":
                source = source[1:]
            if msgList[1][0] == ":":
                msgList[1] = msgList[1][1:]

            logData = source + ": " + msgList[1]

        elif msgListLen == 1:
            debug.warn("I got a strange message from the server, not sure what it means: " + message)
            return

        if channel:
            log = self.addChannel(msgList[2])
        elif private:
            log = self.addMessage(source)
        else:
            log = self.addServer("status")

        log.writeLog(logData)

    def __addList(self, lst, item, channel = False, message = False):
        found = self.__findList(item)

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
