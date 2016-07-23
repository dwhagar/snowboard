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
Processes basic IRC commands.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''
import time
import re
from . import debug
from . import basicMessages

def channelTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []

    whoAreRE = r"^\b(" + ircMsg.net.botnick + r")(, | |: ){0,1}\b(Who are you)\?{0,1}$"
    pingRE = r"^(ping)[ ]{0,1}(me){0,1}[,]{0,1}[ ]{0,1}(please){0,1}[?!.]{0,1}$"

    if re.search(whoAreRE, ircMsg.data, flags = re.IGNORECASE):
        commands = __identifySelf(ircMsg)
    elif re.search(pingRE, ircMsg.data, flags = re.IGNORECASE):
        commands = __pingMe(ircMsg)

    return commands

def ctcpTriggers(ircMsg):
    '''Processes triggers for CTCP replies.'''
    commands = []

    if ircMsg.command == "PINGREPLY":
        commands = __pingBack(ircMsg)

    return commands


def joinTrigger(ircMsg):
    commands = []

    chan = ircMsg.net.findChannel(ircMsg.dest)
    nick = ircMsg.net.findNick(ircMsg.src)
    voiceNick = False
    opNick = False

    if not chan is None:
        if chan.checkFlag("voiceall"):
            if nick is None:
                voiceNick = True
            elif nick.user.checkDenied("voice") or nick.user.checkDenied("autovoice"):
                voiceNick = False
            else:
                voiceNick = True

        if not nick is None:
            if nick.user.checkApproved("autoops"):
                opNick = True
            if nick.user.checkApproved("autovoice"):
                voiceNick = True

        if chan.opped:
            if opNick:
                commands.append("MODE " + ircMsg.dest + " +o " + ircMsg.src)
            elif voiceNick:
                commands.append("MODE " + ircMsg.dest + " +v " + ircMsg.src)

    return commands

def msgTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []

    if ircMsg.dataList[0].lower() == "quit":
        commands = __quitCommand(ircMsg)
    if ircMsg.dataList[0].lower() == "hop":
        commands = __hopServers(ircMsg)
    elif ircMsg.data.lower() == "who are you?":
        commands = __identifySelf(ircMsg)

    return commands

def noticeTriggers(ircMsg):
    '''Process triggers for basic NOTICE commands'''
    commands = []

    # Handle NickServ identification.
    if ircMsg.data.lower().find("nickname is registered") > -1:
        commands += __authNickServ(ircMsg)
    elif ircMsg.data.lower().find("password accepted") > -1:
        commands += __acceptedNickServ(ircMsg)
    elif ircMsg.data.lower().find("you are now identified") > -1:
        commands += __acceptedNickServ(ircMsg)
    elif ircMsg.data.lower().find("password incorrect") > -1:
        commands += __deniedNickServ(ircMsg)
    elif ircMsg.data.lower().find("invalid password") > -1:
        commands += __deniedNickServ(ircMsg)

    return commands

def __acceptedNickServ(ircMsg):
    '''Provides handling for NickServ accepting the identify command.'''
    debug.message("I have confirmed my identity with " + ircMsg.src + ".")

    return []

def __authNickServ(ircMsg):
    '''Sends authorization to NickServ'''
    commands = []

    if ircMsg.net.config.nickPass is None:
        debug.warn(ircMsg.src + " is requesting that I identify myself, but I have no password configured.")
    else:
        debug.message(ircMsg.src + " is requesting that I identify myself, attempting to do so.")
        commands.append("PRIVMSG " + ircMsg.src + " :identify " + ircMsg.net.config.nickPass)

    return commands

def __deniedNickServ(ircMsg):
    '''Provides handling for NickServ denying the identify commands.'''
    debug.warn(ircMsg.src + " would not accept my password, I cannot identify myself.")

    return []

def __hopServers(ircMsg):
    '''Tells the bot to hop from one server to another.'''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)

    if nick.authed:
        if nick.user.checkApproved("admin"):
            debug.message("User " + ircMsg.src + " initiated a server hop.")
            commands.append("PRIVMSG " + ircMsg.src + " :Initiatating a server hop.")
            commands.append("QUIT Server hop by order of " + ircMsg.src + ".")
        else:
            commands += basicMessages.denyMessage(ircMsg.src, "hop")
    else:
        commands += basicMessages.noAuth(ircMsg.src, "hop")

    return commands

def __identifySelf(ircMsg):
    '''The bot will send back identifying information.'''
    commands = []

    if ircMsg.dest[0] == '#':
        dest = ircMsg.dest
        chan = ircMsg.net.findChannel(dest)
        botnick = chan.botnick
    else:
        dest = ircMsg.src
        botnick = ircMsg.net.botnick

    commands.append(
        "PRIVMSG " + dest + " :I am " + botnick + ", a Snowboard bot running software version " + ircMsg.net.config.version + ".  Project Snowboard can be found at https://github.com/dwhagar/snowboard.")

    return commands

def __pingBack(ircMsg):
    '''Processes a return ping, relays the lag back.'''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)
    if nick.pingOut > 0:
        lagTime = time.time() - nick.pingOut
        lagTime = round(lagTime, 4)

        commands.append(
            "PRIVMSG " + nick.pingDest + " :Your current ping is " + str(lagTime) + " seconds " + ircMsg.src + ".")

        # We got out ping, don't keep looking.
        nick.pingOut = 0
        nick.pingDest = None

    return commands

def __pingMe(ircMsg):
    '''Pings a user and sends them back the results.'''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)
    nick.pingOut = time.time()
    nick.pingDest = ircMsg.dest
    commands.append("PING " + ircMsg.src + " :" + str(time.time()))

    return commands

def __quitCommand(ircMsg):
    '''Quits from IRC.'''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)

    if nick.authed:
        if nick.user.checkApproved("admin"):
            # Generally speaking we should not make a habit of invoking the
            # sendCommands function directly, and just return a list.  This is a
            # special case, since once we send the Quit command the connection will
            # be closed by the server.
            ircMsg.net.sendCommands(["PRIVMSG " + ircMsg.src + " :Quitting IRC now."])
            debug.message("Quitting IRC by order of " + ircMsg.src + ".")
            ircMsg.net.quit()
            return [] # Normally I wouldn't do this either
        else:
            commands += basicMessages.denyMessage(ircMsg.src, "quit")
    else:
        commands += basicMessages.noAuth(ircMsg.src, "quit")

    return commands