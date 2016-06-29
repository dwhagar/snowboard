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
from . import passwordTools
from .user import User
from .userChannel import UserChannel
from .userFlags import UserFlags

def msgTriggers(ircMsg):
    '''Process triggers for user commands.'''
    commands = []

    if ircMsg.dataList[0].lower() == "init" and ircMsg.net.config.init > 0:
        commands = __initCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "addhost":
        commands = __addHost(ircMsg)
    elif ircMsg.dataList[0].lower() == "adduser":
        commands = __addCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "chpass":
        commands = __passwordCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "delhost":
        commands = __delHost(ircMsg)
    elif ircMsg.dataList[0].lower() == "deluser":
        commands = __delCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "ident":
        commands = __identCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "listusers":
        commands = __listUsersCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "moduser":
        commands = __modCmd(ircMsg)
    elif ircMsg.dataList[0].lower() == "userinfo":
        commands = __userInfo(ircMsg)

    return commands

def __addCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    commands = []
    thisCmd = "adduser"

    cmdLen = len(ircMsg.dataList)

    cmdChannel = None
    dataList = ircMsg.dataList[:]

    if cmdLen > 1:
        if ircMsg.dataList[1][0] == "#":
            cmdChannel = ircMsg.dataList[1]
            dataList.remove(cmdChannel)

    if not (cmdLen >= 6 and cmdLen <= 7) and (not cmdChannel is None):
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)
        return commands

    if cmdLen >= 5 and cmdLen <= 7:
        nick = ircMsg.net.findNick(ircMsg.src)

        if nick.authed:
            if nick.user.checkApproved("usermanager"):
                uid = ircMsg.net.users.uidHash(dataList[1])
                exists = ircMsg.net.users.uidExists(uid)

                if not exists:
                    newUser = User()
                    newUser.uid = uid
                    newUser.user = dataList[1]
                    newUser.loadHostmasks(dataList[2])
                    newUser.pwHash = passwordTools.passwordHash(dataList[3])

                    try:
                        newUser.level = int(dataList[4])
                    except ValueError:
                        debug.error("Error with 'adduser':  Level '" + dataList[4] + "' is not a number.")
                        commands.append(
                            "PRIVMSG " + ircMsg.src + " :Unable to execute command, access level '" + dataList[
                                4] + "' is not a number.")
                        return commands

                    if cmdLen > 5:
                        newUser.flags.toData(" ".join(dataList[5:]))

                    # Load the channel in question to the new user.
                    if not (cmdChannel is None):
                        # If the channel isn't known to the bot, don't add
                        # permissions.
                        if not (ircMsg.net.findChannel):
                            commands += basicMessages.noChannel(ircMsg.src, thisCmd, cmdChannel)
                        else:
                            # Move permissions from the user global permissions
                            # to the channel information.
                            newUChannel = UserChannel()
                            newUChannel.name = cmdChannel
                            newUChannel.level = newUser.level
                            newUChannel.flags.approved = newUser.flags.approved
                            newUChannel.flags.denied = newUser.flags.denied
                            newUser.channels.append(newUChannel)

                            # Erase the flags from the global permissions
                            # before adding the user to the database.
                            newUser.level = 0
                            newUser.flags.approve = []
                            newUser.flags.denied = []

                    # Need to make sure, if a user does not have access to
                    # a flag or level they cannot add it to a new user.
                    block = False

                    if not (cmdChannel is None):
                        for flag in newUser.flags.approved:
                            if not nick.user.checkApproved(flag):
                                block = True
                        if nick.user.level <= newUser.level:
                            block = True
                    else:
                        channelObject = nick.user.findChannel(cmdChannel)
                        if not (channelObject is None):
                            for flag in newUChannel.flags.approved:
                                if not channelObject.checkApproved(flag):
                                    block = True
                                if nick.user.checkDenied(flag):
                                    block = True
                        if channelObject.level < newUChannel.level:
                            block = True

                    if not block:
                        ircMsg.net.users.addUser(newUser)
                        if cmdChannel is None:
                            debug.message(
                                "Adding new user " + newUser.user + " to the user database for " + ircMsg.src + ".")
                            commands.append(
                                "PRIVMSG " + ircMsg.src + " :Adding " + newUser.user + " to the user database.")
                        else:
                            debug.message(
                                "Adding new user " + newUser.user + " to the user database of " + newUChannel.name + " for " + ircMsg.src + ".")
                            commands.append(
                                "PRIVMSG " + ircMsg.src + " :Adding " + newUser.user + " to the " + newUChannel.name + " user database.")
                    else:
                        debug.error(
                            "Error with 'adduser':  User " + ircMsg.src + " attempted to grant privleges to " + newUser.user + " greater than his/her own access.")
                        commands.append(
                            "PRIVMSG " + ircMsg.src + " :Command failed, you cannot add greater privleges than the ones you possess.")
                else:
                    debug.error("Error with 'adduser':  User " + dataList[1] + " already exists.")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Command failed, user " + dataList[1] + " already exists.")
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __addHost(ircMsg):
    '''Adds a hostmask to the users own account.'''
    commands = []
    thisCmd = "addhost"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) == 2:
        if nick.auth:
            nick.user.hostmasks.append(ircMsg.dataList[1].lower())
            nick.user.hostmasks = list(set(nick.user.hostmasks))
            ircMsg.net.users.updateUser(nick.user)
            nick.getPrivs()

            debug.info("User " + ircMsg.src + " added hotmask " + ircMsg.dataList[1] + " to their account.")
            commands.append(
                "PRIVMSG " + ircMsg.src + " :Successfully added hotmask " + ircMsg.dataList[1] + " to your account.")
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands


