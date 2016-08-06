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


def cmdDisabled(src, cmd, dest = None):
    '''Provides a basic /command is disabled/ message.'''
    commands = []

    if not dest is None:
        msgPrefix = "NOTICE " + src + " :"
        suffix = " in " + dest + "."
    else:
        msgPrefix = "PRIVMSG " + src + " :"
        suffix = "."

    commands.append(msgPrefix + "The " + cmd + " command has been disabled by an administrator" + suffix)

    return commands

def cmdHelp(src, cmd, dest = None):
    '''Returns help text for a particular command.'''
    commands = []
    helpFile = "help/" + cmd + ".txt"

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    if isfile(helpFile):
        file = open(helpFile.lower())
        data = file.readlines()

        for message in data:
            message = message.strip('/r')
            message = message.strip('/n')

            if not (message == ""):
                commands.append(msgPrefix + message)

        file.close()
    else:
        debug.error("Help file for command '" + cmd + "' (" + helpFile + ")not found!")
        commands.append(msgPrefix + "I could not find help associated with the '" + cmd + "' command.")

    commands.append(
        msgPrefix + "See official documentation at https://github.com/dwhagar/snowboard/wiki for more information.")

    return commands

def denyMessage(src, cmd, dest = None):
    '''Stock deny messages for debug and to send back to the server.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but does not have sufficient access.")
    commands.append(
        msgPrefix + "You do not have sufficient access to the '" + cmd + "' command.  This may be due to access restrictions or attempting to set flags or a level higher than your own.")

    return commands

def noAuth(src, cmd, dest = None):
    '''Stock not authenticated messages for debug and the server.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but has not been authenticated.")
    commands.append(msgPrefix + "You are not identified.")

    return commands

def noChannel(src, cmd, chan, dest = None):
    '''Stock message for unable to find a channel.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but I was unable to find channel '" + chan + "' in the database.")
    commands.append(msgPrefix + "I'm sorry but I could not find " + chan + " in the database.")

    return commands

def noOps(src, cmd, chan, dest = None):
    '''Strock message for if the bot does not have ops.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' on " + chan + " but I do not have ops.")
    commands.append(msgPrefix + "I'm sorry, but I don't have operator privileges here.")

    return commands

def noUser(src, cmd, user, dest = None):
    '''Stock message for a user that does not exist.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but " + user + " could not be found in the database.")
    commands.append(msgPrefix + "I'm sorry but I could not find " + user + " in the database.")

    return commands

def paramFail(src, cmd, dest = None):
    '''Stock message for not enough parameters.'''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.info("Nick " + src + " tried to use the '" + cmd + "' command, but did not provide the correct parameters.")
    commands.append(msgPrefix + "You did not provide the correct parameters for the '" + cmd + "' command.")
    # Automatically add on command help.
    commands += cmdHelp(src, cmd, dest)

    return commands

def valError(src, cmd, field, val, required, dest = None):
    '''Standard message for a value related error.'''

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.info(
        "Nick " + src + " tried to use the '" + cmd + "' command but specified '" + val + "' for '" + field + "', which is not a " + required + ".")
    commands = [msgPrefix + "Error:  " + cmd + ":  " + field + " needs to be a " + required + " (was given " + str(
            val) + ")."]

    return commands