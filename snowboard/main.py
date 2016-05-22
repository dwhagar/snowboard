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

from . import config
from . import connection
from . import channel

def __parse_args(argv, cfg):
    """Parse command-line arguments.
    """
    argparser = argparse.ArgumentParser(
        prog="snowboard",
        description="IRC Bot Written in Python 3.",
        fromfile_prefix_chars="@")
    
    argparser.add_argument("--verbose", "-v", action="count", default=0,
        help="increase output verbosity")
    argparser.add_argument("--config", "-c", help="specify the configuration file to use.")
    
    cfg.options = argparser.parse_args(argv)
    
    cfg.verbosity = cfg.options.verbose
    cfg.file = cfg.options.config

def __get_message(conn):
    """Get a message from the server.
    """
    try:
        line = conn.read_until("\r\n".encode("utf-8"))
    except:
        return False
    
    line = line.decode("utf-8")
    line = line.strip(":")
    line = line.replace("\r","")
    line = line.replace("\n","")
    return line

def __send_message(conn, message):
    """Send message to server.
    """
    print(message)
    message = message + "\n"
    conn.write(message.encode("utf-8"))

def __get_server_name(conn):
    """Get the server name.
    """
    conn.read_until(b'\r\n')
    config.SERVERNAME = conn.read_until(b'\r\n').split()[0][1:].decode('utf-8')

def __authenticate(conn, nick, realname):
    """Log into IRC.
    """
    __send_message(conn, "NICK " + nick)
    __send_message(conn, "USER " + nick + " 0 * :" + realname)

def __join_channel(conn, chan):
    """Join a channel.
    """
    __send_message(conn, "JOIN " + chan)
    return channel.Channel(chan)

# Join the configured channels.
def __join_channels(conn, channel_names):
    """Join each channel in a list.
    """
    channels = []
    for chan in channel_names:
        __join_channel(conn, chan)
    return channels

# Go through the master channel list and add new channels and nicks.
def __update_master_channels(master, channels):
    pass

# Go through the master nick list and add new nicks and update memberships.
def __update_master_nicks(conn, master, channels):
    pass

# Pase channel names from a server and return a list of Names
def __parse_names(conn, raw, masterChannels, masterNicks):
    names = []
    response = raw.split()
    channel = response[4]
    response = response[5:]
    for name in response:
        oped = False
        voiced = False
        
        name = name.strip(':')
        if name[0] == '@' or name[1] == '@':
            oped = True
            name = name.replace('@','')
        if name[0] == '+' or name[1] == '+':
            voiced = True
            name = name.replace('+','')
            
        # TODO: Use two lists, one channels list and one nicks list.
        
        # SARIA: Had to add these to make it work
        channels = None
        nicks = None
        
        __update_master_channels(masterChannels, channels)
        __update_master_nicks(conn, masterNicks, nicks)

def __process_responses(conn, message, channels):
    response = message.split()
    
    # Process WHO responses to get hostnames.
    if response[1] == "352":
        for channel in channels:
            for name in channel.names:
                if name.nick.lower() == response[4].lower():
                    name.setHost(response[5])
    # Process NAMES responses to get all names for channels joined.
    elif response[1] == "353":
        names = __parse_names(conn, message, None, None)
        for channel in channels:
            if channel.name.lower() == response[4].lower():
                channel.updateNames(names)
    elif response[0] == "PING":
        __send_message(conn, "PONG " + response[1])

def __quit_command(message):
    print(message)
    commands = []
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

def __execute_commands(conn, commands):
    for command in commands:
        if command == "*QUIT*":
            ### TODO:
            ### Rather than sending the QUIT command then continuing to
            ### loop with what should be a dead connection, perhaps we
            ### should set a flag and then break out of the main loop?
            __send_message(conn, "QUIT :" + config.QUITMSG)
        else:
            __send_message(conn, commands)

def main(argv):
    cfg = config.Config()
    __parse_args(argv, cfg)
    cfg.read()

    result = 0    # Define a result value, so we can pass it back to the shell
    
    with connection.Connection(config.SERV, port=config.SERVPORT) as conn:
        __get_server_name(conn)
        __authenticate(conn, config.BOTNICK, config.REALNAME)
        
        # Complete connection.
        while True:
            message = __get_message(conn)
            ### TODO:
            ### If we're not going to let serverLine throw, then we'll have
            ### to handle errors here, somehow.
            response = message.split()
            if response[1] == "396":
                break
        
        channels = __join_channels(conn, config.BOTCHANS)
        
        while True:
            message = __get_message(conn)
            if message == False:
                break
            
            __process_responses(conn, message, channels)
            
            __execute_commands(conn, __get_commands(message))
    
    # Print the message about disconnection.
    print("Disconnected from the server.")
    
    return result
