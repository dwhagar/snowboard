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
'''

from . import debug

def triggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if messageList[0].lower() == "quit":
        commands = __quitCommand(ircMsg)

    return commands
    
def __quitCommand(ircMsg):
    '''Quits from IRC.'''
    # Generally speaking we should not make a habit of invoking the
    # sendCommands function directly, and just return a list.  This is a
    # special case, since once we send the Quit command the connection will
    # be closed by the server.
    ircMsg.net.sendCommands(["PRIVMSG " + ircMsg.src + " :Quitting IRC now."])
    debug.message("Quitting IRC at command of " + ircMsg.src + ".")
    ircMsg.net.quit()
    return [] # No commands are returned.