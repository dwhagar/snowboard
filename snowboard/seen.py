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
Keep track of nicks, hosts, and who last said what.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import contextlib
import sqlite3
import time

_SQL_CREATE_HOSTS_TABLE = """
    CREATE TABLE IF NOT EXISTS hosts (
        nick  TEXT PRIMARY KEY,
        hosts TEXT,
        time  INTEGER,
        act   TEXT
    )
"""

_SQL_CREATE_NICKS_TABLE = """
    CREATE TABLE IF NOT EXISTS nicks (
        host  TEXT PRIMARY KEY,
        nicks TEXT,
        time  INTEGER,
        act   TEXT)
"""

__SQL_INSERT_INTO_HOSTS = """
    INSERT INTO hosts
        (nick, hosts, time, act)
        VALUES
        (:nick, :hosts, :time, :act)
"""

__SQL_INSERT_INTO_NICKS = """
    INSERT INTO nicks
        (host, nicks, time, act)
        VALUES
        (:host, :nicks, :time, :act)
"""

__SQL_SELECT_ACT_FROM_HOSTS_BY_NICK = """
    SELECT act, time FROM hosts WHERE nick = :nick
""" # LIMIT 1?

__SQL_SELECT_ACT_FROM_NICKS_BY_HOST = """
    SELECT act, time FROM nicks WHERE host = :host
""" # LIMIT 1?

__SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK = """
    SELECT hosts FROM hosts WHERE nick = :nick
""" # LIMIT 1?

__SQL_SELECT_NICKS_FROM_NICKS = "SELECT nicks FROM nicks"

__SQL_SELECT_NICKS_FROM_NICKS_BY_HOST = """
    SELECT nicks FROM nicks WHERE host = :host
""" # LIMIT 1?

_SQL_UPDATE_ACT_IN_HOSTS = """
    UPDATE hosts
        SET act = :act, time = :time
        WHERE nick = :nick
"""

_SQL_UPDATE_ACT_IN_NICKS = """
    UPDATE nicks
        SET act = :act, time = :time
        WHERE host = :host
"""

__SQL_UPDATE_HOSTS_IN_HOSTS = """
    UPDATE hosts
        SET hosts = :hosts
        WHERE nick = :nick
"""

__SQL_UPDATE_NICKS_IN_NICKS = """
    UPDATE nicks
        SET nicks = :nicks
        WHERE host = :host
"""

