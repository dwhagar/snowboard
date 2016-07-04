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


def channelTriggers(ircMsg):
    '''Processes channel triggers.'''
    commands = []

    if ircMsg.dataList[0] == "!opme":
        commands = __opmeCommand(ircMsg)

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
                commands.append("MODE " + ircMsg.dest + " +o " + ircM.src)
            else:
                commands += basicMessages.denyMessage(ircMsg.dest, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.dest, thisCmd)
    else:
        commands += basicMessages.noOps(ircMsg.dest, thisCmd, ircMsg.src)

    return commands
