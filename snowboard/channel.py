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
what that person's privliges are within the channel.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from .users import Users
from .channelDB import ChannelDB

class Channel:
    '''A class to store all information the bot knows about a channel.'''
    def __init__(self, name, network, members = []):
        self.botnick = None
        self.db = ChannelDB(network, name)
        self.defaultModes = ""
        self.defaultTopic = ""
        self.desc = ""
        self.flags = []
        self.joined = False
        self.name = name
        self.members = members  # A list of lists, storing Nick and ChanPriv
        self.modes = ""
        self.network = network
        self.topic = ""
        self.opped = False
        self.voiced = False

        self.loadData()

    def addFlag(self, flag):
        '''Adds a flag to the channel and saves it.'''
        if not (flag.lower() in map(str.lower, self.flags)):
            if not flag == "":
                self.flags.append(flag)

        self.saveData()

    def addNick(self, nick, priv):
        '''Add a nick to the list.'''
        existing = self.findNick(nick)
        if existing is None:
            member = [nick, priv]
            self.members.append(member)

    def checkFlag(self, flag):
        '''Checks to see if a flag exists.'''
        result = False

        if flag.lower() in map(str.lower, self.flags):
            result = True

        return result

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
                result = member

        return result

    def join(self):
        '''Join a channel.'''
        if not self.joined:
            return ["JOIN " + self.name]

    def loadData(self):
        '''Loads data into the object from the database.'''
        self.flags, self.defaultTopic, self.desc, self.defaultModes = self.db.loadData()

    def part(self):
        '''Leaves a channel.'''
        if self.joined:
            return ["PART " + self.name]

    def removeFlag(self, flag):
        '''Removes a flag from the channel and saves the DB.'''
        if flag.lower() in map(str.lower, self.flags):
            self.flags.remove(flag.lower())

        self.db.saveFlags(self.flags)

    def removeNick(self, nick):
        '''Remove a nick from the list.'''
        existing = self.findNick(nick)
        if not existing is None:
            self.members.remove(existing)

    def saveData(self):
        '''Saves channel data to the database.'''
        self.db.saveData(self.flags, self.defaultTopic, self.desc, self.defaultModes)

    def updateSelf(self):
        '''Update the bots knowledge of its own privileges.'''
        me = self.findNick(self.botnick)

        self.opped = me[1].op
        self.voiced = me[1].voice

        self.loadData()
