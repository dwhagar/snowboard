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
Reads all configuration data for an instance of snowboard.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''
import configparser

from . import channel
from . import server

# Global verbosity.
verbosity = 0

class Config:
    def __init__(self, configFile = "snowboard.ini"):
        # Set Defaults.
        self.versionNumber = 0
        self.revisionNUmber = 1
        self.buildNumber = 1
        self.releaseStage = "alpha"
        self.version = str(self.versionNumber) + "." + str(self.revisionNUmber) + "." + str(self.buildNumber) + "-" + self.releaseStage
        self.botnick = "Snowboard"
        self.realname = "Project Snowboard"
        self.network = "Network"
        self.servers = []
        self.channels = []
        self.quitmsg = "Project Snowboard https://github.com/dwhagar/snowboard"
        self.options = None
        self.sslVerify = True
        self.retries = 3
        self.delay = 1
        self.init = 0
        self.pingInterval = 300
        self.checkInterval = 300
        self.maxLag = 90
        self.nickPass = None
        self.logLevel = 0

        # Read configuration.
        self.file = configFile

    def read(self):
        '''Reads configuration data from the config file.'''
        # Get everything out of the configuration file.
        config = configparser.ConfigParser()
        config.read(self.file)

        # Load all sections to parse
        # Network, server, and channel information is required
        # Parse Servers into a List, grab the network name.
        self.network = config['Network']['name']
        servers = config['Network']['servers']
        servers = servers.replace(' ','')
        combined = servers.split(',')
        for entry in combined:
            line = entry.split(':')
            if line[1][0] == '+':
                ssl = True
                line[1] = line[1][1:]
            else:
                ssl = False

            newServer = server.Server(line[0], int(line[1]), ssl)
            self.servers.append(newServer)

        # Parse Channels into a List
        channels = config['Network']['channels']
        channels = channels.replace(' ','')
        self.channels = channels.split(',')

        # These sections all have reasonable defaults, so it checks to see if
        # the keys are there, if they are not defaults are used.
        for section in config.sections():
            keys = config[section]
            if section == "Identity":
                if "botnick" in keys:
                    self.botnick = config[section]["botnick"]
                if "realname" in keys:
                    self.realname = config[section]["realname"]
                if "nickpass" in keys:
                    self.nickPass = config[section]["nickpass"]
            elif section == "Messages":
                if "quit" in keys:
                    self.quitmsg = config[section]["quit"]
            elif section == "Network":
                if "sslverify" in keys:
                    verify = int(config[section]["sslverify"])
                    if verify == 0:
                        self.sslVerify = False
                    else:
                        self.sslVerify = True
                if "retries" in keys:
                    self.retries = int(config[section]["retries"])
                if "delay" in keys:
                    self.delay = float(config[section]["delay"])
                if "pingtimer" in keys:
                    self.pingInterval = int(config[section]["pingtimer"])
                if "cleantimer" in keys:
                    self.cleanInterval = int(config[section]["cleantimer"])
                if "maxlag" in keys:
                    self.maxLag = int(config[section]["maxlag"])