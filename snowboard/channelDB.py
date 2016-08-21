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
ChannelDB class, provides a connection to a database for channel settings.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import sqlite3

class ChannelDB:
    '''
    Allows a Channel object to use the database to store information.

    Public Data Members:
        channel:
            A string object for the name of a channel for which the database
            has information.
        network:
            A string object representing the network name, which is used to
            also derive the filename of the database.
        conn:
            An sqlite3 object, connection to the actual sqlite database file.
        db:
            Direct access to the database itself.
    '''
    def __init__(self, network, channel):
        '''
        Initializes the ChannelDB object.

        :param network:
            A string object with the name of the network, intended to be all
            lowercase (will be converted anyway).
        :param channel:
            A string object with the name of the channel, intended to be all
            lowercase (will be converted anyway).
        '''
        self.channel = channel.lower()
        self.network = network
        self.database = network.lower() + ".db"
        self.conn = None
        self.db = None

        self.__initDB()  # Make sure there is a database and it has the table.

    def channelExists(self):
        '''
        Determines if the channel already exists in the database.

        :return:
            Boolean object, true or false on the existence of a channel in the
            database.
        '''
        self.__openDB()

        query = "SELECT flags FROM channels WHERE channel IS '" + self.channel + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if data is None:
            result = False
        else:
            result = True

        self.__closeDB()

        return result

    def loadData(self):
        '''
        Loads data from the database.  If a channel does not exist in the
        datbase, it will return blank strings/lists for all attributes.

        :return:
            A tuple containing the following:
                flags:
                    A list of string objects containing flags for a channel.
                topic:
                    A string object containing the default topic of a channel.
                desc:
                    A string ojbect containing the description for a channel.
                modes:
                    A string object of default channel mods.
                announce:
                    A string ojbect of the channels announcement.
        '''
        self.__openDB()

        query = "SELECT flags, topic, desc, modes, announce FROM channels WHERE channel IS '" + self.channel + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if data is None:
            flags = []
            topic = ""
            desc = ""
            modes = ""
            announce = ""
        else:
            flags = data[0].split(',')
            topic = data[1]
            desc = data[2]
            modes = data[3]
            announce = data[4]

        if flags is None:
            flags = ""
        if topic is None:
            topic = ""
        if desc is None:
            desc = ""
        if modes is None:
            modes = ""
        if announce is None:
            announce = ""

        self.__closeDB()

        return flags, topic, desc, modes, announce

    def saveData(self, flags, topic, desc, modes, announce):
        '''
        Saves channel data to the database.

        :param flags:
            A list of string objects, containing a channel's flags.
        :param topic:
            A string object containing a channel's default topic.
        :param desc:
            A string object containing the default description for a channel.
        :param modes:
            A string object containing the default modes of a channel.
        :param announce:
            A string object containing the channel's announcement.
        '''
        if len(flags) > 0:
            flagsText = ",".join(flags)
        else:
            flagsText = ""

        if self.channelExists():
            data = [flagsText.lower(), topic, desc, modes, announce]
            query = "UPDATE channels SET flags = ?, topic = ?, desc = ?, modes = ?, announce = ? WHERE channel IS '" + self.channel + "'"
        else:
            data = [self.channel, flagsText.lower(), topic, desc, modes, announce]
            query = "INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?)"

        self.__openDB()
        self.db.execute(query, data)
        self.__closeDB()

    def __closeDB(self):
        '''Closes the database out, saving all changes made.'''
        self.conn.commit()
        self.conn.close()
        self.conn = None

    def __initDB(self):
        '''Initializes the database if one does not exist.'''
        self.__openDB()

        initCmd = "CREATE TABLE IF NOT EXISTS channels (channel TEXT PRIMARY KEY, flags TEXT, topic TEXT, desc TEXT, modes TEXT, announce TEXT)"

        self.db.execute(initCmd)

        self.__closeDB()

    def __openDB(self):
        '''Opens the channel database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
