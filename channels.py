# Channels / Nicks Class Definitions

# Define data structures to store information about a channel and the
# people in it.

class Channel:
	# Constructor
	def __init__(self, name=None):
		self.__topic = ""
		self.__names = []
		
		if name == None:
			self.__name = ""
		else:
			self.__name = name
	
	# Add names to the channel.
	def addName(self, name):
		self.__names.append(Nick(name))
	
	# Change a name within the list, by index
	def updateName(self, name, idx):
		self.__names[idx] = name
	
	# Replace the entire channel list with a new one.
	def updateNames(self, names):
		self.__names = names
	
	# Find a name in the list of names, and return its index.
	def findName(self, name):
		if name in self.__names:
			result = self.__names(name)
		else:
			result = -1
		
		return result
	
	# Remove an item in the names list, by name.
	def removeName(self, name):
		self.__names.remove(name)
	
	# Retrieve the list of names in the channel.
	def names(self):
		return self.__names
	
	# Set the channels name
	def setName(self, name):
		self.__name = name
	
	# Retrieve the name of the channel.
	def name(self):
		return self.__name
	
	# Returns the number of names in the channel.
	def count(self):
		return len(self.__names)
		
class Nick:	
	# Constructor
	def __init__(self, nick=None):
		self.__op = False
		self.__voice = False
		self.__host = ""

		if nick == None:
			self.__nick = ""
		else:
			self.__nick = nick
	
	# Set the operator status of a nick on a channel.
	def setOp(self, op):
		self.__op = op
	
	# Retrieve the operator status of a nick on a channel.
	def op(self):
		return self.__op
	
	# Set the voice status of a nick on a channel.
	def setVoice(self, voice):
		self.__voice = voice
	
	# Retrieve the operator status of a nick on a channel.
	def voice(self):
		return self.__op
		
	# Set the host for this nick.
	def setHost(self, host):
		self.__host = host
	
	# Retrieve the host for a nick on a channel.
	def host(self):
		return self.__host