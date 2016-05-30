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

///Properties///
.name
The name of the channel, as it would be read by the IRC server.

.network
The nam eof the network the channel is on.

.joined
Boolean value of if the channel has been joined or not.

.members
A list of members, each member in the format of [Nick, ChanPriv].

.users
A Users object, acts as the interface to the channels user database.

///Constructor///
Users(name, network, [members])
Initializes the object, the constructor can take up to 3 inputs, but requires
a name and a network name at the very least.

name:
The name of the channel itself.

network:
The name of the network the channel is on.

members:
A list of Nick objects and ChanPriv objects in the format of
[[Nick, ChanPriv], [Nick, ChanPriv], ...]

///Methods///
.join():
Instructs the bot to join the channel.

.part():
Instructs the bot to leave the channel.

.findNick(nick)
Finds a particular nick, if it exists, within the channel's member list.
This will return None if no nick is found.

Takes one input, a Nick object.

.addNick(nick, priv)
Adds a nick to the members list, if a member is found with that nick, it
will return the Nick object.

Takes two inputs, a Nick object and a ChanPriv objects.

.removeNick(nick)
Removes a nick from the member list if that nick exists.

Takes one input, a Nick object.

.getAllPrivs()
Accesses the database and get the channel privleges for all members of
that channel.
'''

from . import users

class Channel:
    '''A class to store all information the bot knows about a channel.'''
    def __init__(self, name, network, members = []):
        self.name = name
        self.network = network
        self.joined = False
        self.members = members # A list of lists, storing Nick and ChanPriv
        self.users = user.Users(self.network, self.name[1:])
    
    def join(self):
        '''Join a channel.'''
        if not self.joined:
            return ["JOIN " + self.name] 
     
    def part(self):
        '''Leaves a channel.'''
        if self.joined:
            return ["PART " + self.name]
    
    def findNick(self, nick):
        '''Find a nick in the list, if one exists.'''
        result = None
        
        # Find the proper entry in members.
        for member in self.members:
            if member[0].name.lower() == nick.name.lower():
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
                priv.user = data[0]
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
    def __init__(self, isop = False, isvoice = False, level = 0, approved = [], denied = []):
        self.op = isop
        self.voice = isvoice
        self.level = level
        self.approved = approved
        self.denied = denied