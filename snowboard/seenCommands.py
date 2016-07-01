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
Processes triggers for the seen module.
'''

import re
import datetime
import time
from .seen import Seen

def chanTriggers(ircMsg):
    '''Processes channel queries for the seen module.'''
    commands = []

    if ircMsg.dataList[0].lower() == "!seen":
        commands = __seenQuery(ircMsg)
    if ircMsg.dataList[0].lower() == "!trace" and ircMsg.dataList[1].lower() == "nick":
        commands = __traceNick(ircMsg)

    return commands

def rawTriggers(net, message):
    '''Processes raw message triggers.'''
    dbTriggerA = r"^(.*)!(.*@.*) (PRIVMSG|PART) (#.*) :(.*)$"
    dbTriggerB = r"^(.*)!(.*@.*) (QUIT) :(.*)$"
    dbTriggerC = r"^(.*)!(.*@.*) (JOIN|PART) (#.*)$"

    searchA = re.compile(dbTriggerA, re.IGNORECASE)
    searchB = re.compile(dbTriggerB, re.IGNORECASE)
    searchC = re.compile(dbTriggerC, re.IGNORECASE)

    seen = Seen(net.name)

    if searchA.match(message):
        # Process joins and parts that have messages.
        data = searchA.split(message)

        nick = data[1]
        host = data[2]
        dest = data[4]
        msg = data[5]

        if data[3] == "PRIVMSG":
            act = "on " + dest + " saying '" + msg + "'"
        elif data[3] == "PART":
            act = "leaving " + dest + " with message '" + msg + "'"

        seen.save(nick, host, act)
    elif searchB.match(message):
        # Process quit messages.
        data = searchB.split(message)

        nick = data[1]
        host = data[2]
        msg = data[4]

        act = "leaving IRC with message '" + msg + "'"

        seen.save(nick, host, act)
    elif searchC.match(message):
        data = searchC.split(message)

        nick = data[1]
        host = data[2]
        dest = data[4]

        if data[3] == "JOIN":
            act = "joining " + dest
        elif data[3] == "PART":
            act = "leaving " + dest

        seen.save(nick, host, act)
    else:
        messageList = message.split()
        if messageList[1] == "352":
            host = messageList[4] + "@" + messageList[5]
            nick = messageList[7]
            act = "online"
            seen.save(nick, host, act)
    return


def __removeItem(list, text):
    '''Removes an string from a list, not paying attention to case.'''
    index = 0
    for item in list:
        if text.lower() in map(str.lower, list):
            list.pop(index)
        index += 1

    return list

def __seenQuery(ircMsg):
    '''Query the seen database.'''
    commands = []

    if not ((ircMsg.dataList[1].lower() == ircMsg.net.botnick.lower()) or (
        ircMsg.src.lower() == ircMsg.dataList[1].lower())):
        seen = Seen(ircMsg.net.name)

        nicks, hosts = seen.nickSearch(ircMsg.dataList[1])
        lastTime, lastNick, lastHost, lastAct = seen.timeSearch(nicks, hosts)

        timeDiff = round(time.time()) - round(lastTime)
        delta = datetime.timedelta(seconds = timeDiff)

        if (delta.days == 0) and (delta.seconds < 1):
            ago = "less than a second"
        else:
            ago = str(delta)

        isHere = ircMsg.net.findNick(lastNick)

        if isHere is None:
            if lastNick.lower() == ircMsg.dataList[1].lower():
                commands.append(
                    "PRIVMSG " + ircMsg.dest + " :I last saw " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ".")
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :I last saw " + ircMsg.dataList[
                    1] + " as " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ".")
        else:
            if lastNick.lower() == ircMsg.dataList[1].lower():
                commands.append(
                    "PRIVMSG " + ircMsg.dest + " :I last saw " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ", they are still here.")
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :I last saw " + ircMsg.dataList[
                    1] + " as " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ", they are still here as " + isHere.name + ".")
    elif ircMsg.dataList[1].lower() == ircMsg.net.botnick.lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :I am right here.")
    elif ircMsg.src.lower() == ircMsg.dataList[1].lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :Wherever you go, there you are.")
    else:
        commands.append("PRIVMSG " + ircMsg.dest + " :I'm not sure what you're asking me to do.")

    return commands


def __traceNick(ircMsg):
    '''
    Query the seen database, for all nicks and hosts used common to one nick,
    used to find out what other nicks/hosts a person has used in a channel.
    '''
    commands = []

    if not ((ircMsg.dataList[2].lower() == ircMsg.net.botnick.lower()) or (
        ircMsg.src.lower() == ircMsg.dataList[2].lower())):
        seen = Seen(ircMsg.net.name)

        nicks, hosts = seen.nickSearch(ircMsg.dataList[2])

        if len(nicks) > 0 and len(hosts) > 0:

            nicks = __removeItem(nicks, ircMsg.dataList[2])
            hostText = ", ".join(hosts)

            if hostText > 1:
                noun = "hosts"
            else:
                noun = "host"

            if len(nicks) > 0:
                nickText = ", ".join(nicks)
                message = "I have seen " + ircMsg.dataList[
                    2] + " as " + nickText + " connecting from " + noun + " " + hostText + "."
            else:
                message = "I have seen " + ircMsg.dataList[2] + " connecting from " + noun + " " + hostText + "."

            msgList = ircMsg.net.splitMessage(message)

            for msg in msgList:
                commands.append("PRIVMSG " + ircMsg.dest + " :" + msg)
        else:
            commands.append(
                "PRIVMSG " + ircMsg.dest + " :I have no information on " + ircMsg.dataList[2] + " in my database.")

    elif ircMsg.dataList[2].lower() == ircMsg.net.botnick.lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :I usually have the same nick.")
    elif ircMsg.src.lower() == ircMsg.dataList[2].lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :Don't you know who you are?")
    else:
        commands.append("PRIVMSG " + ircMsg.dest + " :I'm not sure what you're asking me to do.")

    return commands
