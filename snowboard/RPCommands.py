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
Commands useful for using Snowboard on an RP channel.

Specifically these commands will be useful for channels tagged with
the following flags:

ic
dice
'''


def joinTriggers(ircMsg):
    '''Triggers based on join messages for a channel.'''
    commands = []

    if not ircMsg.src == ircMsg.net.botnick:
        chan = ircMsg.net.findChannel(ircMsg.dest)

        if not chan is None:
            if chan.checkFlag("ic"):
                commands.append(
                    "NOTICE " + ircMsg.src + " :The channel " + ircMsg.dest + " is currently In Character (IC).  To talk Out of Character (OOC) please use #BlazingUmbra-OOC.  Further information can be found in the channel topic.  Type ^desc for a description of the setting, !help for bot commands, ^rules for rules.")

    return commands
