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
Stores the complete user privleges for a single user.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from . import passwordTools
from .userFlags import UserFlags
from .userChannel import UserChannel

class User:
    '''A place to store the complete privleges of a single user.'''
    def __init__(self):
        self.uid = None
        self.user = None
        self.pwHash = None
        self.hostmasks = []
        self.level = 0
        self.flags = UserFlags()
        self.channels = []

    def checkApproved(self, flag):
        '''Checks with the users flags to see if they are approved.'''
        return self.flags.checkApproved(flag, self.level)

    def checkDenied(self, flag):
        '''Checks with the users flags to see if they are denied.'''
        return self.flags.checkDenied(self, flag)

    def findChannel(self, channel):
        '''Finds a channel, if one exists, in the list of privleges.'''
        result = None

        if len(channels) > 0:
            index = 0

            for chan in channels:
                if chan.name.lower() == channel.lower():
                    result = channels[index]
                    break
                index += 1

        return result

    def loadChannels(self, data):
        '''Adds channels to the object from the database line.'''
        self.channels = []
        dataList = data.split('//')

        if len(dataList) > 0:
            if not (dataList[0] == ""):
                for item in dataList:
                    newChan = UserChannel()
                    newChan.toData(item)
                    self.channels.append(newChan)

    def loadHostmasks(self, data):
        '''Loads hostmasks into the object from the database line.'''
        self.hostmasks = data.split(',')

    def saveChannels(self):
        '''Converts the channel list into a single string for saving to db.'''
        if len(self.channels) > 0:
            dataList = []

            for chan in self.channels:
                dataList.append(chan.toString())

            line = "//".join(dataList)
        else:
            line = ""

        return line

    def saveHostmasks(self):
        '''Converts the hostmask list into a string to be saved to the db.'''
        if len(self.hostmasks) > 0:
            line = ",".join(self.hostmasks)
        else:
            line = ""

        return line

    def verify(self, password):
        '''Verifies a password.'''
        result = False

        if passwordTools.passwordHash(password) == self.pwHash:
            result = True

        return result