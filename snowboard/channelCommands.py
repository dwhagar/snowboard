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
Commands relating to channel management.  Channel flags of use here
are:

keeptopic
noweather
norules
nochans
'''

import pyowm
import random
from os.path import isfile
from . import basicMessages
from . import debug

def channelTriggers(ircMsg):
    '''Processes channel triggers for channel fucntions.'''
    commands = []

    if ircMsg.dataList[0] == "^opme":
        commands = __opmeCommand(ircMsg)
    elif ircMsg.dataList[0] == "^reset":
        commands = __resetTopic(ircMsg)
    elif ircMsg.dataList[0] == "^desc":
        commands = __showDesc(ircMsg)
    elif ircMsg.dataList[0] == "^rules":
        __showRules(ircMsg)
    elif ircMsg.dataList[0] == "^chans":
        __showChans(ircMsg)
    elif ircMsg.dataList[0] == "^w":
        commands = __showWeather(ircMsg)
    elif ircMsg.dataList[0] == "^button":
        commands = __buttonPress(ircMsg)

    return commands

def msgTriggers(ircMsg):
    '''Processes message triggers for channel functions.'''
    commands = []

    if ircMsg.dataList[0] == "modchan":
        commands = __modChannel(ircMsg)

    return commands

def resetTopics(net):
    '''Resets all channel topics to default.'''
    commands = []

    for chan in net.channels:
        if (not chan.defaultTopic == "") and chan.opped:
            if (not chan.topic == chan.defaultTopic) and chan.checkFlag("keeptopic"):
                commands.append("TOPIC " + chan.name + " :" + chan.defaultTopic)

    return commands


def __buttonPress(ircMsg):
    '''The infamous button script.'''
    commands = []

    nick = ircMsg.net.findNick(ircMsg.src)
    chan = ircMsg.net.findChannel(ircMsg.dest)
    chanNick = chan.findNick(nick)

    if (len(ircMsg.dataList) > 1) and (not chan.checkFlag("ic")):
        if ircMsg.dataList[1].lower() == "on":
            if chanNick[1].op:
                chan.removeFlag("nobutton")
                commands.append("PRIVMSG " + ircMsg.dest + " :The button is now turned on.")
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :You do not have ops in this channel.")
        elif ircMsg.dataList[1].lower() == "off":
            if chanNick[1].op:
                chan.addFlag("nobutton")
                commands.append("PRIVMSG " + ircMsg.dest + " :The button is now turned off.")
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :You do not have ops in this channel.")
        elif not chan.checkFlag("nobutton"):
            target = " ".join(ircMsg.dataList[1:])
            source = ircMsg.src
            fileName = "button.txt"
            lines = []

            if (not target.lower() == source.lower()) and (not target.lower() == ircMsg.net.botnick.lower()):
                if isfile(fileName):
                    file = open(fileName)
                    data = file.readlines()

                    for message in data:
                        message = message.strip('/r')
                        message = message.strip('/n')

                        if not (message == ""):
                            lines.append(message)

                    file.close()

                    random.seed()
                    choice = random.choice(lines)

                    choice = choice.replace("::source::", source)
                    choice = choice.replace("::target::", target)

                    commands.append("PRIVMSG " + ircMsg.dest + " :" + choice)
                else:
                    debug.error("Could not send file " + fileName + ", the file was not found.")
                    commands.append(
                        "PRIVMSG " + ircMsg.dest + " :That information could not be located.  Please contact the bot admin.")
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :Don't ask me to do that, it's just not right.")
    else:
        commands.append("PRIVMSG " + ircMsg.dest + " :You should really tell me whose button you want me to push.")
    return commands

def __modChannel(ircMsg):
    '''Commands to change channel properties.'''
    commands = []
    thisCmd = "modchan"

    nick = ircMsg.net.findNick(ircMsg.src)

    if len(ircMsg.dataList) >= 3:
        chan = ircMsg.net.findChannel(ircMsg.dataList[1])
        cmd = ircMsg.dataList[2]

        if len(ircMsg.dataList) >= 4:
            data = " ".join(ircMsg.dataList[3:])
        else:
            data = ""

        if not chan is None:
            if nick.user.checkApproved("channelmanager", chan.name):
                if cmd == "addflags":
                    data.replace(" ", "")
                    list = data.split(",")
                    if not list == []:
                        for flag in list:
                            chan.addFlag(flag)
                        debug.message("Channel flags were added to " + chan.name + " by " + ircMsg.src + ".")
                        commands.append("PRIVMSG " + ircMsg.src + " :Flags added to " + chan.name + ".")
                    else:
                        commands += basicMessages.paramFail(ircMsg.src, cmd)
                elif cmd == "delflags":
                    data.replace(" ", "")
                    list = data.split(",")
                    if not list == []:
                        for flag in list:
                            chan.removeFlag(flag)
                        debug.message("Channel flags were added to " + chan.name + " by " + ircMsg.src + ".")
                        commands.append("PRIVMSG " + ircMsg.src + " :Flags added to " + chan.name + ".")
                    else:
                        commands += basicMessages.paramFail(ircMsg.src, cmd)
                elif cmd == "desc":
                    debug.info("Channel description requested by " + ircMsg.src + ".")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Description for " + chan.name + " is '" + chan.desc + "'.")
                elif cmd == "flags":
                    debug.info("Channel flags requested by " + ircMsg.src + ".")
                    if chan.flags == []:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has no flags set.")
                    else:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has flags " + ",".join(
                            chan.flags) + ".")
                elif cmd == "settopic":
                    chan.defaultTopic = data
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Default topic for " + chan.name + " has been set.")
                    debug.message("Default topic for " + chan.name + " was set by " + ircMsg.src + ".")
                elif cmd == "setdesc":
                    chan.desc = data
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Description for " + chan.name + " has been set.")
                    debug.message("Channel description for " + chan.name + " was set by " + ircMsg.src + ".")
                elif cmd == "setflags":
                    data.replace(" ", "")
                    data = data.lower()
                    chan.flags = data.split(",")
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Flags for " + chan.name + " have been set.")
                    debug.message("Channel flags for " + chan.name + " were set by " + ircMsg.src + ".")
                elif cmd == "topic":
                    debug.info("Default topic requested by " + ircMsg.src + ".")
                    commands.append(
                        "PRIVMSG " + ircMsg.src + " :Default topic for " + chan.name + " is '" + chan.defaultTopic + "'.")
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd)
        else:
            commands += basicMessages.noChannel(ircMsg.src, thisCmd, ircMsg.dataList[1])
    else:
        commands += basicMessages.paramFail(ircMsg.src, thisCmd)

    return commands

def __opmeCommand(ircMsg):
    '''Allows a person to gain ops in a channel when allowed.'''
    commands = []
    thisCmd = "^opme"

    nick = ircMsg.net.findNick(ircMsg.src)
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if chan.opped:
        if nick.authed:
            if nick.user.checkApproved("channelmanager", ircMsg.dest) or nick.user.checkApproved("ops", ircMsg.dest):
                commands.append("MODE " + ircMsg.dest + " +o " + ircMsg.src)
            elif nick.user.checkApproved("voice", ircMsg.dest):
                commands.append("MODE " + ircMsg.dest + " +v " + ircMsg.src)
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd, ircMsg.dest)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd, ircMsg.dest)
    else:
        commands += basicMessages.noOps(ircMsg.src, thisCmd, chan.name, ircMsg.dest)

    return commands

def __resetTopic(ircMsg):
    '''Resets a given channels topic to default.'''
    commands = []
    thisCmd = "^reset"

    nick = ircMsg.net.findNick(ircMsg.src)
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if chan.opped:
        if nick.authed:
            if nick.user.checkApproved("channelmanager", ircMsg.dest):
                commands.append("TOPIC " + chan.name + " :" + chan.defaultTopic)
            else:
                commands += basicMessages.denyMessage(ircMsg.src, thisCmd, ircMsg.dest)
        else:
            commands += basicMessages.noAuth(ircMsg.src, thisCmd, ircMsg.dest)
    else:
        commands += basicMessages.noOps(ircMsg.src, thisCmd, chan.name, ircMsg.dest)

    return commands


def __showChans(ircMsg):
    '''Shows rules from the rules.txt help file.'''
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if not chan.checkFlag("nochans"):
        ircMsg.net.sendFile("help/chans.txt", "NOTICE", ircMsg.src)

def __showDesc(ircMsg):
    '''Sends a channel description to a user.'''
    commands = []

    chan = ircMsg.net.findChannel(ircMsg.dest)

    if chan.desc == "":
        commands.append("NOTICE " + ircMsg.src + " :There is no description for this channel.")
    else:
        commands.append("NOTICE " + ircMsg.src + " :" + chan.desc)

    debug.info("Nick " + ircMsg.src + " requested the channel description for " + chan.name + ".")

    return commands

def __showRules(ircMsg):
    '''Shows rules from the rules.txt help file.'''
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if not chan.checkFlag("norules"):
        ircMsg.net.sendFile("help/rules.txt", "NOTICE", ircMsg.src)


def __showWeather(ircMsg):
    '''Shows the current weather by city.'''
    commands = []
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if not chan.checkFlag("noweather") and len(ircMsg.dataList) > 0:
        weather = pyowm.OWM("337b19f7282e26f73f44973a7ce90472")
        city = " ".join(ircMsg.dataList[1:])
        current = weather.weather_at_place(city)

        if not current is None:
            location = current.get_location()
            locationText = location.get_name()
            data = current.get_weather()
            tempDataF = data.get_temperature('fahrenheit')
            tempDataC = data.get_temperature('celsius')
            conditions = data.get_detailed_status().title()
            tempHigh = "::I::" + str(round(tempDataF['temp_max'])) + "F/" + str(round(tempDataC['temp_max'])) + "C::I::"
            tempLow = "::I::" + str(round(tempDataF['temp_min'])) + "F/" + str(round(tempDataC['temp_min'])) + "C::I::"
            tempNow = "::I::" + str(round(tempDataF['temp'])) + "F/" + str(round(tempDataC['temp'])) + "C::I::"

            weatherText = "Current conditions for ::B::" + locationText + "::B:::  ::I::" + conditions + "::I:: and " + tempNow + " with a high of " + tempHigh + " and a low of " + tempLow + "."
            commands.append("PRIVMSG " + ircMsg.dest + " :" + weatherText)
        else:
            commands.append("PRIVMSG " + ircMsg.dest + " :I could not find weather data for that location.")

    return commands
