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
privleges associated with the nick in a global sense.  The object also
contains the fungtion to request a hostname for a particular nick.
'''
class Nick:
    def __init__(self, nick, host = "", priv = None):
        self.name = nick
        self.host = host
        self.priv = priv # NickPriv object
        
    def getHost(self):
        return ["WHO " + self.name]

# Stpres information about privileges of a nick, across all channels.
class NickPriv:
    def __init__(self, level = 0, uid = None, admin = False):
        self.uid = uid          # UID of a particular user, unique ID in DB
        self.admin = admin
        self.level = level