# Bot class definition.
#
# This defines an object which is used to handle a single instance of the bot
# so that all of an instance of the bot can be kept in one concise place.

import socket
import configparser

from channels import *


# Class to store and load configuration data.
class Config:
    # Constructor
    def __init__(self, configFile):
        # Set Defaults.
        self.botnick = "Snowboard"
        self.realname = "Project Snowboard"
        self.servers = []
        self.channels = []
        self.quitmsg = "Project Snowboard https://github.com/dwhagar/snowboard"
        
        # Read configuration.
        self.config = configFile
        self.readConfig()
    
    # Read the config file into memory.
    def readConfig(self):
        # Get everything out of the configuration file.
        config = configparser.ConfigParser()
        config.read(self.config)
        
        # Load Settings
        self.botnick = config['Identity']['botnick']
        self.readlname = config['Identity']['realname']
        self.quitmsg = config['Messages']['quit']
        
        # Parse Servers into a List
        servers = config['Network']['servers']
        servers = servers.replace(' ','')
        combined = servers.split(',')
        for entry in combined:
            line = entry.split(':')
            newServer = Server(line[0], line[1])
            self.servers.append(newServer)
        
        # Parse Channels into a List
        channels = config['Network']['channels']
        channels = channels.replace(' ','')
        channelList = channels.split(',')
        for channel in channelList:
            newChannel = Channel(channel)
            self.channels.append(newChannel)
                

# Defines a server connection configuration, does not handle the actual
# connection, but provides settings such as name, port, and ssl options.
class Server:
    # Constructor
    def __init__(self, host, port = 6667):
        self.host = host
        self.port = port