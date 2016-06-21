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
Useful functions for standardized messages both in debug and for feedback to
the user.
'''

from . import debug

def denyMessage(src, cmd):
    '''Stock deny messages for debug and to send back to the server.'''
    commands = []
    
    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but does not have sufficient access.")
    commands.append("PRIVMSG " + src + " :You cannot access to the '" + cmd + "' command.")
    
    return commands

def noAuth(src, cmd):
    '''Stock not authenticated messages for debug and the server.'''
    commands = []
    
    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but has not been authenticated.")
    commands.append("PRIVMSG " + src + " :You are not identified.")
    
    return commands