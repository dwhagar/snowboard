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
'''

import argparse
import time

from . import config
from . import connection
from . import channel
from . import network

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
    config.verbosity = cfg.options.verbose
    config.init = cfg.options.init
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
    elif response[1:2] == ":Closing Link:":
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
        # TODO:  Process the MODE message from the server.
    # Process a PRIVMSG message.
    elif response[1] == "PRIVMSG":
        cmds = __get_commands(raw, net)
    
    return cmds

def __check_init():
    '''Checks for if the init command has been used, to define admin'''
    

def __get_commands(raw, net):
    '''Gets commands from scripts to be then set back to the IRC Server'''
    response = raw.split()
    source = response[0][1:]
    temp = source.split('!')
    srcNick = temp[0]
    srcHost = temp[1]
    message = " ".join(response[3:])
    message = message.strip(':')
    messageList = message.split()
    toChannel = False
    
    if response[2][0] == "#":
        toChannel = True
    
    if not toChannel:
        # Going to take this command out, eventually, when we don't need it
        # for testing and clean quits anymore.
        if message.lower() == "quit now":
            net.quit()
        
        # Process the init command, if that command is enabled.
        if messageList[0] == "init" and config.init > 0:
            net.addUser(srcNick, messageList[2], messageList[1], 255, ["admin"], [])
        
    return commands

def main(argv):
    # Get the configuration from the file specified by the command line options.
    cfg = config.Config()
    __parse_args(argv, cfg)    
    cfg.read()
    
    result = 0    # Define a result value, so we can pass it back to the shell
    
    net = network.Network(cfg)
    
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
    
    # Loop until we break the loop.
    while net.online():
        # Is there data?
        data = net.checkMessages()
        if data == None:
            time.sleep(0)
            continue
        else:
            # If anything needs to be sent to the server, we'll get a list
            # of commands from the response processor.
            cmds = __process_responses(net, data)
            if len(cmds) > 0:
                net.sendCommands(cmds)
        
        # Make sure we don't amp up the CPU to max.
        time.sleep(0)
    
    return result