def __changeFlags(ircMsg, modUser, nick, thisCmd, nickChannel = None, modChannel = None):
    '''Add or remove flags from a user profile.'''
    commands = []

    flags = ircMsg.dataList[3].lower()
    newFlags = UserFlags()
    newFlags.toData(flags)

    if ircMsg.dataList[2].lower() == "addflags":
        # Add the new flags to the user object.
        if modChannel is None:
            modUser.flags.approved += newFlags.approved
            modUser.flags.denied += newFlags.denied
        else:
            modChannel.flags.approved += newFlags.approved
            modChannel.flags.denied += newFlags.approved
        action = "added"
    elif ircMsg.dataList[2].lower() == "delflags":
        # Remove the new flags from the user object.
        if modChannel is None:
            for flag in newFlags.approved:
                if flag in modUser.flags.approved:
                    modUser.flags.approved.remove(flag)
            for flag in newFlags.denied:
                if flag in modUser.flags.denied:
                    modUser.flags.denied.remove(flag)
        else:
            for flag in newFlags.approved:
                if flag in modChannel.flags.approved:
                    modChannel.flags.approved.remove(flag)
            for flag in newFlags.denied:
                if flag in modChannel.flags.denied:
                    modChannel.flags.denied.remove(flag)
        action = "removed"
    elif ircMsg.dataList[2].lower() == "setflags":
        # Replaces the flags of a specific user.
        if modChannel is None:
            modUser.flags.approved = newFlags.approved
            modUser.flags.denied = newFlags.denied
        else:
            modChannel.flags.approved = newFlags.approved
            modChannel.flags.denied = newFlags.denied
        action = "set"

    # Make sure there is sufficient access to modify.
    blocked = __levelBlock(-1, nick, modUser, nickChannel, modChannel)

    # If there is sufficient access, then make the changes.
    if not blocked:
        modUser.flags.cleanFlags()
        ircMsg.net.users.updateUser(modUser)
        ircMsg.net.resetPrivs(modUser.uid)
        debug.message(
            "User " + ircMsg.src + " used the 'moduser' command to " + action + " flags on account " + modUser.name + ".")
        commands.append(
            "PRIVMSG " + ircMsg.src + " :Successfully " + action + " flags " + flags + " on account " + modUser.name + ".")
    else:
        commands += basicMessages.denyMessage(ircMsg.src, thisCmd)

    return commands


