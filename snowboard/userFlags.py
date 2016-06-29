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
A place to store a users flags.
'''

from . import userLevels

class UserFlags:
    def __init__(self):
        self.approved = []
        self.denied = []

    def checkApproved(self, flag, level = 0):
        '''Checks to see if a user is approved for a flag.'''
        # Gant flags based on user level, but explicitly do not add them
        # to the database.
        approved = self.approved[:] + userLevels.grantFlags(level)

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

    def cleanFlags(self):
        '''Cleans the list of flags of abnormalities.'''
        # Clean any blank strings from the lists, and there is no white space.
        for flag in self.approved:
            flag = flag.strip()
            if flag == "":
                self.approved.remove(flag)
        for flag in self.denied:
            flag = flag.strip()
            if flag == "":
                self.denied.remove(flag)

        # Make sure there are no duplicates.
        self.approved = list(set(self.approved))
        self.denied = list(set(self.denied))

    def toData(self, flags):
        '''Converts a string of flags into lists for the object.'''
        flagList = flags.split(':')
        if len(flagList) == 1:
            self.approved = flagList[0].split(',')
            self.denied = []
        elif len(flagList) == 2:
            self.approved = flagList[0].split(',')
            self.denied = flagList[1].split(',')
        else:
            self.approved = []
            self.approved = []

        self.cleanFlags()


    def toString(self):
        '''Converts the userflags to a single string.'''
        self.cleanFlags()

        approvedString = ",".join(self.approved).lower().replace(':','')
        deniedString = ",".join(self.denied).lower().replace(':','')

        result = approvedString + ":" + deniedString

        return result