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

from . import basicMessages
from . import debug

def channelTriggers(ircMsg):
    '''Processes channel triggers for channel fucntions.'''
    commands = []

    if ircMsg.dataList[0] == "!opme":
        commands = __opmeCommand(ircMsg)

    return commands


def msgTriggers(ircMsg):
    '''Processes message triggers for channel functions.'''
    commands = []

    if ircMsg.dataList[0] == "modchan":
        commands = __modChannel(ircMsg)

    return commands


def __modChannel(ircMsg):
    '''Commands to change channel properties.'''
    commands = []
    thisCmd = "modchan"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) >= 3:
        chan = ircMsg.net.findChannel(ircMsg.dataList[1])
        cmd = ircMsg.dataList[2]

        if len(ircMsg.dataList) >= 4:
            data = " ".join(ircMsg.dataList[3:])
        else:
            data = ""

        if not chan is None:
            if nick.user.checkApproved("channelmanager", chan.name):
                if cmd == "addflags":
                    data.replace(" ", "")
                    list = data.split(",")
                    if not list == []:
                        for flag in list:
                            chan.addFlag(flag)
                        debug.message("Channel flags were added to " + chan.name + " by " + ircMsg.src + ".")
                        commands.append("PRIVMSG " + ircMsg.src + " :Flags added to " + chan.name + ".")
                    else:
                        commands += basicMessages.paramFail(ircMsg.src, cmd)
                elif cmd == "delflags":
                    data.replace(" ", "")
                    list = data.split(",")
                    if not list == []:
                        for flag in list:
                            chan.removeFlag(flag)
                        debug.message("Channel flags were added to " + chan.name + " by " + ircMsg.src + ".")
                        commands.append("PRIVMSG " + ircMsg.src + " :Flags added to " + chan.name + ".")
                    else:
                        commands += basicMessages.paramFail(ircMsg.src, cmd)
                elif cmd == "desc":
                    debug.info("Channel description requested by " + ircMsg.src + ".")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Description for " + chan.name + " is '" + chan.desc + "'.")
                elif cmd == "flags":
                    debug.info("Channel flags requested by " + ircMsg.src + ".")
                    if chan.flags == []:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has no flags set.")
                    else:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has flags " + ",".join(
                            chan.flags) + ".")
                elif cmd == "settopic":
                    chan.defaultTopic = data
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Flags for " + chan.name + " have been set.")
                    debug.message("Default topic for " + chan.name + " was set by " + ircMsg.src + ".")
                elif cmd == "setdesc":
                    chan.desc = data
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Flags for " + chan.name + " have been set.")
                    debug.message("Channel description for " + chan.name + " was set by " + ircMsg.src + ".")
                elif cmd == "setflags":
                    data.replace(" ", "")
                    data = data.lower()
                    chan.flags = data.split(",")
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Flags for " + chan.name + " have been set.")
                    debug.message("Channel flags for " + chan.name + " were set by " + ircMsg.src + ".")
                elif cmd == "topic":
                    debug.info("Default topic requested by " + ircMsg.src + ".")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Default topic for " + chan.name + " is '" + chan.defaultTopic + "'.")
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noChannel(ircMsg.src, thisCmd, ircMsg.dataList[1])
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __opmeCommand(ircMsg):
    '''Allows a person to gain ops in a channel when allowed.'''
    commands = []
    thisCmd = "!opme"

    nick = ircMsg.net.findNick(ircMsg.src)
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if chan.opped:
        if nick.authed:
            if nick.user.checkApproved("channelmanager", ircMsg.dest) or nick.user.checkApproved("ops", ircMsg.dest):
                commands.append("MODE " + ircMsg.dest + " +o " + ircMsg.src)
            else:
                commands += basicMessages.denyMessage(ircMsg.dest, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.dest, thisCmd)
    else:
        commands += basicMessages.noOps(ircMsg.dest, thisCmd, ircMsg.src)

    return commands
