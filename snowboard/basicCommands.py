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
    '''
    Process trigger words / phrases from an IRC channel.

    Triggers processed are:
        "Nick, who are you?" (and variations, see regular expression):
            Instructs the bot to tell the channel what it is and where further
            information on its operation can be found.
        "Ping me" (and variations, see regular expression):
            Instructs the bot to ping a person and then post the ping time to
            the open channel.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    whoAreRE = r"^\b(" + ircMsg.net.botnick + r")(, | |: ){0,1}\b(Who are you)\?{0,1}$"
    pingRE = r"^(ping)[ ]{0,1}(me){0,1}[,]{0,1}[ ]{0,1}(please){0,1}[?!.]{0,1}$"

    if re.search(whoAreRE, ircMsg.data, flags = re.IGNORECASE):
        commands = __identifySelf(ircMsg)
    elif re.search(pingRE, ircMsg.data, flags = re.IGNORECASE):
        commands = __pingMe(ircMsg)

    return commands

def ctcpTriggers(ircMsg):
    '''
    Processes triggers sent via CTCP to the bot, in particular processes a
    returning ping reply sent to the bot after the "ping me" trigger is used.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    if ircMsg.command == "PINGREPLY":
        commands = __pingBack(ircMsg)

    return commands


def joinTrigger(ircMsg):
    '''
    Processes triggers based on when people join a channel.

    Triggers processed:
        Channel joins which cause the bot to auto op or auto voice a user.
        User must be authenticated and have the "autovoice" / "autoops"
        flags, or the channel itself must be flagged to voice all users
        in which case the "voice" / "autovoice" deny flag can be used
        to not voice a particular user.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
        This should only be triggered from a channel and thus the destination
        field of the ircMessage object should always be a channel.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    # Pull the correct objects for the sender and destination.
    chan = ircMsg.net.findChannel(ircMsg.dest)
    nick = ircMsg.net.findNick(ircMsg.src)

    # Set appropriate flags to defaults.
    voiceNick = False
    opNick = False

    # Assuming the channel is found in the database (likely, but not certain)
    # process the join for needed flags.
    if not chan is None:
        # If a channel has the "voiceall" flag, the bot should voice anyone
        # who is not restricted by their channel flags.
        if chan.checkFlag("voiceall"):
            if nick is None:
                voiceNick = True
            elif nick.user.checkDenied("voice") or nick.user.checkDenied("autovoice"):
                voiceNick = False
            else:
                voiceNick = True

        # Now if the channel is or is not set for auto-voice, process to see
        # if the nick requires a voice, assuming the nick is found in the
        # member list (should be).
        if not nick is None:
            if nick.user.checkApproved("autoops"):
                opNick = True
            if nick.user.checkApproved("autovoice"):
                voiceNick = True

        # Actually load the command into the list to be returned.
        if chan.opped:
            if opNick:
                commands.append("MODE " + ircMsg.dest + " +o " + ircMsg.src)
            elif voiceNick:
                commands.append("MODE " + ircMsg.dest + " +v " + ircMsg.src)

    return commands

def msgTriggers(ircMsg):
    '''
    Process triggers sent via private message to the bot.

    Triggers processed:
        quit:
            Instructs the bot to quit IRC at once.
        hop:
            Instructs the bot to disconnect from the server and move to a
            different server.
        who are you?:
            Instructs the bot to tell the user what it is and where to find
            documentation on its operation.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    if ircMsg.dataList[0].lower() == "quit":
        commands = __quitCommand(ircMsg)
    elif ircMsg.dataList[0].lower() == "hop":
        commands = __hopServers(ircMsg)
    elif ircMsg.data.lower() == "who are you?":
        commands = __identifySelf(ircMsg)

    return commands

def noticeTriggers(ircMsg):
    '''
    Processes incoming NOTICE triggers from the server, in this case it allows
    the bot to authenticate itself with NickServ.

    Triggers processed:
        nickname is registered: (can be anywhere in the message)
            Triggers the bot to sent and authentication message to NickServ.
        password accepted: (can be anywhere in the message)
            Triggers the bot to log that its nick has been authenticated.
        you are now identified: (can be anywhere in the message)
            Same as "password accepted"
        password incorrect: (can be anywhere in a message)
            Triggers the bot to log that its nick was not authenticated.
        invalid password: (can be anywhere in a message)
            Same as "password incorrect"

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    # Handle NickServ identification.
    if ircMsg.data.lower().find("nickname is registered") > -1:
        commands += __authNickServ(ircMsg)
    elif ircMsg.data.lower().find("password accepted") > -1:
        __acceptedNickServ(ircMsg)
    elif ircMsg.data.lower().find("you are now identified") > -1:
        __acceptedNickServ(ircMsg)
    elif ircMsg.data.lower().find("password incorrect") > -1:
        __deniedNickServ(ircMsg)
    elif ircMsg.data.lower().find("invalid password") > -1:
        __deniedNickServ(ircMsg)

    return commands

def __acceptedNickServ(ircMsg):
    '''
    Simply instructs the bot to log that its NickServ password was accepted.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        None
    '''
    debug.message("I have confirmed my identity with " + ircMsg.src + ".")

def __authNickServ(ircMsg):
    '''
    Returns a list of commands to authenticate the bot with NickServ.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    if ircMsg.net.config.nickPass is None:
        debug.warn(ircMsg.src + " is requesting that I identify myself, but I have no password configured.")
    else:
        debug.message(ircMsg.src + " is requesting that I identify myself, attempting to do so.")
        commands.append("PRIVMSG " + ircMsg.src + " :identify " + ircMsg.net.config.nickPass)

    return commands

def __deniedNickServ(ircMsg):
    '''
    Simply instructs the bot to log that its NickServ password was not accepted.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        None
    '''
    debug.warn(ircMsg.src + " would not accept my password, I cannot identify myself.")

def __hopServers(ircMsg):
    '''
    If the person sending the command has admin privileges then the bot will
    send back confirmation that it has received the command and is going to
    hop servers, log the command to the debug log, and quit the server with a
    message saying why / who ordered it to hop servers.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)

    if nick.authed:
        if nick.user.checkApproved("admin"):
            debug.message("User " + ircMsg.src + " initiated a server hop.")
            commands.append("PRIVMSG " + ircMsg.src + " :Initiating a server hop.")
            commands.append("QUIT Server hop by order of " + ircMsg.src + ".")
        else:
            commands += basicMessages.denyMessage(ircMsg.src, "hop")
    else:
        commands += basicMessages.noAuth(ircMsg.src, "hop")

    return commands

def __identifySelf(ircMsg):
    '''
    The bot will identify itself to the person who asked who it is or back to
    the channel on which the person asked the question.  The bot will say that
    it is a bot, its software version, and where to find the software.

    :param ircMsg:
        ircMessage object, a message from the IRC Server.
    :return:
        commands, a list of IRC commands to be sent to the server.
    '''
    commands = []

    # Act differently if the bot is on a channel.
    if ircMsg.dest[0] == '#':
        dest = ircMsg.dest
    # If the bot is not on a channel, then
    else:
        dest = ircMsg.src

    commands.append(
        "PRIVMSG " + dest + " :I am " + ircMsg.net.botnick + ", a Snowboard bot running software version " + ircMsg.net.config.version + ".  Project Snowboard can be found at https://github.com/dwhagar/snowboard.")

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