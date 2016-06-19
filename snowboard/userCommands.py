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

 # The interval at which the system will clean the master nicks list.
checkInterval = 300
checkNext = 0

def msgTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if ircMsg.dataList[0].lower() == "init" and ircMsg.net.config.init > 0:
        commands = __initCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "adduser":
        commands = __addCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "ident":
        commands = __identCmd(ircMsg)
                
    return commands
    
def cleanTimer(net, time):
    '''Executes the Nick list cleaning every checkInterval seconds.'''
    commands = []
    global checkNext
    global checkInterval
    
    # When initialized, set next time it will run, but don't run immediately.
    if checkNext == 0:
        debug.message("Master nick cleaning timer initialized.")
        checkNext = time + checkInterval
    
    if checkNext == time:
        debug.info("Running cleaning routine for the master nicks list.")
        net.cleanNicks()
        checkNext = time + checkInterval
    
    return commands
    
def __initCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    debug.message("Initialized admin user " + ircMsg.src + " with hostmask " + ircMsg.dataList[1] + ".")
    ircMsg.net.addUser(ircMsg.src, ircMsg.dataList[2], ircMsg.dataList[1], 255, ["admin"], [])
    ircMsg.net.config.init = 0
    message = "Added user " + ircMsg.src + " to the master database, as admin.  Disabling 'init' command.  For security, please do not start the bot with the -i / --init options again."
    return ["PRIVMSG " + ircMsg.src + " :" + message]

def __addCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    commands = []
    
    nick = ircMsg.net.findNick(ircMsg.src)
    
    if nick.authed:
        if nick.priv.checkFlag("usermanager"):
            user = ircMsg.dataList[1]
            hostmask = ircMsg.dataList[2]
            password = ircMsg.dataList[3]
            
            debug.message("Adding new user " + user + " to the global user database for " + ircMsg.src + ".")
            commands.append("PRIVMSG " + ircMsg.src + " :Adding " + user + " to the global user database.")
            
            try:
                level = int(ircMsg.dataList[4])
            except ValueError:
                debug.error("Error with 'adduser':  Level '" + ircMsg.dataList[4] + "' is not a number.")
                commands.append("PRIVMSG " + ircMsg.src + " :Unable to execute command, access level '" + ircMsg.dataList[4] + "' is not a number.")
                return commands
            
            if len(ircMsg.dataList) > 4:
                flags = "".join(ircMsg.dataList[5:])
                flags = flags.replace(' ','')
                flags = flags.split(':')
                approved = flags[0].split(',')
                if approved[0] == '':
                    approved = []
                    
                if len(flags) > 1:
                    denied = flags[1].split(',')
                    if denied[0] == '':
                        denied = []
                else:
                    denied = []
            else:
                approved = []
                denied = []
                
            result = ircMsg.net.addUser(user, password, hostmask, level, approved, denied)
            
            if not result:
                debug.error("Error with 'adduser':  User " + user + " already exists.")
                commands.append("PRIVMSG " + ircMsg.src + " :Command failed, user " + user + " already exists.")
                
        else:
            debug.message("Nick " + ircMsg.src + " tried to use the 'adduser' command, but does not have sufficient access.")
            commands.append("PRIVMSG " + ircMsg.src + " :You cannot access the 'adduser' command.")
    else:
        debug.message("Nick " + ircMsg.src + " tried to use the 'adduser' command, but was not identified.")
        commands.append("PRIVMSG " + ircMsg.src + " :You are not identified.")

    return commands

def __identCmd(ircMsg):
    '''Identify command to authenticate a user.'''
    commands = []
    
    nick = ircMsg.net.findNick(ircMsg.src)
    commands = nick.auth(ircMsg.dataList[1])
    
    return commands