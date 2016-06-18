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
    
    if ircMsg.dataList[0].lower() == "quit":
        commands = __quitCommand(ircMsg)

    return commands
    
def __quitCommand(ircMsg):
    '''Quits from IRC.'''
    commands = []
    
    nick = ircMsg.net.findNick(ircMsg.src)
    
    if nick.authed:
        if ("admin" in nick.priv.denied) or ("quit" in nick.priv.denied):
            debug.message("User " + ircMsg.src + " tried to use the 'quit' command but is expressly blocked from doing so.")
            command.append("PRIVMSG " + ircMsg.src + " :Access to the 'quit' command is expressly denied.")
        elif ("admin" in nick.priv.approved) or ("quit" in nick.priv.approved):
            # Generally speaking we should not make a habit of invoking the
            # sendCommands function directly, and just return a list.  This is a
            # special case, since once we send the Quit command the connection will
            # be closed by the server.
            ircMsg.net.sendCommands(["PRIVMSG " + ircMsg.src + " :Quitting IRC now."])
            debug.message("Quitting IRC by order of " + ircMsg.src + ".")
            ircMsg.net.quit()
            return [] # Normally I wouldn't do this either
        else:
            debug.message("User " + ircMsg.src + " tried to use the 'quit' command, but does not have sufficient access.")
            commands.append("PRIVMSG " + ircMsg.src + " :You access to the 'quit' command.")
    else:
        debug.message("User " + ircMsg.src + " tried to use the 'quit' command, but has not been authenticated.")
        commands.append("PRIVMSG " + ircMsg.src + " :You have not authenticated yet, you have to do that first with the 'ident' command.")
        
    return commands