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
Commands relating to channel management.
'''

import urllib.parse
import urllib.request
import urllib.error
import json
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
        commands = __showRules(ircMsg)
    elif ircMsg.dataList[0] == "^chans":
        commands = __showChans(ircMsg)
    elif ircMsg.dataList[0] == "^w":
        commands = __showWeather(ircMsg)
    elif ircMsg.dataList[0] == "^button":
        commands = __buttonPress(ircMsg)
    elif ircMsg.dataList[0] == "^help":
        commands = __chanHelp(ircMsg)
    elif ircMsg.dataList[0] == "^announcement":
        commands = __announce(ircMsg)

    return commands

def joinTriggers(ircMsg):
    commands = []

    commands += __announce(ircMsg)

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

def __announce(ircMsg):
    commands = []

    chan = ircMsg.net.findChannel(ircMsg.dest)

    if not chan is None:
        if (not (chan.botnick.lower() == ircMsg.src.lower())) and (not (chan.announce == "")):
            commands.append("NOTICE " + ircMsg.src + " :" + chan.announce)

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

def __chanHelp(ircMsg):
    '''Sends channel commands to a person.'''
    chan = ircMsg.net.findChannel(ircMsg.dest)

    commands = []
    cmd = "^help"

    if not chan.checkFlag("nohelp"):
        ircMsg.net.sendFile("help/channel-help.txt", "NOTICE", ircMsg.src)
    else:
        commands += basicMessages.cmdDisabled(ircMsg.src, cmd, ircMsg.dest)

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
                elif cmd == "announce":
                    debug.info("Channel announcement requested by " + ircMsg.src + ".")
                    if chan.announce == "":
                        commands.append("PRIVMSG " + ircMsg.src + " :Announcement for " + chan.name + " is not set.")
                    else:
                        commands.append(
                            "PRIVMSG " + ircMsg.src + " :Announcement for " + chan.name + " is '" + chan.announce + "'.")
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
                    if chan.desc == "":
                        commands.append("PRIVMSG " + ircMsg.src + " :Description for " + chan.name + " is not set.")
                    else:
                        commands.append(
                            "PRIVMSG " + ircMsg.src + " :Description for " + chan.name + " is '" + chan.desc + "'.")
                elif cmd == "flags":
                    debug.info("Channel flags requested by " + ircMsg.src + ".")
                    if chan.flags == []:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has no flags set.")
                    else:
                        commands.append("PRIVMSG " + ircMsg.src + " :Channel " + chan.name + " has flags " + ",".join(
                            chan.flags) + ".")
                elif cmd == "setannounce":
                    chan.announce = data
                    chan.saveData()
                    commands.append("PRIVMSG " + ircMsg.src + " :Announcement for " + chan.name + " has been set.")
                    debug.message("Announcement for " + chan.name + " was set by " + ircMsg.src + ".")
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
                    if chan.defaultTopic == "":
                        commands.append("PRIVMSG " + ircMsg.src + " :Default topic for " + chan.name + " is not set.")
                    else:
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

    commands = []
    cmd = "^chans"

    if not chan.checkFlag("nochans"):
        ircMsg.net.sendFile("help/chans.txt", "NOTICE", ircMsg.src)
    else:
        commands += basicMessages.cmdDisabled(ircMsg.src, cmd, ircMsg.dest)

    return commands

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

    commands = []
    cmd = "^rules"

    if not chan.checkFlag("norules"):
        ircMsg.net.sendFile("help/rules.txt", "NOTICE", ircMsg.src)
    else:
        commands += basicMessages.cmdDisabled(ircMsg.src, cmd, ircMsg.dest)

    return commands

def __showWeather(ircMsg):
    '''Shows the current weather by city.'''
    commands = []
    cmd = "^w"
    chan = ircMsg.net.findChannel(ircMsg.dest)

    if not chan.checkFlag("noweather") and len(ircMsg.dataList) > 0:
        city = " ".join(ircMsg.dataList[1:])
        yahooURL = "https://query.yahooapis.com/v1/public/yql?"
        yql = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='{0}')".format(
            city)
        query = [('q', yql), ('format', 'json')]
        url = yahooURL + urllib.parse.urlencode(query)
        debug.message(yql)
        debug.message(url)
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as err:
            response = err

        if response.code == 200:
            data = json.loads(response.read().decode('utf-8'))
            if not data['query']['results'] is None:
                locationData = data['query']['results']['channel']['location']
                conditionData = data['query']['results']['channel']['item']['condition']
                high = int(data['query']['results']['channel']['item']['forecast'][0]['high'])
                low = int(data['query']['results']['channel']['item']['forecast'][0]['low'])
                current = int(conditionData['temp'])
                date = data['query']['results']['channel']['lastBuildDate']
                humidity = data['query']['results']['channel']['atmosphere']['humidity']
                conditionText = "::B::" + conditionData['text'] + "::B:: and ::I::" + __tempString(
                    current) + "::I:: with a high of ::I::" + __tempString(
                    high) + "::I::, a low of ::I::" + __tempString(low) + "::I::, and " + humidity + "% humidity"
                locationText = locationData['city'] + "," + locationData['region'] + ", " + locationData['country']
                text = "In ::B::" + locationText + "::B:: the time is " + date + ".  Current conditions are " + conditionText + "."
                commands.append("PRIVMSG " + ircMsg.dest + " :" + text)
            else:
                commands.append("PRIVMSG " + ircMsg.dest + " :I could not find any information on that location.")
        else:
            errorCode = str(response.code)
            commands.append(
                "PRIVMSG " + ircMsg.dest + " :There was an problem getting information on that location, error code is '" + errorCode + "'.")
    else:
        commands += basicMessages.cmdDisabled(ircMsg.src, cmd, ircMsg.dest)

    return commands

def __tempString(temp):
    '''Returns a formatted temperature string given temp in F'''
    f = temp
    c = round((f - 32) * 5 / 9)

    text = str(f) + "F/" + str(c) + "C"

    return text