class Seen:
    '''Connection to the database where seen data will be stored.'''

    def __init__(self, network):
        self.network = network

        self.__dbname = network.lower() + ".db"

        # Make sure there is a database and it has the table.
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_CREATE_HOSTS_TABLE)
                cursor.execute(_SQL_CREATE_NICKS_TABLE)

    def hostSearch(self, host):
        '''Finds all hosts associated with a nick.'''
        result = None
        done = False

        prevNicks = []
        prevHosts = []

        nicks = self.loadNicks(host)
        hosts = [host]

        while not done:
            for nick in nicks:
                hosts += self.loadHosts(nick)

            hosts = list(set(hosts)).sort()

            for host in hosts:
                nicks += self.loadNicks(host)

            nicks = list(set(nicks)).sort()

            if (prevNicks == nicks) and (prevHosts == hosts):
                done = True
                result = (nicks, hosts)
            else:
                prevNicks = nicks
                prevHosts = hosts

        return result

    def nickSearch(self, nick):
        '''Finds all hosts associated with a nick.'''
        result = (None, None)
        done = False

        prevNicks = []
        prevHosts = []

        nicks = [nick]
        hosts = self.loadHosts(nick)

        if not (hosts is None):
            while not done:
                for host in hosts:
                    nicks += self.loadNicks(host)

                nicks = self.__removeDupes(nicks)

                for nick in nicks:
                    hosts += self.loadHosts(nick)

                hosts = self.__removeDupes(hosts)

                if (prevNicks == nicks) and (prevHosts == hosts):
                    done = True
                    result = (nicks, hosts)
                else:
                    prevNicks = nicks[:]
                    prevHosts = hosts[:]

        return result

    def loadHostAction(self, host):
        '''Load action from a given nick.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_ACT_FROM_NICKS_BY_HOST, { "host" : host.lower() }):
                    act, time = row
                    return row
        return None

    def loadHosts(self, nick):
        '''Loads a list of hosts from the nick given.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK, { "nick" : nick.lower() }):
                    return row[0].split(",")
        return None

    def loadNickAction(self, nick):
        '''Load action from a given nick.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_ACT_FROM_HOSTS_BY_NICK, { "nick" : nick.lower() }):
                    act, time = row
                    return row
        return None

    def loadNicks(self, host):
        '''Loads a list of nicks from the nick given.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_NICKS_FROM_NICKS_BY_HOST, { "host" : host.lower() }):
                    return row[0].split(",")
        return None

    def save(self, nick, host, act):
        '''Save a nick, host, and action to the DB'''
        self.saveNick(nick, host)
        self.saveHost(nick, host)
        self.saveAction(nick, host, act)

    def saveAction(self, nick, host, act):
        '''Saves the action and time for a user.'''
        t = time.time()
        # Could possibly compact both dictionaries into one, if sure there
        # will be no issue between nick and host.
        hosts_data = {
            "nick" : nick.lower(),
            "act"  : act,
            "time" : t
        }
        nicks_data = {
            "host" : host.lower(),
            "act"  : act,
            "time" : t
        }
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_UPDATE_ACT_IN_HOSTS, hosts_data)
                cursor.execute(_SQL_UPDATE_ACT_IN_NICKS, nicks_data)

    def saveHost(self, nick, host):
        '''Saves the nick and host to the database.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            # First load hosts.
            hosts = None
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK, { "nick" : nick.lower() }):
                    hosts = row[0].split(",")

            if not hosts:
                data = {
                    "nick"  : nick.lower(),
                    "hosts" : host.lower(),
                    "time"  : 0,
                    "act"   : ""
                }
                sql = __SQL_INSERT_INTO_HOSTS
            else:
                if not (host.lower() in map(str.lower, hosts)):
                    hosts = hosts[-19:] + [host.lower()]
                data = {
                    "nick"  : nick.lower(),
                    "hosts" : ",".join(hosts)
                }
                sql = __SQL_UPDATE_HOSTS_IN_HOSTS

            with connection as cursor:
                cursor.execute(sql, data)

    def saveNick(self, nick, host):
        '''Saves the nick and host to the database.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            # First load nicks.
            nicks = None
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_NICKS_FROM_NICKS):
                    nicks = row[0].split(",")

            if not nicks:
                data = {
                    "host"  : host.lower(),
                    "nicks" : nick,
                    "time"  : 0,
                    "act"   : ""
                    "
                }
                sql = __SQL_INSERT_INTO_NICKS
            else:
                if not (nick.lower() in map(str.lower, nicks)):
                    nicks = nicks[-29:] + [nick]
                data = {
                    "host"  : host.lower(),
                    "nicks" : ",".join(nicks)
                }
                sql = __SQL_UPDATE_NICKS_IN_NICKS

            with connection as cursor:
                cursor.execute(sql, data)

    def searchNicks(self, nick):
        '''Search through the nicks in the DB'''
        result = []
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(__SQL_SELECT_NICKS_FROM_NICKS):
                    nickList = row[0].split(',')
                    for item in nickList:
                        if item.lower().find(nick.lower()) > -1:
                            result.append(item)

        result = self.__removeDupes(result)

        return result

    def timeSearch(self, nicks, hosts):
        '''Searching through nicks and hosts, find the most recent thing.'''
        # Store the resulting variables.
        lastAct = ""
        maxTime = 0
        lastNick = ""
        lastHost = ""

        for nick in nicks:
            act, t = self.loadNickAction(nick)
            if t > maxTime:
                maxTime = t
                lastNick = nick
                lastAct = act

        for host in hosts:
            act, t = self.loadHostAction(host)
            if t >= maxTime:
                maxTime = t
                lastHost = host
                lastAct = act

        result = (maxTime, lastNick, lastHost, lastAct)

        return result

    def __removeDupes(self, lst):
        '''Takes a list and removes the duplicates, case insenetive.'''
        result = []

        for item in lst:
            if not (item.lower() in map(str.lower, result)):
                result.append(item)

        return result
