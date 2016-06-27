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
Stores user privleges for a specific channel.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from .userFlags import UserFlags

class UserChannel:
    '''A place to store complete privleges for a user on a channel.'''
    def __init__(self):
        self.name = None
        self.level = 0
        self.flags = UserFlags()

    def checkApproved(self, flag):
        '''Checks with the users flags to see if they are approved.'''
        return self.flags.checkApproved(flag, self.level)

    def checkDenied(self, flag):
        '''Checks with the users flags to see if they are denied.'''
        return self.flags.checkDenied(flag)

    def toData(self, data):
        '''Decode a string into the object properties.'''
        properties = data.split('/')

        self.name = properties[0].lower()
        self.level = int(properties[1])
        self.flags.toData(data[2].lower())

    def toString(self):
        '''Encodes the object properties to a string.'''
        levelString = str(self.level)
        flagString = self.flags.toString()

        encoded = self.name + "/" + levelString + "/" + flagString

        return encoded