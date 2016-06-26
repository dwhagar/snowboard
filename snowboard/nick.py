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
from .user import User

class Nick:
    '''
    Stores information about a nick on the IRC network including hostname and
    privleges associated with the nick in a global sense.
    '''
    def __init__(self, nick, users):
        self.name = nick
        self.host = None
        self.user = User()
        self.users = users
        self.authed = False
        self.openWHO = False

    def auth(self, password):
        '''Authenticates a user against the user database.'''
        commands = []

        # See if we can get the privs on a user, just in case they were added
        # after we last tried.
        if self.user.uid == None:
            uid = self.getUID()

        # Now if we still don't have the privs or the UID on file then, there
        # is an issue.
        if self.user.uid == None:
            debug.message("No user information for " + self.name + " could be found.")
            commands.append("PRIVMSG " + self.name + " :You were not found in my database.")
            authorized = False
        else:
            self.getPrivs()
            debug.info("Attempting to authenticate " + self.name + ".")
            authorized = self.user.verify(password)

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
        self.user = User()

    def getUID(self):
        '''Gets the user ID based on the host, only works if host is known'''
        if self.host == "":
            return None

        # Get the UID itself, if one exists.
        self.user.uid = self.users.matchHost(self.name + "!" + self.host)

        return self.user.uid

    def getPrivs(self):
        '''Gets access rights from the database for a user.'''

        if self.user.uid == None:
            thisUser = None
        else:
            thisUser = self.users.userInformation(self.user.uid)
            self.user = thisUser

        return thisUser

    def sendWHO(self):
        '''Issues a WHO command to establish a hostname for a user.'''
        self.openWHO = True
        return ["WHO " + self.name]