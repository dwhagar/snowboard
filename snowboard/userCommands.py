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
See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from . import debug
from . import basicMessages

def msgTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if ircMsg.dataList[0].lower() == "init" and ircMsg.net.config.init > 0:
        commands = __initCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "adduser":
        commands = __addCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "deluser":
        commands = __delCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "ident":
        commands = __identCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "listusers":
        commands = __listCmd(ircMsg)
                
    return commands

def __addCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    commands = []
    thisCmd = "adduser"
    
    if len(ircMsg.dataList) >= 5:
        nick = ircMsg.net.findNick(ircMsg.src)
    
        if nick.authed:
            if nick.priv.checkApproved("usermanager"):
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
            
                # Need to make sure, if a user does not have access to a flag
                # they cannot add it to a new user.
                block = False
            
                for flag in approved:
                    if not nick.priv.checkApproved(flag):
                        block = True
                    
                if nick.priv.level < level:
                    block = True
                
                hosts = [hostmask]
                uid = ircMsg.net.users.uidHash(user)
                exists = ircMsg.net.users.uidExists(uid)
            
                if not block:
                    if not exists:
                        ircMsg.net.users.addUser(uid, user, password, hosts, level, approved, denied)
                    else:
                        debug.error("Error with 'adduser':  User " + user + " already exists.")
                        commands.append("PRIVMSG " + ircMsg.src + " :Command failed, user " + user + " already exists.")
                else:
                    debug.error("Error with 'adduser':  User " + ircMsg.src + " attempted to grant privleges to " + user + " greater than his/her own access.")
                    commands.append("PRIVMSG " + ircMsg.src + " :Command failed, you cannot add greater privleges than the ones you possess.")
            else:
                commands += basicMessages.denyMessages(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __delCmd(ircMsg):
    '''Removes a user from the user database.'''
    commands = []
    thisCmd = "deluser"
    
    if len(ircMsg.dataList) >= 2:
        nick = ircMsg.net.findNick(ircMsg.src)
    
        user = ircMsg.dataList[1]
    
        if nick.authed:
            if nick.priv.checkApproved("usermanager"):
                uid = ircMsg.net.users.uidHash(user)
                exists = ircMsg.net.users.uidExists(uid)
                
                if exists:
                    data = ircMsg.net.users.userInformation(uid)
                    level = data[2]
                    
                    if nick.priv.level >= level:
                        ircMsg.net.users.removeUser(uid)
                        debug.message("User " + ircMsg.src + " removed " + user + " from the global user database.")
                        commands.append("PRIVMSG " + ircMsg.src + " :Removing " + user + " from the global user database.")
                    else:
                        debug.message("User " + ircMsg.src + " tried to remove " + user + " from the global database, did not have high enough access.")
                        commands.append("PRIVMSG " + ircMsg.src + " :You cannot remove " + user + ", your access level is not high enough.")
                else:
                    commands += basicMessages.noUser(ircMsg.src, thisCmd, user)
            else:
                commands += basicMessages.denyMessages(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)
    
    return commands

def __formatUserLine(item):
    '''Formats a single line of user information.'''
    user = item[0]
    level = str(item[1])
    approved = item[2]
    denied = item[3]
    
    if approved == "" and denied == "":
        message = "User: " + user + "; Level: " + level
    elif approved == "":
        message = "User: " + user + "; Level: " + level + "; Denied Flags: " + denied
    elif denied == "":
        message = "User: " + user + "; Level: " + level + "; Approval Flags: " + approved
    else:
        message = "User: " + user + "; Level: " + level + "; Approval Flags: " + approved + "; Denied Flags: " + denied

    return message

def __identCmd(ircMsg):
    '''Identify command to authenticate a user.'''
    commands = []
    thisCmd = "ident"
    
    if len(ircMsg.dataList) >= 2:
        nick = ircMsg.net.findNick(ircMsg.src)
        commands = nick.auth(ircMsg.dataList[1])
    else:
        commands += basicMessage.paramFail(ircMsg.src, thisCmd)
    
    return commands

def __initCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    commands = []
    thisCmd = "init"
    
    if len(ircMsg.dataList) >= 3:
        debug.message("Initialized admin user " + ircMsg.src + " with hostmask " + ircMsg.dataList[1] + ".")
    
        hosts = [ircMsg.dataList[1]]
        password = ircMsg.dataList[2]
        user = ircMsg.src
        uid = ircMsg.net.users.uidHash(user)
        exists = ircMsg.net.users.uidExists(uid)
    
        if not exists:
            ircMsg.net.users.addUser(uid, user, password, hosts, 255, [], [])
            ircMsg.net.config.init = 0
            commands.append("PRIVMSG " + ircMsg.src + " :Added user " + user + " to the master database, as admin.  Disabling 'init' command.  For security, please do not start the bot with the -i / --init options again.")
        else:
            debug.error("Error with 'adduser':  User " + user + " already exists.")
            commands.append("PRIVMSG " + ircMsg.src + " :Command failed, user " + user + " already exists.")
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)
        
    return commands

def __listCmd(ircMsg):
    '''Provides a list of users.'''
    commands = []
    
    if len(ircMsg.dataList) > 1:
        channel = ircMsg.dataList[1]
    else:
        channel = None
    
    nick = ircMsg.net.findNick(ircMsg.src)
    
    if nick.authed:
        if channel == None:
            data = ircMsg.net.users.getUsers()
        else:
            chan = ircMsg.net.findChannel(channel)
            
            if chan == None:
                debug.info("Nick " + ircMsg.src + " was looking for the user list of " + channel + ", but the channel was not found.")
                commands.append("PRIVMSG " + ircMsg.src + " :Channel " + channel + " was not found in my database.")
                data = []
            else:
                data = chan.users.getUsers()
        
        if len(data) > 0:
            for item in data:
                message = __formatUserLine(item)
                commands.append("PRIVMSG " + ircMsg.src + " :" + message)
        else:
            if channel == None:
                debug.info("Nick " + ircMsg.src + " was looking for the global user list, but there are no users in that channel.")
                commands.append("PRIVMSG " + ircMsg.src + " :There are no users on the globel user list.  I think something went wrong!")
            elif not chan == None:
                debug.info("Nick " + ircMsg.src + " was looking for the user list of " + channel + ", but there are no users in that channel.")
                commands.append("PRIVMSG " + ircMsg.src + " :There are no users listed on " + channel + ".")
    else:
        commands += basicMessages.noAuth(ircMsg.src, "listusers")
            
    return commands