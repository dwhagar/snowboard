# Bot class definition.
#
# This defines an object which is used to handle a single instance of the bot
# so that all of an instance of the bot can be kept in one concise place.

from channels import *

class Bot:
    # Constructor
    def __init__(self, configFile):
        # Set Defaults.
        self.__botnick = "Snowboard"
        self.__realname = "Project Snowboard"
        self.__servers = []
        
        # Read configuration.
        self.__config = configFile
        self.readConfig()
    
    # Read the config file into memory.
    def readConfig(self):
        # Get everything out of the configuration file.
        cfg = open(self.__config)
        data = cfg.readlines()
        cfg.close()
        
        # Parse the configuration data.
        data = data.split('\n')
        for line in data:
            # Prepare each configuration line.
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            option = line.split()
            
            # Derrive the directive and the setting.
            directive = option[0].lower()
            setting = option[1:]
            
            # Go through for known directives, ignore unknown directives.
            # botnick directive
            if directive == "botnick":
                setting = setting.replace(' ', '_') # Spaces not allowed
                self.__botnick == setting
            # realname directive
            elif directive == "realname":
                self.__realname
            # server directive
            elif direct == "server":
                # Server directive will be a comma seperated list
                # host:port, host:port, etc...
                setting = setting.replace(' ', '') # No spaces
                servers = setting.split(',')
                
                # Seperate the host from port.
                for server in servers:
                    combined = server.split(':')
                    host = combined[0]
                    # TODO: This is where we will add checks for if the port
                    #       is an SSL port.
                    port = int(combined[1])
                    # TODO: Make sure if user specifies no port, default
                    #       Applies.
                    
                    # Add the server to the list.
                    newServer = Server(host, port)
                    self.__servers.append(newServer)

# Defines a server connection configuration, does not handle the actual
# connection, but provides settings such as name, port, and ssl options.
class Server:
    # Constructor
    def __init__(self, host, port = 6667):
        self.__host = host
        self.__port = port
    
    # Read only object, sets when initialized.
    def host():
        return self.__host
    
    def port():
        return self.__port
    
    # TODO: Add options for SSL connection