# Channels / Nicks Class Definitions

# Define data structures which allow the bot to keep track of channels and
# nicks that it sees.

# TODO:  Class documentation

# A class to store all information the bot knows about a particular channel.
class Channel:
    # Contructor
    def __init__(self, name = None):
        if name == None:
            self.__name = ""
        else:
            self.__name = name
        self.__nicks = []
    
    # Set and get the channels name.
    def setName(self, name):
        self.__name = name
    
    def name(self):
        return self.__name
    
    # Functions to deal with the list of nicks.
    def addNick(self, nick):
        if not (nick in self.__nicks):
            self.__nicks.append(nick)
        
    def removeNick(self, nick):
        self.__nicks.remove(nick)
    
    # Find the index of a nick in a list.
    def findNick(self, search):
        result = -1
        
        for nick in self.__nicks:
            if nick.lower() == search.lower():
                result = self.__nicks.index(nick)
        
        return result
    
    # Update a single nick out of the list, by index.
    def updateNick(self, index, nick):
        self.__nicks[index] = nick
    
    # Update the entire list of nicks at once.
    def updateNicks(self, nicks):
        self.__nicks = nicks
    
    # Grab a single nick out of the list.
    def nick(self, index):
        return self.__nicks[index]
    
    # Grab the entire list.
    def nicks(self):
        return self.__nicks
    
        
# A class to store all information the bot knows about a particular nick.		
class Nick:	
    # Constructor
    def __init__(self, name = None):
        if name == None:
            self.__nick = ""
        else:
            self.__nick = name
        
        self.__channels = []
        self.__isadmin = False
        self.__host = ""
    
    # Set various attributes
    def setNick(self, name):
        if type(name) == str:
            self.__nick = name
    
    def setHost(self, host):
        if type(host) == str:
            self.__host = host
    
    def setAdmin(self, admin):
        if type(admin) == bool:
            self.__isadmin = admin
    
    # Get the basic attributes
    def nick(self):
        return self.__nick
    
    def host(self):
        return self.__host
    
    def admin(self):
        return self.__isadmin
    
    # Deal with the channel list, add, remove, find, etc...
    def addMember(self, channel):
        if self.findMember(channel.name()) == -1:
            self.__channels.append(channel)
    
    def removeMember(self, channel):
        self.__channels.remove(channel)
    
    # Returns the index of a member, channel is a string.
    def findMember(self, channel):
        result = -1
        
        for member in self.__channels:
            if member.name().lower() == channel.lower():
                result = self.__channels.index(member)
        
        return result
    
    # Update a single member from the list, by index.
    def updateMember(self, index, channel):
        self.__channels[index] = channel
    
    # This allows an entire list of channels to be updated at one time.
    def updateMembers(self, channels):
        self.__channels = channels
    
    # Gets a single member channel from the list.
    def member(self, index):
        return self.__channels[index]
    
    # Gets the entire list of member channels.
    def members(self):
        return self.__channels


# A class to store what channels a nick is a member of.
class Member:
    # Constructor
    def __init__(self, chanName = None):
        # What channel is it.
        if chanName == None:
            self.__name = ""
        else:
            self.__name = chanName
        
        # Privleges on channel.
        self.__isop = False
        self.__isvoice = False
    
    # Set various attributes.
    def setName(self, name):
        if type(name) == str:
            self.__name = name
    
    def setOp(self, opped):
        if type(opped) == bool:
            self.__isop = opped
    
    def setVoice(self, voiced):
        if type(voiced) == bool:
            self.__isvoice = voiced
    
    # Get various attributes.
    def name(self):
        return self.__name
    
    def isop(self):
        return self.__isop
    
    def isvoice(self):
        return self.__isvoice