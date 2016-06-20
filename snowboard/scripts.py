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

Scripts can be added like any other module, placing the pythong file into the
folder "snowboard/snowboard" with the other module files, then imported here.

The format for importing is:
from . import scriptname
Where scriptname imports "scriptname.py".

Once the module is imported it can then be used like any other.
'''

from . import debug
from . import basicCommands
from . import userCommands

def channelScripts(ircMsg):
    '''Executes scripts that should trigger from channel content.'''
    cmds = []
    cmds += basicCommands.channelTriggers(ircMsg)
    
    return cmds
    
def messageScripts(ircMsg):
    '''Executes scripts that should trigger from private message content.'''
    cmds = []
    cmds += basicCommands.msgTriggers(ircMsg)
    cmds += userCommands.msgTriggers(ircMsg)
    
    return cmds
    
def privNoticeScripts(ircMsg):
    '''Executes scripts that should be triggered by a notice message.'''
    cmds = []
    
    return cmds
    
def chanNoticeScripts(ircMsg):
    '''Executes scripts that should be triggered by a notice message.'''
    cmds = []
    
    return cmds
    
def timers(net, time):
    '''Passes the current time onto a series of timers.'''
    cmds = []
    
    return cmds