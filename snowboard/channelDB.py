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

        query = "SELECT flags, topic, desc FROM channels WHERE channel IS '" + self.channel + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if data is None:
            flags = []
            topic = ""
            desc = ""
        else:
            flags = data[0].split(',')
            topic = data[1]
            desc = data[2]

        self.__closeDB()

        return flags, topic, desc

    def saveData(self, flags, topic, desc):
        '''Saves a list of flags to the database.'''
        if len(flags) > 0:
            flagsText = ",".join(flags).lower()
        else:
            flagsText = ""

        self.__openDB()

        data = [flagsText, topic, desc]

        if self.channelExists():
            query = "UPDATE channels SET flags = ?, topic = ?, desc = ? WHERE channel IS '" + self.channel + "'"
        else:
            query = "INSERT INTO channels VALUES (?, ?, ?)"

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

        initCmd = "CREATE TABLE IF NOT EXISTS channels (channel TEXT PRIMARY KEY, flags TEXT, topic TEXT, desc TEXT)"

        self.db.execute(initCmd)

        self.__closeDB()

    def __openDB(self):
        '''Opens the user database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
