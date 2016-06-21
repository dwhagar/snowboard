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

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from . import debug

def msgTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if ircMsg.dataList[0].lower() == "quit":
        commands = __quitCommand(ircMsg)
    elif ircMsg.data.lower() == "who are you?":
        commands = __identifySelf(ircMsg)

    return commands
    
def channelTriggers(ircMsg):
    '''Process triggers for basic commands.'''
    commands = []
    
    if ircMsg.dataList[0][:len(ircMsg.net.botnick)].lower() == ircMsg.net.botnick.lower():
        data = " ".join(ircMsg.dataList[1:])
        if data.lower() == "who are you?":
            commands = __identifySelf(ircMsg)

    return commands

def __quitCommand(ircMsg):
    '''Quits from IRC.'''
    commands = []
    
    nick = ircMsg.net.findNick(ircMsg.src)
    
    if nick.authed:
        if nick.priv.checkFlag("admin"):
            # Generally speaking we should not make a habit of invoking the
            # sendCommands function directly, and just return a list.  This is a
            # special case, since once we send the Quit command the connection will
            # be closed by the server.
            ircMsg.net.sendCommands(["PRIVMSG " + ircMsg.src + " :Quitting IRC now."])
            debug.message("Quitting IRC by order of " + ircMsg.src + ".")
            ircMsg.net.quit()
            return [] # Normally I wouldn't do this either
        else:
            debug.message("Nick " + ircMsg.src + " tried to use the 'quit' command, but does not have sufficient access.")
            commands.append("PRIVMSG " + ircMsg.src + " :You cannot access to the 'quit' command.")
    else:
        debug.message("Nick " + ircMsg.src + " tried to use the 'quit' command, but has not been authenticated.")
        commands.append("PRIVMSG " + ircMsg.src + " :You are not identified.")
        
    return commands
    
def __identifySelf(ircMsg):
    '''The bot will send back identifying information.'''
    commands = []
    
    if ircMsg.dest[0] == '#':
        dest = ircMsg.dest
        chan = ircMsg.net.findChannel(dest)
        botnick = chan.botnick
    else:
        dest = ircMsg.src
        botnick = ircMsg.net.botnick
    
    commands.append("PRIVMSG " + dest + " :I am " + botnick + ", a Snowboard bot.  Project Snowboard can be found at https://github.com/dwhagar/snowboard where my code is under development and documentation can be found.")
    
    return commands