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
This is where the core processing is done for the systems scripts and
commands.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.

Scripts can be added like any other module, placing the pythong file into the
folder "snowboard/snowboard" with the other module files, then imported here.

The format for importing is:
from . import scriptname
Where scriptname imports "scriptname.py".

Once the module is imported it can then be used like any other.
'''

from . import basicCommands
from . import userCommands
from . import seenCommands
from . import channelCommands
from . import RPCommands

def channelScripts(ircMsg):
    '''Executes scripts that should trigger from channel content.'''
    cmds = []
    cmds += basicCommands.channelTriggers(ircMsg)
    cmds += seenCommands.chanTriggers(ircMsg)
    cmds += channelCommands.channelTriggers(ircMsg)
    return cmds

def messageScripts(ircMsg):
    '''Executes scripts that should trigger from private message content.'''
    cmds = []
    cmds += basicCommands.msgTriggers(ircMsg)
    cmds += userCommands.msgTriggers(ircMsg)
    cmds += channelCommands.msgTriggers(ircMsg)
    return cmds

def privActionScripts(ircMsg):
    '''Executes scripts that should be triggered by a private action.'''
    cmds = []

    return cmds


def privNoticeScripts(ircMsg):
    '''Executes scripts that should be triggered by a private notice message.'''
    cmds = []
    cmds += basicCommands.noticeTriggers(ircMsg)
    return cmds


def chanActionScripts(ircMsg):
    '''Executes scripts that should be triggered by public action.'''
    cmds = []

    return cmds


def chanNoticeScripts(ircMsg):
    '''Executes scripts that should be triggered by a public notice message.'''
    cmds = []

    return cmds


def ctcpScripts(ircMsg):
    '''Executes scripts that should be triggered by a CTCP message.'''
    cmds = []
    cmds += basicCommands.ctcpTriggers(ircMsg)
    return cmds


def joinScripts(ircMsg):
    '''Processes script triggers based on channel joins.'''
    cmds = []
    cmds = RPCommands.joinTriggers(ircMsg)
    return cmds


def partScripts(ircMsg):
    '''Processes script triggers based on channel parts.'''
    cmds = []

    return cmds

def rawMessages(net, message):
    '''Executes scripts that process raw messages from the server.'''
    cmds = []
    seenCommands.rawTriggers(net, message)
    return cmds


def timers(net, time):
    '''Passes the current time onto a series of timers.'''
    cmds = []

    # 5 Minute Timer
    if (round(time) % 300) == 0:
        cmds += channelCommands.resetTopics(net)

    return cmds