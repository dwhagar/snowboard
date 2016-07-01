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


def __seenQuery(ircMsg):
    '''Query the seen database.'''
    commands = []

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

    return commands
