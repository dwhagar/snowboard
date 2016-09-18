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
Reads all configuration data for an instance of snowboard and stores that
information to be used by the Network object.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import configparser

from . import server

# Global verbosity.
verbosity = 0

class Config:
    '''
    Manages configuration data for snowboard.

    Public Data Members:
        versionNumber:
            Integer object, stores the current major version number.
        revisionNumber:
            Integer object, stores the current minor version number.
        buildNumber:
            Integer object, stores the current build version number.
        releaseStage:
            String object, stores the release stage the bot is in with this
            version (alpha, beta, public-beta, stable, dev, etc.).
        version:
            String object, describes in one line the version, build, and
            release stage of this version of Snowboard.
        botnick:
            The bots default / intended nick name on IRC.
        realname:
            The bots configured "Real Name" used during IRC login.
        network:
            The name given to this IRC network.
        servers:
            A list of Server objects containing connection information
            for each configured IRC Server to be used.
        channels:
            A list of string objects containing each channel the bot is to
            join on connect.
        quitmsg:
            A string object, the bots "reason" for quitting when the bot is
            told to quit IRC.
        options:
            A Namespace object passed from the argument parser during startup,
            stores all the commandline options sent to the bot when it was
            executed.
        sslVerify:
            A boolean object telling the bot if it should verify SSL
            connections via certificates or ignore certificate validity.
        retries:
            An integer object telling how many retries per server should be
            done before moving onto the next server in the list.
        delay:
            An integer object telling how many seconds the bot should pause
            between connection attempts.
        init:
            An integer object telling if the bot should accept the "init"
            command.  Note, this command is used to initialize the user
            database, and must be enabled with the -i / -init command line
            argument.  A warning will be generated if this flag is set to 1.
            See the userCommands library for details.
        pingInterval:
            An integer object telling the bot how long it should wait on an
            idle connection before initiating a server ping.
        checkInterval:
            An integer object telling the bot how long between it cleans its
            internal Nick list for nicks which are no longer online.
        maxLag:
            An integer object telling the bot how high the lag time between
            itself and the server can be (in seconds) before the bot will
            disconnect and attempt to reconnect.
        nickPass:
            A string object telling the bot a password to use for
            authentication with NickServ should the bots nick be registered.
        logLevel:
            An integer object containing the current log level.  This works
            like the verbosity, between 0 and 3.  0 For no logging and 3 for
            maximum logging.
        file:
            The name of the configuration file to use.
    '''

    # TODO: Implement a save function to allow bot attributes to be changed and reloaded while the bot is running.

    def __init__(self, configFile = "snowboard.ini"):
        '''
        Initializes the Config object.  Everything that can have a default if
        not configured via the file, should have a default configured here.

        :param configFile:
            A string object for the file name of the configuration to load.
        '''
        self.versionNumber = 0
        self.revisionNUmber = 1
        self.buildNumber = 5
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
        '''
        Reads data from a configuration file.

        A configuration file is required to have a minimum of the following:
            A list of channels to join in the "Network" section, under the
            "channels" key.
            A list of servers to connect to in the "Network" section, under
            the "server" key in the format of "server:[+]port".
            A network name in the "Network" section undder the "name" key.

        Example of minimum requirements:
        [Network]
        name = Network
        servers = oneserver.irc.com:+6696, twoserver.irc.com:6667
        channels = #Something, #SomethingElse

        In the above case, the server name has a '+' in front of the port
        number if that server supports SSL or not.  Thus oneserver.irc.com
        uses port 6696 and that port should use SSL for its connection.
        '''
        # Get everything out of the configuration file.
        config = configparser.ConfigParser()

        # TODO: Error handling if the configuration file is missing, should display a useful error to the log and console.
        config.read(self.file)

        # TODO: If one of the required configurations sections is missing, should quit after displaying a useful error.
        # Load all sections to parse
        # Network, server, and channel information is required
        # Parse Servers into a List, grab the network name.

        # The network key is specifically important!  This will define the
        # file name and other options for settings and users within the
        # database.

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
                    self.checkInterval = int(config[section]["cleantimer"])
                if "maxlag" in keys:
                    self.maxLag = int(config[section]["maxlag"])