def __changeHosts(ircMsg, modUser, nick, thisCmd):
    '''Changes the hosts associated with a user profile.'''
    commands = []

    hostmasks = ircMsg.dataList[3].lower().split(',')
    if ircMsg.dataList[2].lower() == "addhost":
        modUser.hostmasks += hostmasks
        modUser.hostmasks = list(set(modUser.hostmasks))
    elif ircMsg.dataList[2].lower() == "delhost":
        for host in hostmasks:
            if host in modUser.hostmasks:
                modUser.hostmasks.remove(host)
    elif ircMsg.dataList[2].lower() == "sethost":
        modUser.hostmasks = hostmasks
        modUser.hostmasks = list(set(modUser.hostmasks))

    # Check for privileges.
    if nick.user.level > modUser.level:
        if len(modUser.hostmasks) > 0:
            ircMsg.net.users.updateUser(modUser)
            ircMsg.net.resetPrivs(modUser.uid)
            debug.message(
                "User " + ircMsg.src + " used the 'moduser' command to hostmasks of " + modUser.name + " to " + ",".join(
                    modUser.hostmasks) + ".")
            commands.append(
                "PRIVMSG " + ircMsg.src + " :Successfully changed hostmasks " + modUser.name + " to " + ",".join(
                    modUser.hostmasks) + ".")
        else:
            debug.info("User " + ircMsg.src + " tried to remove all hostmasks from user " + modUser.name + ".")
            commands.append("PRIVMSG " + ircMsg.src + " :You cannot remove all hostmasks from a user.")
    else:
        commands += basicMessages.denyMessage(ircMsg.src, thisCmd)

    return commands

def __delCmd(ircMsg):
    '''Removes a user from the user database.'''
    commands = []
    thisCmd = "deluser"

    if len(ircMsg.dataList) == 2:
        nick = ircMsg.net.findNick(ircMsg.src)

        user = ircMsg.dataList[1]

        if nick.authed:
            if nick.user.checkApproved("usermanager"):
                uid = ircMsg.net.users.uidHash(user)
                exists = ircMsg.net.users.uidExists(uid)

                if exists:
                    userData = ircMsg.net.users.userInformation(uid)

                    if nick.user.level > userData.level:
                        ircMsg.net.users.removeUser(uid)
                        ircMsg.net.removeAccess(uid)

                        debug.message("User " + ircMsg.src + " removed " + user + " from the user database.")
                        commands.append("PRIVMSG " + ircMsg.src + " :Removing " + user + " from the user database.")
                    else:
                        debug.message(
                            "User " + ircMsg.src + " tried to remove " + user + " from the database, did not have high enough access.")
                        commands.append("PRIVMSG " + ircMsg.src + " :You cannot remove " + user + ", your access level is not high enough.")
                else:
                    commands += basicMessages.noUser(ircMsg.src, thisCmd, user)
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __delHost(ircMsg):
    '''Removes a hostname from the users own profile.'''
    commands = []
    thisCmd = "delhost"

    nick = ircMsg.net.findNick(ircMsg.src)
    host = ircMsg.dataList[1].lower()

    if len(ircMsg.dataList) == 2:
        if nick.auth:
            if len(nick.user.hostmasks) > 1:
                if host in nick.user.hostmasks:
                    nick.user.hostmasks.remove(host)
                ircMsg.net.users.updateUser(nick.user)
                nick.getPrivs()

                debug.info("User " + ircMsg.src + " added hotmask " + ircMsg.dataList[1] + " to their account.")
                commands.append("PRIVMSG " + ircMsg.src + " :Successfully added hotmask " + ircMsg.dataList[
                    1] + " to your account.")
            else:
                debug.info("User " + ircMsg.src + " tried to remove all the hostmasks from their account.")
                commands.append("PRIVMSG " + ircMsg.src + " :You cannot remove all the hostmasks from your account.")
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands


def __flagBlock(flag, nick, nickChannel = None):
    '''Determines if flags should block a user from access to a command.'''
    if not (nickChannel is None):
        chanApproved = nickChannel.checkApproved(flag)
        chanDenied = nickChannel.checkDenied(flag)
    else:
        chanApproved = False
        chanDenied = False

    globalApproved = nick.user.checkApproved(flag)

    blocked = (not (chanApproved or globalApproved)) or chanDenied

    return blocked


def __formatChannels(dest, channels):
    '''Takes a list of UserChannel objects and formats them for output.'''
    commands = []
    messageCmd = "PRIVMSG " + dest + " :"

    for channel in channels:
        message = "Channel: " + channel.name + "; Level: " + str(channel.level)
        if len(channel.flags.approved) > 0:
            message += "; Approved Flags: " + ",".join(channel.flags.approved)
        if len(channel.flags.denied) > 0:
            message += "; Denied Flags: " + ",".join(channel.flags.denied)
        commands.append(messageCmd + message)

    return commands

