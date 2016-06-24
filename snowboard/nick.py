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

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from . import debug
from . import userLevels

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
    
    def auth(self, password):
        '''Authenticates a user against the user database.'''
        commands = []
        
        # See if we can get the privs on a user, just in case they were added
        # after we last tried.
        if self.priv.uid == None:
            self.getPrivs()
        
        # Now if we still don't have the privs or the UID on file then, there
        # is an issue.
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
       
    def clearPrivs(self):
        '''Clears privleges from the object.'''
        self.priv.uid = None
        self.priv.user = None
        self.priv.level = 0
        self.priv.approved = []
        self.priv.denied = []
        self.priv.hostmasks = []
    
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
    
    def sendWHO(self):
        '''Issues a WHO command to establish a hostname for a user.'''
        self.openWHO = True
        return ["WHO " + self.name]
            
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
        # Gant flags based on user level, but explicitly do not add them
        # to the database.
        approved = self.approved[:] + userLevels.grantFlags(self.level)
        
        if flag.lower() in self.denied:
            valid = False
        elif flag.lower() in approved:
            valid = True
        elif "admin" in approved:
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