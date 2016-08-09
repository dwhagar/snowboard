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

import sqlite3

'''Connection to the channels database.'''

class ChannelDB:
    def __init__(self, network, channel):
        self.channel = channel.lower()
        self.network = network
        self.database = network.lower() + ".db"
        self.conn = None
        self.db = None

        self.__initDB()  # Make sure there is a database and it has the table.

    def channelExists(self):
        '''Determines if the channel already exists in the database.'''
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
        '''Determines if the channel already exists in the database.'''
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
        '''Saves a list of flags to the database.'''
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
        '''Closes the user database.'''
        self.conn.commit()
        self.conn.close()
        self.conn = None

    def __initDB(self):
        '''Intended to initialize a database that doesn't yet exist.'''
        self.__openDB()

        initCmd = "CREATE TABLE IF NOT EXISTS channels (channel TEXT PRIMARY KEY, flags TEXT, topic TEXT, desc TEXT, modes TEXT, announce TEXT)"

        self.db.execute(initCmd)

        self.__closeDB()

    def __openDB(self):
        '''Opens the user database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
