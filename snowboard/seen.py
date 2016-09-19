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
from . import debug

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

_SQL_INSERT_INTO_HOSTS = """
    INSERT INTO hosts
        (nick, hosts, time, act)
        VALUES
        (:nick, :hosts, :time, :act)
"""

_SQL_INSERT_INTO_NICKS = """
    INSERT INTO nicks
        (host, nicks, time, act)
        VALUES
        (:host, :nicks, :time, :act)
"""

_SQL_SELECT_ACT_FROM_HOSTS_BY_NICK = """
    SELECT act, time FROM hosts WHERE nick = :nick
""" # LIMIT 1?

_SQL_SELECT_ACT_FROM_NICKS_BY_HOST = """
    SELECT act, time FROM nicks WHERE host = :host
""" # LIMIT 1?

_SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK = """
    SELECT hosts FROM hosts WHERE nick = :nick
""" # LIMIT 1?

_SQL_SELECT_NICKS_FROM_NICKS = "SELECT nicks FROM nicks"

_SQL_SELECT_NICKS_FROM_NICKS_BY_HOST = """
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

_SQL_UPDATE_HOSTS_IN_HOSTS = """
    UPDATE hosts
        SET hosts = :hosts
        WHERE nick = :nick
"""

_SQL_UPDATE_NICKS_IN_NICKS = """
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

                    sortedNicks, sortedHosts = self.recentSort(nicks, hosts)
                    resultNicks = []
                    resultHosts = []

                    for item in sortedNicks:
                        resultNicks.append(item[0])
                    for item in sortedHosts:
                        resultHosts.append(item[0])

                    result = resultNicks, resultHosts

                else:
                    prevNicks = nicks[:]
                    prevHosts = hosts[:]

        return result

    def loadHostAction(self, host):
        '''Load action from a given nick.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_ACT_FROM_NICKS_BY_HOST, {"host": host.lower()}):
                    act, time = row
                    return row
        return None

    def loadHosts(self, nick):
        '''Loads a list of hosts from the nick given.'''
        result = None
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK, {"nick": nick.lower()}):
                    result = row[0]
        if result:
            if " " in result:
                debug.error("Spaces detected in the hosts database for '" + nick + "'.")
            result = result.split(",")
            for item in result:
                if "@" not in item:
                    debug.error("There is a hostname in the database for '" + nick + "' that is not formatted correctly.")
        return result

    def loadNickAction(self, nick):
        '''Load action from a given nick.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_ACT_FROM_HOSTS_BY_NICK, {"nick": nick.lower()}):
                    act, time = row
                    return row
        return None

    def loadNicks(self, host):
        '''Loads a list of nicks from the nick given.'''
        result = None
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_NICKS_FROM_NICKS_BY_HOST, {"host": host.lower()}):
                    return row[0].split(",")
        if result is not None:
            if ' ' in result:
                debug.error("Spaces detected in the nicks database for '" + host + "'.")
            result = result.split(",")
        return result

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
                for row in cursor.execute(_SQL_SELECT_HOSTS_FROM_HOSTS_BY_NICK, {"nick": nick.lower()}):
                    hosts = row[0].split(",")

            if not hosts:
                data = {
                    "nick"  : nick.lower(),
                    "hosts" : host.lower(),
                    "time"  : 0,
                    "act"   : ""
                }
                sql = _SQL_INSERT_INTO_HOSTS
            else:
                if not (host.lower() in map(str.lower, hosts)):
                    hosts = hosts[-99:] + [host.lower()]
                data = {
                    "nick"  : nick.lower(),
                    "hosts" : ",".join(hosts)
                }
                sql = _SQL_UPDATE_HOSTS_IN_HOSTS

            with connection as cursor:
                cursor.execute(sql, data)

    def saveNick(self, nick, host):
        '''Saves the nick and host to the database.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            # First load nicks.
            nicks = None
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_NICKS_FROM_NICKS):
                    nicks = row[0].split(",")

            if not nicks:
                data = {
                    "host"  : host.lower(),
                    "nicks" : nick,
                    "time"  : 0,
                    "act"   : ""
                }
                sql = _SQL_INSERT_INTO_NICKS
            else:
                if not (nick.lower() in map(str.lower, nicks)):
                    nicks = nicks[-99:] + [nick]
                data = {
                    "host"  : host.lower(),
                    "nicks" : ",".join(nicks)
                }
                sql = _SQL_UPDATE_NICKS_IN_NICKS

            with connection as cursor:
                cursor.execute(sql, data)

    def searchNicks(self, nick):
        '''Search through the nicks in the DB'''
        result = []
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_NICKS_FROM_NICKS):
                    nickList = row[0].split(',')
                    for item in nickList:
                        if item.lower().find(nick.lower()) > -1:
                            result.append(item)

        result = self.__removeDupes(result)

        return result

    def recentSort(self, nicks, hosts):
        '''
        Sorts the nicks and hosts lists given by how recently activity was
        last seen on each item.
        '''

        sortedNicks = []
        sortedHosts = []

        for nick in nicks:
            act, t = self.loadNickAction(nick)
            sortedNicks.append((nick, t, act))

        for host in hosts:
            act, t = self.loadHostAction(host)
            sortedHosts.append((host, t, act))

        sortedNicks.sort(key = lambda data: data[1])
        sortedHosts.sort(key = lambda data: data[1])

        return sortedNicks, sortedHosts

    def removeNick(self, nck):
        '''Completely removes a nick from the database.'''
        # First the hard part, removing all instances of the nick from the
        # nicks table.
        found = False
        nck = nck.lower()
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            to_delete = []
            to_update = []
            with connection as cursor:
                for row in cursor.execute("SELECT host, nicks FROM nicks"):
                    host, nicks = row
                    nicks = nicks.split(",")
                    # Save the original number of nicks, then remove any
                    # instance of the target nick.
                    nicks_old_len = len(nicks)
                    nicks = list(filter(lambda n: n.lower() != nck, nicks))
                    # If the number of nicks has changed, we have to do a
                    # delete or update.
                    nicks_new_len = len(nicks)
                    if nicks_new_len != nicks_old_len:
                        found = True
                        if nicks_new_len == 0:
                            to_delete.append({"host" : host})
                        else:
                            to_update.append({"host" : host, "nicks" : ",".join(nicks)})
                # Now that we have the lists of rows to delete or update,
                # do the deletes first then commit.
                cursor.executemany("DELETE FROM nicks WHERE host = :host", to_delete)
            # Then do the updates as a separate transaction.
            with connection as cursor:
                cursor.executemany("UPDATE nicks SET nicks = :nicks WHERE host = :host", to_update)
            # Now the easy part: the hosts table.
            with connection as cursor:
                for row in cursor.execute("SELECT 1 FROM hosts where nick = :nick LIMIT 1", {"nick" : nck}):
                    found = True
                    cursor.execute("DELETE FROM hosts WHERE nick = :nick", {"nick" : nck})
        return found

    def timeSearch(self, nicks, hosts):
        '''Searching through nicks and hosts, find the most recent thing.'''

        # TODO: Use the new recentSort function to simplify this.

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
        '''Takes a list and removes the duplicates, case insensitive.'''
        result = []

        for item in lst:
            if not (item.lower() in map(str.lower, result)):
                result.append(item)

        return result

    def cleanDB(self):
        '''Cleans the database of possible errors.'''
        self.cleanHosts()
        self.cleanNicks()

    def cleanHosts(self):
        '''Cleans the hosts table of possible errors.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            bad_nicks = []
            updates = []
            with connection as cursor:
                for row in cursor.execute("SELECT nick, hosts FROM hosts"):
                    nick, hosts = row
                    if nick.startswith(":") or " " in nick:
                        bad_nicks.append({ "nick" : nick })
                    else:
                        hosts = hosts.split(",")
                        update = False
                        # Trim to last 100.
                        update = update or len(hosts) > 100
                        hosts = hosts[-100:]
                        # Remove hosts with spaces.
                        update = update or any(map(lambda s: " " in s, hosts))
                        hosts = [ n for n in hosts if " " not in n ]
                        # Remove preceding ":".
                        update = update or any(map(lambda s: s.startswith(":"), hosts))
                        hosts = list(map(lambda s: s[1:] if s.startswith(":") else s, hosts))
                        # Remove hosts without "@".
                        update = update or any(map(lambda s: "@" not in s, hosts))
                        hosts = [ n for n in hosts if "@" in n ]
                        if update:
                            updates.append({"nick": nick, "hosts": ",".join(hosts)})
            # Now, delete any bad hosts and commit that transaction before
            # doing anything else.
            with connection as cursor:
                cursor.executemany("DELETE FROM hosts WHERE nick = :nick", bad_nicks)
            # Finally, do any updates to nicks that need doing.
            with connection as cursor:
                cursor.executemany("UPDATE hosts SET hosts = :hosts WHERE nick = :nick", updates)

    def cleanNicks(self):
        '''Cleans the nicks table of possible errors.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            bad_hosts = []
            updates = []
            with connection as cursor:
                for row in cursor.execute("SELECT host, nicks FROM nicks"):
                    host, nicks = row
                    if "@" not in host or " " in host:
                        bad_hosts.append({ "host" : host })
                    else:
                        nicks = nicks.split(",")
                        update = False
                        # Trim to last 100.
                        update = update or len(nicks) > 100
                        nicks = nicks[-100:]
                        # Remove nicks with spaces.
                        update = update or any(map(lambda s: " " in s, nicks))
                        nicks = [ n for n in nicks if " " not in n ]
                        # Remove preceding ":".
                        update = update or any(map(lambda s: s.startswith(":"), nicks))
                        nicks = list(map(lambda s: s[1:] if s.startswith(":") else s, nicks))
                        # Check if an update is necessary.
                        if update:
                            updates.append({"host": host, "nicks": ",".join(nicks)})
            # Now, delete any bad hosts and commit that transaction before
            # doing anything else.
            with connection as cursor:
                cursor.executemany("DELETE FROM nicks WHERE host = :host", bad_hosts)
            # Finally, do any updates to nicks that need doing.
            with connection as cursor:
                cursor.executemany("UPDATE nicks SET nicks = :nicks WHERE host = :host", updates)
