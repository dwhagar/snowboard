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

# A class to store all information the bot knows about a particular channel.
class Channel:
    def __init__(self, name, members = []):
        self.name = name
        self.joined = False
        self.members = members # A list of lists, storing Nick and ChanPriv
    
    # Join a channel.
    def join(self):
        if not self.joined:
            return ["JOIN " + self.name] 
     
    # Part from a channel.       
    def part(self):
        if self.joined:
            return ["PART " + self.name]
    
    # Find a nick in the list, if one exists.
    def __findNick(self, nick):
        result = None
        
        # Find the proper entry in members.
        for member in self.members:
            if member[0].name.lower() == nick.name.lower():
                result = member
        
        return result
    
    # Add a nick to the list.        
    def addNick(self, nick, priv):
        existing = self.__findNick(nick)
        if existing == None:
            member = [nick, priv]
            self.members.append(member)
        else:
            member[0] = nick
            member[1] = priv

# Stores information about privileges on a channel. 
class ChannelPriv:
    def __init__(self, isop = False, isvoice = False, level = 0):
        self.op = isop
        self.voice = isvoice
        self.level = level