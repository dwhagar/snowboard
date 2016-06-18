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
Provides triggers and processing to handle commands relating to user
management and authentication.
'''

from . import debug

def triggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if ircMsg.dataList[0].lower() == "init" and ircMsg.net.config.init > 0:
        commands = __initCmd(ircMsg)
    if ircMsg.dataList[0].lower() == "ident":
        commands = __identCmd(ircMsg)
                
    return commands
    
def __initCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    debug.message("Initialized admin user " + ircMsg.src + " with hostmask " + messagelist[2] + ".")
    ircMsg.net.addUser(ircMsg.src, ircMsg.dataList[2], ircMsg.dataList[1], 255, ["admin"], [])
    ircMsg.net.config.init = 0
    message = "Added user " + ircMsg.src + " to the master database, as admin.  Disabling 'init' command.  For security, please do not start the bot with the -i / --init options again."
    return ["PRIVMSG " + ircMsg.src + " :" + message]

def __identCmd(ircMsg):
    '''Identify command to authenticate a user.'''
    commands = []
    
    nick = ircMsg.net.findNick(ircMsg.src)
    commands = nick.auth(ircMsg.dataList[1])
    
    return commands