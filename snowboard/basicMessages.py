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
    
def noChannel(src, cmd, chan):
    '''Stock message for unable to find a channel.'''
    commands = []
    
    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but I was unable to find channel '" + chan + "' in the database.")
    commands.append("PRIVMSG " + src + " :I'm sorry but I could not find " + chan + " in the database.")
    
    return commands
    
def noUser(src, cmd, user):
    '''Stock message for a user that does not exist.'''
    commands = []
    
    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but " + user + " could not be found in the database.")
    commands.append("PRIVMSG " + src + " :I'm sorry but I could not find " + user + " in the database.")
    
    return commands
    
def paramFail(src, cmd):
    '''Stock message for not enough parameters.'''
    commands = []
    
    debug.info("Nick " + src + " tried to use the '" + cmd + "' command, but did not provide enough parameters.")
    commands.append("PRIVMSG " + src + " :You did not provide enough parameters for the '" + cmd + "' command.")
    
    return commands