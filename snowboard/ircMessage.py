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
Defines a class to store data on an IRC message from the server.

//Constructor//
Accepts 5 paremeters:
net
A network object.

src
A string, the source Nick of the message.

srcHost
A string, the source user@host of the message.

dest
A string, the destination of the message.

command
A string, the command from the IRC server (such as PRIVMSG, NOTICE, etc...)

data
A string, the actual message itself.

//Data//
The following are defined in the constructor.
.net
.src
.srchost
.dest
.command
.data

.dataList
A list of words in the .data member variable, makes for easier processing to
just do this once when the object is created.
'''

class ircMessage:
    def __init__(self, net, src, srcHost, dest, command, data):
        self.net = net
        self.src = src
        self.srcHost = srcHost
        self.dest = dest
        self.command = command
        self.data = data
        self.dataList = data.split()