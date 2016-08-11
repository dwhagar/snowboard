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
Basic messages to be used by any particular script, includes the sending of
command help for a misused command and messages to the debug system.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from os.path import isfile
from . import debug

def cmdDisabled(src, cmd, dest = None):
    '''
    An message telling that a command has been disabled.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    # dest will be None if it goes back to somewhere other than the source
    # such as for a channel based command
    if not dest is None:
        msgPrefix = "NOTICE " + src + " :"
        suffix = " in " + dest + "."
        debug.info("Nick " + src + " tried to use the '" + cmd + "but it was disabled.")
    # Sends command back to the source of there is no destination specified
    else:
        msgPrefix = "PRIVMSG " + src + " :"
        suffix = "."
        debug.info("Nick " + src + " tried to use the '" + cmd + " in '" + dest + "' but it was disabled.")

    commands.append(msgPrefix + "The " + cmd + " command has been disabled by an administrator" + suffix)

    return commands

def cmdHelp(src, cmd, dest = None):
    '''
    Sends help text for a particular command.  The help file will simply be
    the command name with a .txt ext in the /help directory.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    helpFile = "help/" + cmd + ".txt"

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    # TODO: Need to replace the file sending function here with the one already provided by the Network object.
    if isfile(helpFile):
        file = open(helpFile.lower())
        data = file.readlines()

        for message in data:
            message = message.strip('/r')
            message = message.strip('/n')

            if not (message == ""):
                commands.append(msgPrefix + message)

        file.close()
    # If the file was not found, report the error.
    else:
        debug.error("Help file for command '" + cmd + "' (" + helpFile + ")not found!")
        commands.append(msgPrefix + "I could not find help associated with the '" + cmd + "' command.")

    # Final line saying where further documentation can be found.
    commands.append(
        msgPrefix + "See official documentation at https://github.com/dwhagar/snowboard/wiki for more information.")

    return commands

def denyMessage(src, cmd, dest = None):
    '''
    Access denied message for general use.  Logs to the debug log and provides
    an error message to send back to the user.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
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
    '''
    Stock not authenticated messages for debug and the server.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but has not been authenticated.")
    commands.append(msgPrefix + "You are not identified.")

    return commands

def noChannel(src, cmd, chan, dest = None):
    '''
    Stock message for unable to find a channel in the database.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but I was unable to find channel '" + chan + "' in the database.")
    commands.append(msgPrefix + "I'm sorry but I could not find " + chan + " in the database.")

    return commands

def noOps(src, cmd, chan, dest = None):
    '''
    Stock message for if the bot does not have ops.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' on " + chan + " but I do not have ops.")
    commands.append(msgPrefix + "I'm sorry, but I don't have operator privileges here.")

    return commands

def noUser(src, cmd, user, dest = None):
    '''
    Stock message for a user that does not exist.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
    commands = []

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.message("Nick " + src + " tried to use the '" + cmd + "' command, but " + user + " could not be found in the database.")
    commands.append(msgPrefix + "I'm sorry but I could not find " + user + " in the database.")

    return commands

def paramFail(src, cmd, dest = None):
    '''
    Stock message for an incorrect number of parameters.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command was being used.
    :param dest:
        A string object, defaults to None, defines if a command should be sent
        to a destination other than back to its source.
    :return:
        A list object of commands to be sent to the server.
    '''
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
    '''
    Reports a value error to the user and logs it in the debug log.

    :param src:
        A string object, where a command originated from.
    :param cmd:
        A string object, what command generated the error.
    :param field:
        A string object, what field in the command generated the error.
    :param val:
        A string object, what value was given for the field that generated
        the error.
    :param required:
        A string object, what the required type of value is.
    :param dest:
        A string object, where to send the message.  Default is None,
        if left at None it will send the message back to the source.
    :return:
        A list object of commands to send to the IRC server.
    '''

    if not dest is None:
        msgPrefix = "PRIVMSG " + dest + " :"
    else:
        msgPrefix = "PRIVMSG " + src + " :"

    debug.info(
        "Nick " + src + " tried to use the '" + cmd + "' command but specified '" + val + "' for '" + field + "', which is not a " + required + ".")
    commands = [msgPrefix + "Error:  " + cmd + ":  " + field + " needs to be a " + required + " (was given " + str(
            val) + ")."]

    return commands