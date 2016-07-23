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

    if ircMsg.dataList[0].lower() == "^seen":
        commands = __seenQuery(ircMsg)
    if ircMsg.dataList[0].lower() == "^trace" and ircMsg.dataList[1].lower() == "nick":
        commands = __traceNick(ircMsg)

    return commands

def rawTriggers(net, message):
    '''Processes raw message triggers.'''
    dbTriggerA = r"^(.*)!(.*@.*) (PRIVMSG|PART) (#.*) :(.*)$"
    dbTriggerB = r"^(.*)!(.*@.*) (QUIT|NICK) :(.*)$"
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
        # Process quit and nick messages.
        data = searchB.split(message)

        nick = data[1]
        host = data[2]
        msg = data[4]

        if msg == "QUIT":
            act = "leaving IRC with message '" + msg + "'"
            seen.save(nick, host, act)
        elif msg == "NICK":
            act = "changing nick to '" + msg + "'"
            seen.save(nick, host, act)
            act = "changing nick from '" + nick + "'"
            seen.save(msg, host, act)

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

    if len(ircMsg.dataList) == 2:
        if not ((ircMsg.dataList[1].lower() == ircMsg.net.botnick.lower()) or (
                    ircMsg.src.lower() == ircMsg.dataList[1].lower())):
            seen = Seen(ircMsg.net.name)

            nicks, hosts = seen.nickSearch(ircMsg.dataList[1])

            if (not (nicks is None)) and (not (hosts is None)):
                lastTime, lastNick, lastHost, lastAct = seen.timeSearch(nicks, hosts)

                timeDiff = round(time.time()) - round(lastTime)
                delta = datetime.timedelta(seconds = timeDiff)

                if (delta.days == 0) and (delta.seconds < 1):
                    ago = "less than a second"
                else:
                    ago = str(delta)

                for nick in nicks:
                    isHere = ircMsg.net.findNick(nick)
                    if not (isHere is None):
                        break

                if isHere is None:
                    if lastNick.lower() == ircMsg.dataList[1].lower():
                        commands.append(
                            "PRIVMSG " + ircMsg.dest + " :I last saw " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ".")
                    else:
                        commands.append("PRIVMSG " + ircMsg.dest + " :I last saw " + ircMsg.dataList[
                            1] + " as " + lastNick + " " + lastAct + " " + ago + " ago from host " + lastHost + ".")
                else:
                    if lastNick.lower() == isHere.name.lower():
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
                commands.append(
                    "PRIVMSG " + ircMsg.dest + " :I have no information on " + ircMsg.dataList[1] + " in my database.")
        else:
            commands.append("PRIVMSG " + ircMsg.dest + " :I'm not sure what you're asking me to do.")
    else:
        commands.append(
            "PRIVMSG " + ircMsg.dest + " :Where you looking for someone?  You need to tell me who you are looking for, and I'll check.  Only give me one name a time.")

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

        if (not (nicks is None)) and (not (hosts is None)):
            nicks = __removeItem(nicks, ircMsg.dataList[2])

            if len(hosts) > 1:
                noun = "hosts"
            else:
                noun = "host"

            hostsLen = len(hosts)
            if hostsLen == 1:
                hostText = hosts[0]
            elif hostsLen == 2:
                hostText = " and ".join(hosts)
            else:
                hostText = ", and ".join([", ".join(hosts[:-1])] + hosts[-1:])

            nicksLen = len(nicks)
            if nicksLen > 0:
                if nicksLen == 1:
                    nickText = nicks[0]
                elif nicksLen == 2:
                    nickText = " and ".join(nicks)
                else:
                    nickText = ", and ".join([", ".join(nicks[:-1])] + nicks[-1:])

                message = "I have seen " + ircMsg.dataList[
                    2] + " as " + nickText + " connecting from " + noun + " " + hostText + "."
            else:
                message = "I have seen " + ircMsg.dataList[2] + " connecting from " + noun + " " + hostText + "."

            msgList = ircMsg.net.splitMessage(message)

            if len(message) < 350:
                sendCmd = "PRIVMSG " + ircMsg.dest + " :"
            else:
                commands.append(
                    "PRIVMSG " + ircMsg.dest + " :There is a lot of information here, I will send it to you in private.")
                sendCmd = "NOTICE " + ircMsg.src + " :"

            for msg in msgList:
                commands.append(sendCmd + msg)
        else:
            possibleNicks = seen.searchNicks(ircMsg.dataList[2])
            message = "I have no information on '" + ircMsg.dataList[2] + "' in my database."

            possibleNicksLen = len(possibleNicks)
            if possibleNicksLen == 1:
                message += "  Did you mean " + possibleNicks[0] + "?"
            elif possibleNicksLen == 2:
                message += "  Did you mean " + " or ".join(possibleNicks) + "?"
            elif possibleNicksLen > 2:
                nicksList = ", or ".join([", ".join(possibleNicks[:-1])] + possibleNicks[-1:])
                message += "  Did you mean " + nicksList + "?"

            msgList = ircMsg.net.splitMessage(message)

            for msg in msgList:
                commands.append("PRIVMSG " + ircMsg.dest + " :" + msg)

    elif ircMsg.dataList[2].lower() == ircMsg.net.botnick.lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :I usually have the same nick.")
    elif ircMsg.src.lower() == ircMsg.dataList[2].lower():
        commands.append("PRIVMSG " + ircMsg.dest + " :Don't you know who you are?")
    else:
        commands.append("PRIVMSG " + ircMsg.dest + " :I'm not sure what you're asking me to do.")

    return commands