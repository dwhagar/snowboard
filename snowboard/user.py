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