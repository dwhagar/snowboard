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

# Bot class definition.
#
# This defines an object which is used to handle a single instance of the bot
# so that all of an instance of the bot can be kept in one concise place.

import configparser

from .channel import Channel
from .server import Server

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
