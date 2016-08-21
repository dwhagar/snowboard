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
Channel class, stores information about a channel and its members.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

from .users import Users
from .channelDB import ChannelDB

class Channel:
    '''
    Channel class contains all the data associated with a channel and its
    members.

    Public Data Members:
        announce:
            A string object for the general channel announcement.
        botnick:
            A string object containing the nick of the bot in that channel.
            It should also be a reference to the botnick in use by the
            net object.
        db:
            A ChannelDB object to provide a connection to the settings
            database.
        defaultModes:
            A string object for the default modes of a channel.
        defaultTopic:
            A string object for the default topic of a channel.
        desc:
            A description of a channel, mainly used for RP channels to
            describe the channels RP setting.
        flags:
            A list object of strings, each containing a channel flag that
            define how the bot reacts to input from that channel.
        joined:
            A boolean object to say if the channel has been joined ot not.
        joinSent:
            A boolean object to say if the join command has been sent.
        name:
            A string object for the name of the channel.
        members:
            A list object containing information on each member of a
            channel.  Each list element containing a list of two elements,
            the first being a Nick object and the second being a ChannelPriv
            object.
        modes:
            A string object for the current modes of a channel.
        network:
            A string object for the name of the current channel.
        topic:
            A strong object for the current topic of a channel.
        opped:
            A boolean object for if the bot is opped in that channel.
        voiced:
            A boolean object for if the bot is voiced in that channel.
    '''
    def __init__(self, name, network, members = []):
        '''
        Initializes the class.

        :param name:
            A string object, name of the channel.
        :param network:
            A string object, name of the network the channel resides on.
        :param members:
            Defaults to an empty list.  A list object, to store a list of 2
            item lists, each containing a Nick object at Element 1, and a
            ChannelPriv object at Element 2.
        '''
        self.announce = ""
        self.botnick = None
        self.db = ChannelDB(network, name)
        self.defaultModes = ""
        self.defaultTopic = ""
        self.desc = ""
        self.flags = []
        self.joined = False
        self.joinSent = False
        self.name = name
        self.members = members  # A list of lists, storing Nick and ChanPriv
        self.modes = ""
        self.network = network
        self.topic = ""
        self.opped = False
        self.voiced = False

        self.loadData()

    def addFlag(self, flag):
        '''
        Adds a flag string to the channel.
        Checks to make sure the flag doesn't exist before it adds to the
        channel.

        :param flag:
            A string object of the flag that needs to be added.
        '''
        # TODO: Change this to use the existing checkFlag function.
        if not (flag.lower() in map(str.lower, self.flags)):
            if not flag == "":
                self.flags.append(flag)

        self.saveData()

    def addNick(self, nick, priv):
        '''
        Adds a nick and associated privileges to a channel.
        Checks to make sure that the nick doesn't exist in the list first.

        :param nick:
            A Nick object for information on that person to the bot, globally.
            This should be a reference to a Nick out of the bots master list
            in the Network object.
        :param priv:
            A ChannelPriv object for storing a persons status within the
            channel itself.
        '''
        existing = self.findNick(nick)
        if existing is None:
            member = [nick, priv]
            self.members.append(member)

    def checkFlag(self, flag):
        '''
        Checks for a flag within the channels data.

        :param flag:
            A string object for the flag being looked for.
        :return:
            A boolean object for if the flag was found or not.
        '''
        result = False

        if flag.lower() in map(str.lower, self.flags):
            result = True

        return result

    def findNick(self, nck):
        '''
        Finds a nick within the channel and returns the data for that nick.

        :param nck:
            Can either be a Nick object of a nick to find within the channel
            or a String object for the name of a nick within the channel.
        :return:
            Returns either None (if the nick is not found) or the list item
            from the members list.  The list item will have a Nick object for
            its first element and ChannelPriv object for its second element.
        '''
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
        '''
        Returns the command to join a channel, also sets the flag so the bot
        knows that said command has been sent.

        :return:
            A list object containing a string object with the command to join
            the channel.
        '''
        if not self.joined:
            self.joinSent = True
            return ["JOIN " + self.name]

    def loadData(self):
        '''Loads data into the object from the database.'''
        self.flags, self.defaultTopic, self.desc, self.defaultModes, self.announce = self.db.loadData()

    def part(self):
        '''
        Sends the command to leave a channel, resets the flag for the join
        command having been sent.

        :return:
            A list object containing a string object with the command to leave
            a channel.
        '''
        if self.joined:
            self.joinSent = False
            return ["PART " + self.name]

    def removeFlag(self, flag):
        '''
        Removes a flag string to the channel.

        :param flag:
            A string object of the flag that needs to be added.
        '''
        if flag.lower() in map(str.lower, self.flags):
            self.flags.remove(flag.lower())

        self.saveData()

    def removeNick(self, nick):
        '''
        Finds a nick within the channel and removes it.

        :param nck:
            Can either be a Nick object of a nick to find within the channel
            or a String object for the name of a nick within the channel.
        '''
        existing = self.findNick(nick)
        if not existing is None:
            self.members.remove(existing)

    def saveData(self):
        '''Saves channel data to the database.'''
        self.db.saveData(self.flags, self.defaultTopic, self.desc, self.defaultModes, self.announce)

    def updateSelf(self):
        '''Update the bots knowledge of its own privileges.'''
        me = self.findNick(self.botnick)

        self.opped = me[1].op
        self.voiced = me[1].voice

        # This statement ensures that if the bots status has changed, it
        # updates the channels data to reflect current settings, it should
        # not be necessary, but just a safeguard.
        self.loadData()
