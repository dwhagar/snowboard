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
This acts at the core of the script where the network and configuration
objects are directly created and manipulated.  Commands to be sent back to
the network object for sending to the IRC server should be formatted as lists
of strings, each item being a single command.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

# The amount of time the loop with sleep before going on to the next loop.
idleTime = 1 / 8

import argparse
import time
from os.path import isfile

from . import config
from . import network
from . import debug
from . import scripts
from . import ircMessage
from . import ctcpGlobals

def __parse_args(argv, cfg):
    """Parse command-line arguments."""
    argparser = argparse.ArgumentParser(
        prog="snowboard",
        description="IRC Bot Written in Python 3.",
        fromfile_prefix_chars="@")

    # Use the -1 default so that the system knows if verbosity is being
    # overriden by the command line.
    argparser.add_argument("--verbose", "-v",
                           default=0, action="count",
                           help="increase output verbosity")

    # Default to snowboard.ini.
    argparser.add_argument("--config", "-c",
                           default="snowboard.ini",
                           help="specify the configuration file to use.")

    # The init command is used to define the system administrator, or, first
    # user when the bot is run for the first time, and should only be enabled
    # once, to initialize the user database.
    argparser.add_argument("--init", "-i",
                           default=0, action="count",
                           help="tell the bot to accept the init command.")

    # Load all the options from the configuration.
    cfg.options = argparser.parse_args(argv)
    debug.verbosity = cfg.options.verbose
    cfg.init = cfg.options.init
    cfg.file = cfg.options.config

def __process_responses(net, raw):
    '''
    Process responses from the server and pass instructions to the network
    object.
    '''
    response = raw.split()
    cmds = []

    # Process WHO responses to get hostnames.
    if response[1] == "352":
        net.processWho(response)
    # Process NAMES responses to get all names for channels joined.
    elif response[1] == "353":
        net.processNames(response)
    # Process the server closing the link (per RFC 2812)
    elif " ".join(response[1:3]).strip(':').lower() == "closing link":
        net.disconnect()
    # Process a QUIT message.
    elif response[1] == "QUIT":
        net.processQuit(response)
    # Process JOIN and PART messages.
    elif response[1] == "JOIN" or response[1] == "PART":
        net.processJoinPart(response)
    # Process a NICK message.
    elif response[1] == "NICK":
        net.processNick(response)
    # Process mode messages.
    elif response[1] == "MODE":
        net.processMode(response)
    # Pong received, reset the number of pings missed.
    elif response[1] == "PONG":
        net.missedPings = 0
        net.pongReceived = time.time()
        debug.info("Received a PONG response from the server.")
        net.checkLag()

    cmds = __get_commands(raw, net)
    if cmds is None:
        cmds = []

    return cmds

def __get_commands(raw, net):
    '''Gets commands from scripts to be then set back to the IRC Server'''
    commands = []

    # Prepare the server message for processing.
    response = raw.split()
    source = response[0]
    cmd = response[1]

    toChannel = False
    if len(response) > 2:
        dest = response[2]
        if response[2][0] == "#":
            toChannel = True
    else:
        dest = ""

    # Process the source, if it is a user it will have nick and host.
    temp = source.split('!')
    srcNick = temp[0]

    if len(temp) == 2:
        srcHost = temp[1]
    else:
        srcHost = ""

    # Separate out the message from the rest.
    message = " ".join(response[3:])
    message = message.strip(':')

    # Store all the data in an way that is easy to pass along.
    ircMsg = ircMessage.ircMessage(net, srcNick, srcHost, dest, cmd, message)

    # Make sure that when we get a message from someone on IRC, we create
    # a Nick object in the master list for them and fill in what we can.
    # Some notices also come in from the server, don't process a message for
    # a nick unless it has a nick!host pair.
    if (cmd == "NOTICE" or cmd == "PRIVMSG") and (not ircMsg.srcHost == ""):
        nick = net.addNick(ircMsg.src)

        # Just to make sure the hostname is both filled in and matches.
        # Additionally, if the hostname changes, then flag the nick as
        # not authenticated.
        if nick.host == "":
            nick.host = ircMsg.srcHost
            nick.authed = False
            nick.clearPrivs()
        elif not (nick.host == ircMsg.srcHost):
            nick.host = ircMsg.srcHost
            nick.authed = False
            nick.clearPrivs()

        nick.getPrivs()

    # Reply to CTCP ping requests.
    if cmd == "PING" and (not srcNick == net.server):
        commands += net.ctcpPingReply(srcNick)

    # Send the message to be processed by the scripts.
    commands += scripts.rawMessages(net, raw)

    if ircMsg.command in ctcpGlobals.queries or ircMsg.command in ctcpGlobals.replies:
        commands += scripts.ctcpScripts(ircMsg)

    if toChannel:
        if cmd == "NOTICE":
            commands += scripts.chanNoticeScripts(ircMsg)
        elif cmd == "PRIVMSG":
            commands += scripts.channelScripts(ircMsg)
        elif cmd == "ACTION":
            commands += scripts.chanActionScripts(ircMsg)
    else:
        if cmd == "NOTICE":
            commands += scripts.privNoticeScripts(ircMsg)
        elif cmd == "PRIVMSG":
            commands += scripts.messageScripts(ircMsg)
        elif cmd == "ACTION":
            commands += scripts.privActionScripts(ircMsg)

    return commands

def main(argv):
    # Get the configuration from the file specified by the command line options.
    cfg = config.Config()
    __parse_args(argv, cfg)

    if not isfile(cfg.file):
        debug.error("Configuration file '" + cfg.file + "' could not be loaded!")
        return 1

    cfg.read()

    if cfg.init > 0:
        debug.warn("The 'init' command has been enabled.  See docs for more information.")

    result = 0    # Define a result value, so we can pass it back to the shell

    net = network.Network(cfg)

    while net.reconnect:
        # Establish a connection.
        if net.connect():
            net.auth()
            if net.ready():
                net.joinAll()
            else:
                debug.error("Failed to authenticate.")
                return 1
        else:
            debug.error("Failed to connect.")
            return 1

        lastTimer = time.time()

        while net.online() and net.ready():
            # Send any commands.
            net.send()
            # Is there data?
            data = net.checkMessages()
            if not data is None:
                # If anything needs to be sent to the server, we'll get a list
                # of commands from the response processor.
                cmds = __process_responses(net, data)
                if len(cmds) > 0:
                    net.sendCommands(cmds)

            # Basis for the loop to execute timers, we only want to execute a
            # timer if there at least one second between this loop and when
            # timers were last run.
            cmds = []

            if not net.quitting:
                currentTime = time.time()
                if (lastTimer + 1) < currentTime:
                    cmds += net.pingTimer(currentTime)
                    cmds += net.cleanTimer(currentTime)
                    cmds += scripts.timers(net, currentTime)
                    lastTimer = currentTime
                    if len(cmds) > 0:
                        net.sendCommands(cmds)

            # Make sure we don't amp up the CPU to max.
            global idleTime
            time.sleep(idleTime)

        if (not (net.online() and net.ready())) and net.reconnect:

            debug.message("Disconnected from the server.  Attempting to reconnect in " + str(int(net.config.delay)) + " seconds...")
            time.sleep(net.config.delay)

    return result
