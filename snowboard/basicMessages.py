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

from os.path import isfile
from . import debug

def cmdHelp(src, cmd):
    '''Returns help text for a particular command.'''
    commands = []
    helpFile = "help/" + cmd + ".txt"

    if isfile(helpFile):
        file = open(helpFile.lower())
        data = file.readlines()

        for message in data:
            message = message.strip('/r')
            message = message.strip('/n')

            if not (message == ""):
                commands.append("PRIVMSG " + src + " :" + message)

        file.close()
    else:
        debug.error("Help file for command '" + cmd + "' (" + helpFile + ")not found!")
        commands.append("PRIVMSG " + src + " :I could not find help associated with the '" + cmd + "' command.")

    commands.append(
        "PRIVMSG " + src + " :See official documentation at https://github.com/dwhagar/snowboard/wiki for more information.")

    return commands

def denyMessage(src, cmd):
    '''Stock deny messages for debug and to send back to the server.'''
    commands = []

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but does not have sufficient access.")
    commands.append(
        "PRIVMSG " + src + " :You do not have sufficient access to the '" + cmd + "' command.  This may be due to access restrictions or attempting to set flags or a level higher than your own.")

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
    # Automatically add on command help.
    commands += cmdHelp(src, cmd)

    return commands


def valError(src, cmd, field, val, required):
    '''Standard message for a value related error.'''

    debug.info(
        "Nick " + src + " tried to use the '" + cmd + "' command but specified '" + val + "' for '" + field + "', which is not a " + required + ".")
    commands = [
        "PRIVMSG " + src + " :Error:  " + cmd + ":  " + field + " needs to be a " + required + " (was given " + str(
            val) + ")."]

    return commands