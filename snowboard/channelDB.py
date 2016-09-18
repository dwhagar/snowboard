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

import contextlib
import sqlite3

_SQL_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS channels (
        channel  TEXT PRIMARY KEY,
        flags    TEXT,
        topic    TEXT,
        desc     TEXT,
        modes    TEXT,
        announce TEXT
    )
"""

_SQL_SELECT = """
    SELECT flags, topic, desc, modes, announce
        FROM channels
        WHERE channel = :channel
        LIMIT 1
"""

_SQL_UPDATE = """
    UPDATE channels
        SET flags = :flags, topic = :topic, desc = :desc, modes = :modes,
            announce = :announce
        WHERE channel = :channel
"""

_SQL_CONDITIONAL_INSERT = """
    INSERT INTO channels
        (channel, flags, topic, desc, modes, announce)
        SELECT :channel, :flags, :topic, :desc, :modes, :announce
            WHERE (SELECT changes() = 0)
"""

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

        self.__dbfile = network.lower() + ".db"

        # Make sure there is a database and it has the table.
        with contextlib.closing(sqlite3.connect(self.__dbfile)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_CREATE_TABLE)

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
        with contextlib.closing(sqlite3.connect(self.__dbfile)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT, {"channel" : self.channel}):
                    flags, topic, desc, modes, announce = row
                    flags = flags.split(",") if flags else []
                    topic = topic if topic else ""
                    desc  = desc  if desc  else ""
                    modes = modes if modes else ""
                    announce = announce if announce else ""
                    break
                else:
                    flags, topic, desc, modes, announce = [], "", "", "", ""

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
        data = {
            "channel"  : self.channel,
            "flags"    : ",".join(flags).lower(),
            "topic"    : topic,
            "desc"     : desc,
            "modes"    : modes,
            "announce" : announce
        }

        with contextlib.closing(sqlite3.connect(self.__dbfile)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_UPDATE, data)
                cursor.execute(_SQL_CONDITIONAL_INSERT, data)
