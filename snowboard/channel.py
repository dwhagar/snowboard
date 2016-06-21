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
These two classes server to store information on a person in a channel and
what that person's privleges are within the channel.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from . import users

class Channel:
    '''A class to store all information the bot knows about a channel.'''
    def __init__(self, name, network, members = []):
        self.name = name
        self.network = network
        self.joined = False
        self.members = members # A list of lists, storing Nick and ChanPriv
        self.users = users.Users(self.network, self.name[1:])
        self.botnick = None
        self.opped = False
        self.voiced = False
    
    def join(self):
        '''Join a channel.'''
        if not self.joined:
            return ["JOIN " + self.name] 
     
    def part(self):
        '''Leaves a channel.'''
        if self.joined:
            return ["PART " + self.name]
    
    def findNick(self, nck):
        '''Find a nick in the list, if one exists.'''
        result = None
        
        # The function should be able to find the information needed by
        # just a string or a Nick object.
        if type(nck) == str:
            nckStr = nck
        else:
            nckStr = nck.name
        
        # Find the proper entry in members.
        for member in self.members:
            if member[0].name.lower() == nckStr.lower():
                self.__getPrivs(member[0], member[1])
                result = member
        
        return result

    def addNick(self, nick, priv):
        '''Add a nick to the list.'''
        existing = self.findNick(nick)
        if existing == None:
            self.__getPrivs(nick, priv)
            member = [nick, priv]
            self.members.append(member)

    def removeNick(self, nick):
        '''Remove a nick from the list.'''
        existing = self.findNick(nick)
        if not existing == None:
            self.members.remove(existing)
    
    def __getPrivs(self, nick, priv):
        '''Add access rights to a particular Nick and ChanPriv pair'''
        uid = nick.priv.uid
        result = uid
        
        if not uid == None:
            data = self.users.userInformation(uid)
            if not data == None:
                priv.level = data[1]
                priv.approved = data[2]
                priv.denied = data[3]
            else:
                result = None
        
        return result
        
    def getAllPrivs(self):
        '''Load all privleges for all members.'''
        for member in members:
            self.__getPrivs(member[0], member[1])
            
    def updateSelf(self):
        '''Update the bots knowledge of its own privleges.'''
        me = self.findNick(self.botnick)
        
        self.opped = me[1].op
        self.voiced = me[1].voice

'''
An object to store user privleges for a particular channel.

///Data///
.op
Boolean value if the user has ops in the channel or not.

.voice
Boolean value if the user is voiced in the channel or not.

.level
Integer value representing the users current access level for this channel
with the bot.

.approved
A list of flags which determine specific things a user has access to.

.denied
A list of flags which determine specific things a user has no access to.
'''
class ChannelPriv:
    '''Stores users privleges associated with a channel.'''
    def __init__(self, isop = False, isvoice = False):
        self.op = isop
        self.voice = isvoice
        self.level = 0
        self.approved = []
        self.denied = []
        
    def checkFlag(self, flag):
        '''Checks to see if a flag is valid.'''
        if flag.lower() in self.denied:
            valid = False
        elif flag.lower() in self.approved:
            valid = True
        elif "admin" in self.approved:
            valid = True
        else:
            valid = False
        
        return valid   