def __formatUser(dest, userObject):
    '''Takes a User object and formats output for IRC with the info.'''
    commands = []
    messageCmd = "PRIVMSG " + dest + " :"

    # Basic information.
    commands.append(messageCmd + "Username: " + userObject.user)
    commands.append(messageCmd + "Hostmask(s): " + userObject.saveHostmasks())

    # Add all global flags to the text and user global level.
    message = messageCmd + "Level: " + str(userObject.level)

    if not (userObject.flags.approved == []):
        message += "; Approved Flags: " + ",".join(userObject.flags.approved)
    if not (userObject.flags.approved == []):
        message += "; Denied Flags: " + ",".join(userObject.flags.denied)

    commands.append(message)

    # Now for the channels.
    if len(userObject.channels) > 0:
        commands += __formatChannels(dest, userObject.channels)

    return commands

def __formatUserLine(userObject, channel = None):
    '''Formats a single line of user information.'''
    user = userObject.user
    channels = ""

    if channel is None:
        level = str(userObject.level)
        approved = ",".join(userObject.flags.approved)
        denied = ",".join(userObject.flags.denied)

        if len(userObject.channels) > 0:
            chanList = []

            for chan in userObject.channels:
                chanList.append(chan.name)

            channels = ",".join(chanList)
    else:
        level = str(channel.level)
        approved = ",".join(channel.flags.approved)
        denied = ",".join(channel.flags.denied)

    message = "User: " + user + "; Level: " + level

    if not approved == "":
        message += "; Approval Flags: " + approved
    if not denied == "":
        message += "; Denied Flags: " + denied
    if not channels == "":
        message += "; Channels: " + channels

    return message

def __identCmd(ircMsg):
    '''Identify command to authenticate a user.'''
    thisCmd = "ident"

    if len(ircMsg.dataList) >= 2:
        nick = ircMsg.net.findNick(ircMsg.src)
        commands = nick.auth(ircMsg.dataList[1])
    else:
        commands = basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __initCmd(ircMsg):
    '''Execute the tasks for the special init command.'''
    commands = []
    thisCmd = "init"

    if len(ircMsg.dataList) == 3:
        debug.message("Initialized admin user " + ircMsg.src + " with hostmask " + ircMsg.dataList[1] + ".")

        userObject = User()

        userObject.uid = ircMsg.net.users.uidHash(ircMsg.src)
        exists = ircMsg.net.users.uidExists(userObject.uid)

        if not exists:
            userObject.hostmasks = [ircMsg.dataList[1]]
            userObject.pwHash = passwordTools.passwordHash(ircMsg.dataList[2])
            userObject.name = ircMsg.src
            userObject.uid = ircMsg.net.users.uidHash(ircMsg.src)
            userObject.level = 255

            ircMsg.net.users.addUser(userObject)
            ircMsg.net.config.init = 0
            commands.append("PRIVMSG " + ircMsg.src + " :Added user " + userObject.name + " to the master database, as admin.  Disabling 'init' command.  For security, please do not start the bot with the -i / --init options again.")
        else:
            debug.error("Error with 'init':  User " + userObject.user + " already exists.")
            commands.append("PRIVMSG " + ircMsg.src + " :Command failed, user " + userObject.name + " already exists.")
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands


def __levelBlock(level, nick, modUser, nickChannel = None, modChannel = None):
    '''Determines if level should block a user from access to a command.'''
    # When not looking to change someone's level, use -1 for level to disable
    # that check.
    if modChannel is None:
        blocked = (nick.user.level <= modUser.level) or (nick.user.level <= level)
    else:
        if nickChannel is None:
            blocked = (nick.user.level <= modChannel.level) or (nick.user.level <= level)
        else:
            blocked = ((nickChannel.level <= modChannel.level) or (nickChannel.level <= level)) and (
            nickChannel.level > 0)

    return blocked

