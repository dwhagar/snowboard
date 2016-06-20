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
Stores information about a nick on the IRC network including hostname and
privleges associated with the nick in a global sense.

///Data///
.name
The nick of a paticular person on IRC.

.network
The name of the network the bot is on.

.users
Users object, provides access to the user database.

.host
The user@host of a particular nick on IRC.

.priv
A NickPriv object to store global privleges for a particular user.

.authed
Boolean value, has the user been authenticated yet?

///Constructor///
Nick(nick, users, [host], [priv])
Accepts three inputs, two are options.

nick
The nick of the person in question.

users
Users object which provides access to the user database.

host
The user@host of the nick on IRC, this is optional and defaults to an empty
string.

priv
A NickPriv object, this is optional and defaults to None.

///Methods///
.sendWHO()
Sends back a command for the Network object to then send to the server and
request the WHO information on a user, to derrive their hostname.

.getUID()
Retreives the UID from the dabase, only works if the system already knows
the nost of a particular nick, otherwise it will do nothing.  Return None if
no user is found.

.getPrivs()
Retreives the privileges of a user in the database.  If the UID is not yet
known, it will attempt to look it up based on hostname.  If no UID can be
found, the function returns None.

.auth(password)
Authenticates a nick against the user database.  Also assumes that the uid
is already retreived, if it exists when the message initially comes into
the server.  Thus if it doesn't see a uid present, it assume there is not
one.

Accepts one parameter:
password
The users password, unencrypted.
'''

from . import debug

class Nick:
    '''
    Stores information about a nick on the IRC network including hostname and
    privleges associated with the nick in a global sense.
    '''
    def __init__(self, nick, users, host = "", priv = None):
        self.name = nick
        self.host = host
        if priv == None:
            priv = NickPriv()
        self.priv = priv # NickPriv object
        self.users = users
        self.authed = False
        self.openWHO = False
        
    def sendWHO(self):
        '''Issues a WHO command to establish a hostname for a user.'''
        self.openWHO = True
        return ["WHO " + self.name]
    
    def getUID(self):
        '''Gets the user ID based on the host, only works if host is known'''
        if self.host == "":
            return None
        
        # Get the UID itself, if one exists.
        uid = self.users.matchHost(self.name + "!" + self.host)
        
        self.priv.uid = uid
        
        return uid
        
    def getPrivs(self):
        '''Gets access rights from the database for a user.'''
        
        # If we already know who this user is, that's fine, if not
        # then we need to find out.
        
        uid = self.getUID()
        
        if uid == None:
            return
        
        # If there is still no UID, the user does not exist.
        if not uid == None:
            data = self.users.userInformation(uid)
            self.priv.user = data[0]
            self.priv.hostmasks = data[1]
            self.priv.level = data[2]
            self.priv.approved = data[3]
            self.priv.denied = data[4]
        
        return uid
    
    def clearPrivs(self):
        '''Clears privleges from the object.'''
        self.priv.uid = None
        self.priv.user = None
        self.priv.level = 0
        self.priv.approved = []
        self.priv.denied = []
        self.priv.hostmasks = []
        
    def auth(self, password):
        '''Authenticates a user against the user database.'''
        commands = []
        
        if self.priv.uid == None:
            debug.message("No user information for " + self.name + " could be found.")
            commands.append("PRIVMSG " + self.name + " :You were not found in my database.")
            authorized = False
        else:
            debug.info("Attempting to authenticate " + self.name + ".")
            authorized = self.users.verifyUser(self.priv.uid, password)
        
        self.authed = authorized
        
        if authorized:
            debug.message("Authentication for " + self.name + " was successful.")
            commands.append("PRIVMSG " + self.name + " :Authentication successful.")
        else:
            debug.message("Authentication for " + self.name + " failed.")
            commands.append("PRIVMSG " + self.name + " :Authentication failed.")
                   
        return commands
            
'''
Stores global information about a particular nicks privleges.

///Data///
.uid
The unique user ID for this nick in the user database.

.user
The unique user name for this nick in the user database.

.level
Integer value of the users acccess level, globally.

.approved
A list of flags for which access is to be approved.

.denied
A list of flags for which access is to be denied.

.users
Users object to provide access to the user database.

///Constructor///
NickPriv([level], [uid], [user], [approved], [denied])
Accepts up to 4 inputs, all of which are optional.

level
defaults to 0

uid
defaults to None

user
defaults to None

approved
defaults to an empty list

denied
defaults to an empty list
'''
class NickPriv:
    '''Stores information about privileges of a nick, across all channels.'''
    def __init__(self):
        self.uid = None           # UID of a particular user, unique ID in DB
        self.user = None          # The Username of the Nick in the database
        self.hostmasks = []
        self.level = 0
        self.approved = []
        self.denied = []
        
    def checkApproved(self, flag):
        '''Checks to see if a user is approved for a flag.'''
        if flag.lower() in self.denied:
            valid = False
        elif flag.lower() in self.approved:
            valid = True
        elif "admin" in self.approved:
            valid = True
        else:
            valid = False
        
        return valid
    
    def checkDenied(self, flag):
        '''Checks to see if a user is denied for a flag.'''
        # Unlike the checkApproved function, this is designed so that a person
        # can only deny specific people from a function without adding a flag
        # to everyone else's approved list.
        if flag.lower() in self.denied:
            valid = True
        else:
            valid = False
        
        return valid