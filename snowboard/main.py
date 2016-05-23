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

import argparse
import time

from . import config
from . import connection
from . import channel
from . import network

def __parse_args(argv, cfg):
    """Parse command-line arguments.
    """
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
    
    cfg.options = argparser.parse_args(argv)
    config.verbosity = cfg.options.verbose
    cfg.file = cfg.options.config

def __process_responses(net, raw):
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
    # Process JOIN responses to confirm a channel has been joined.
    elif response[1] == "JOIN" or response[1] == "PART":
        net.processJoinPart(response)
    elif response[1] == "PRIVMSG":
        cmds = __get_commands(raw)
    
    return cmds

def __quit_command(message):
    commands = []
    print(message)
    if message == "quit now":
        commands.append("*QUIT*")
    return commands

def __get_commands(raw):
    commands = []
    response = raw.split()
    message = " ".join(response[3:])
    message = message.strip(':')
    
    if response[1] == "PRIVMSG":
        commands = __quit_command(message)
        
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
            return 1
    else:
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