def __listUsersCmd(ircMsg):
    '''Provides a list of users.'''
    commands = []
    thisCmd = "listusers"

    # Make sure the command is long enough.
    if len(ircMsg.dataList) > 1:
        channel = ircMsg.dataList[1]
    else:
        channel = None

    # Grab the information on who sent he command.
    nick = ircMsg.net.findNick(ircMsg.src)

    # Make sure that they are authenticated.
    if nick.authed:
        data = ircMsg.net.users.getUsers()

        # If the command is long enough, then pull the channel information.
        if len(data) > 0:
            if channel is None:
                commands.append("PRIVMSG " + ircMsg.src + " :Here are the users in my database.")

                for item in data:
                    message = __formatUserLine(item)
                    commands.append("PRIVMSG " + ircMsg.src + " :" + message)
            else:
                foundOne = False

                commands.append("PRIVMSG " + ircMsg.src + " :Here are the users in my database for channel " + channel + ".")

                for item in data:
                    itemChannel = item.findChannel(channel)
                    if not (itemChannel is None):
                        foundOne = True
                        message = __formatUserLine(item, itemChannel)
                        commands.append("PRIVMSG " + ircMsg.src + " :" + message)

                if not foundOne:
                    commands.append("PRIVMSG " + ircMsg.src + " :I was unable to find any users who specifically have access to " + channel + ".")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Remember that any user who has global access, not tied to a specific channel, has equal access in all channels.")
        else:
            debug.warn("Nick " + ircMsg.src + " was looking for the user list, but there are no users in that channel.")
            commands.append("PRIVMSG " + ircMsg.src + " :There are no users on the user list.  I think something went wrong!")
    else:
        commands += basicMessages.noAuth(ircMsg.src, thisCmd)

    return commands

