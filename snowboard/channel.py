# A class to store all information the bot knows about a particular channel.
class Channel:
    def __init__(self, name, members = []):
        self.name = name
        self.joined = False
        self.members = members # A list of lists, storing Nick and ChanPriv objects

# Stores information about privileges on a channel. 
class ChannelPriv:
    def __init__(self, isop = False, isvoice = False, level = 0):
        self.op = isop
        self.voice = isvoice
        self.level = level

# Stpres information about privileges of a nick, across all channels.
class NickPriv:
    def __init__(self, level = 0, admin = False):
        self.admin = admin
        self.level = level