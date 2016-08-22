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

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

class ircMessage:
    '''
    A data structure to hold information on an IRC message from the server.

    Public Data Members:
        net:
            A Network object, a reference to the network object which created
            the object.
        src:
            A string object for the source Nick of a message.
        srcHost:
            A string object for the host of a message.
        dest:
            A string object for the destination of a message.  This is either
            the bots own Nick or a channel name.
        command:
            A string object for what IRC command was used to send the message
            (PRIVMSG, NOTICE, one of the translated CTCP commands, etc.).
        data:
            A string object The string data for everything after the command
            or the colon.
        dataList:
            A list of string objects of each individual word in data.
    '''
    def __init__(self, net, src, srcHost, dest, command, data):
        '''
        Initializes the ircMessage object.

        :param net:
            Network object for the originating server.
        :param src:
            String object for the source Nick of the message.
        :param srcHost:
            String object for the source host of the message.
        :param dest:
            String object for the destination of the message.
        :param command:
            String object for the IRC Command used to send the message.
        :param data:
            String object for the data of the message.
        '''
        self.net = net
        self.src = src
        self.srcHost = srcHost
        self.dest = dest
        self.command = command
        self.data = data
        self.dataList = data.split()