def __modCmd(ircMsg):
    '''Modifies a user already in the database.'''
    commands = []
    thisCmd = "moduser"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) == 4:
        if nick.authed:
            if nick.user.checkApproved("usermanager"):
                # First we have to get the user for which we want to modify.
                userName = ircMsg.dataList[1].lower()
                uid = ircMsg.net.users.matchUser(userName)
                modUser = ircMsg.net.users.userInformation(uid)

                if not uid is None:
                    # ModUser Commands
                    if ircMsg.dataList[2].lower() == "level":
                        # Adjusts the level of a user.
                        commands += __setLevel(ircMsg, nick, modUser, thisCmd)
                    elif ircMsg.dataList[2].lower() == "addflags" or ircMsg.dataList[2].lower() == "delflags" or \
                                    ircMsg.dataList[2].lower() == "setflags":
                        commands += __changeFlags(ircMsg, nick, modUser, thisCmd)
                    elif ircMsg.dataList[2].lower() == "addhosts" or ircMsg.dataList[2].lower() == "delhosts" or \
                                    ircMsg.dataList[2].lower() == "sethosts":
                        commands += __changeHosts(ircMsg, nick, modUser, thisCmd)
                    elif ircMsg.dataList[2].lower() == "password":
                        # Allows someone to reset another users password.
                        if nick.user.level > modUser.level:
                            modUser.pwHash = passwordTools.passwordHash(ircMsg.dataList[3])
                            ircMsg.net.users.updateUser(modUser)
                            ircMsg.net.resetPrivs(uid)
                            debug.message("User " + ircMsg.src + " set a new password for " + userName + ".")
                            commands.append("PRIVMSG " + ircMsg.src + " :Password for " + userName + " has been set.")
                        else:
                            commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
                    elif ircMsg.dataList[2].lower() == "rmchan":
                        # Allows a channel to be removed from a user profile.
                        channelName = ircMsg.dataList[3].lower()
                        modChannel = modUser.findChannel(channelName)

                        if not (modChannel is None):
                            modUser.channels.remove(modChannel)
                            # Save the new user information.
                            ircMsg.net.users.updateUser(modUser)
                            ircMsg.net.resetPrivs(uid)
                            debug.message(
                                "User " + ircMsg.src + " removed channel " + channelName + " from " + userName + ".")
                            commands.append(
                                "PRIVMSG " + ircMsg.src + " :Channel " + channelName + " removed from " + userName + ".")
                        else:
                            debug.message(
                                "User " + ircMsg.src + " attempted to remove " + channelName + " from " + userName + " but no special privileges were found.")
                            commands.append(
                                "PRVIMSG " + ircMsg.src + " :User " + userName + " does not have special privileges on channel " + channelName + ".")
                    else:
                        commands += basicMessages.paramFail(ircMsg.src, thisCmd)
                else:
                    commands += basicMessages.noUser(ircMsg.src, thisCmd, userName)
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)

    # Handle channel related commands which will have username and channel.
    elif len(ircMsg.dataList) == 5:
        if nick.authed:
            channelName = ircMsg.dataList[4]
            ircChannel = ircMsg.net.findChannel(channelName)

            if not (ircChannel is None):
                nickChannel = nick.user.findChannel(channelName)

                blocked = __flagBlock("usermanager", nick, nickChannel)

                if not blocked:
                    # First we have to get the user for which we want to modify.
                    userName = ircMsg.dataList[1].lower()
                    uid = ircMsg.net.users.matchUser(userName)
                    modUser = ircMsg.net.users.userInformation(uid)

                    modChannel = modUser.findChannel(channelName)

                    if not (uid is None):
                        if modChannel is None:
                            # Rather than error out, we will add the channel
                            # to the user if it doesn't already exist.
                            modChannel = UserChannel()
                            modChannel.name = channelName
                            modUser.channels.append(modChannel)

                        # ModUser Channel Commands
                        if ircMsg.dataList[2].lower() == "level":
                            # Adjusts the level of a user on a channel.
                            commands += __setLevel(ircMsg, nick, modUser, thisCmd, nickChannel, modChannel)
                        elif ircMsg.dataList[2].lower() == "addflags" or ircMsg.dataList[2].lower() == "delflags" or \
                                        ircMsg.dataList[2].lower() == "setflags":
                            # Adjusts the flags of a user on a channel.
                            commands += __changeFlags(ircMsg, nick, modUser, thisCmd, nickChannel, modChannel)
                        else:
                            commands += basicMessages.paramFail(ircMsg.src, thisCmd)
                    else:
                        commands += basicMessages.noUser(ircMsg.src, thisCmd, userName)
                else:
                    commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
            else:
                commands += basicMessages.noChannel(ircMsg.src, thisCmd, channelName)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)

    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __passwordCmd(ircMsg):
    '''Allows a user to change their own password.'''
    commands = []
    thisCmd = "chpass"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) == 2:
        if nick.authed:
            newpass = ircMsg.dataList[1]
            nick.user.pwHash = passwordTools.passwordHash(newpass)
            ircMsg.net.users.updateUser(nick.user)
            debug.info("User " + ircMsg.src + " updated their password.")
            commands.append("PRIVMSG " + ircMsg.src + " :Your password has been updated.")
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __setLevel(ircMsg, nick, modUser, thisCmd, nickChannel = None, modChannel = None):
    '''Adjusts a user level.'''
    commands = []

    level = ircMsg.dataList[3]

    try:
        level = int(level)
    except ValueError:
        commands += basicMessages.valError(nick.name, thisCmd, "level", level, "number between 0 and 255")
        return commands

    blocked = __levelBlock(level, nick, modUser, nickChannel, modChannel)

    if not blocked:
        if modChannel is None:
            modUser.level = level
        else:
            modChannel.level = level

        ircMsg.net.users.updateUser(modUser)
        ircMsg.net.resetPrivs(modUser.uid)
        debug.message(
            "User " + ircMsg.src + " used the 'moduser' command to change the level of " + modUser.user + " to " + str(
                level) + ".")
        commands.append("PRIVMSG " + ircMsg.src + " :Successfully changed user level of " + modUser.user + " to " + str(
            level) + ".")
    else:
        commands += basicMessages.denyMessage(ircMsg.src, thisCmd)

    return commands

def __userInfo(ircMsg):
    '''Gets information on a user and displays it.'''
    commands = []
    thisCmd = "userinfo"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) == 2:
        if nick.authed:
            userName = ircMsg.dataList[1]
            uid = ircMsg.net.users.matchUser(userName)

            if not (uid is None):
                user = ircMsg.net.users.userInformation(uid)
                debug.info("User " + ircMsg.src + " requested user information on " + userName + ".")
                commands += __formatUser(ircMsg.src, user)
            else:
                basicMessages.noUser(ircMsg.src, thisCmd, userName)
        else:
            basicMessages.noAuth(ircMsg.src, thisCmd)
    else:
        basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands
