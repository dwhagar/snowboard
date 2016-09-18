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

import sqlite3
import time
from . import debug

class Seen:
    '''Connection to the database where seen data will be stored.'''

    def __init__(self, network):
        self.network = network
        self.database = network.lower() + ".db"
        self.conn = None
        self.db = None

        self.__initDB()  # Make sure there is a database and it has the table.

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
        result = None

        self.__openDB()

        query = "SELECT act, time FROM nicks WHERE host IS '" + host.lower() + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if not data is None:
            result = (data[0], data[1])

        self.__closeDB()

        return result

    def loadHosts(self, nick):
        '''Loads a list of hosts from the nick given.'''
        result = None

        self.__openDB()

        query = "SELECT hosts FROM hosts WHERE nick IS '" + nick.lower() + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if not data is None:
            if ' ' in data[0]:
                debug.error("Spaces detected in the hosts database for '" + nick + "'.")
            result = data[0].split(",")
            for item in result:
                if not ('@' in item):
                    debug.error(
                        "There is a hostname in the database for '" + nick + "' that is not formatted correctly.")

        self.__closeDB()

        return result

    def loadNickAction(self, nick):
        '''Load action from a given nick.'''
        result = None

        self.__openDB()

        query = "SELECT act, time FROM hosts WHERE nick IS '" + nick.lower() + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if not data is None:
            result = (data[0], data[1])

        self.__closeDB()

        return result

    def loadNicks(self, host):
        '''Loads a list of nicks from the nick given.'''
        result = None

        self.__openDB()

        query = "SELECT nicks FROM nicks WHERE host IS '" + host.lower() + "'"
        self.db.execute(query)
        data = self.db.fetchone()

        if not data is None:
            if ' ' in data[0]:
                debug.error("Spaces detected in the nicks database for '" + host + "'.")
            result = data[0].split(",")

        self.__closeDB()

        return result

    def save(self, nick, host, act):
        '''Save a nick, host, and action to the DB'''
        self.saveNick(nick, host)
        self.saveHost(nick, host)
        self.saveAction(nick, host, act)

    def saveAction(self, nick, host, act):
        '''Saves the action and time for a user.'''

        data = [act, time.time()]

        nickQuery = "UPDATE hosts SET act = ?, time = ? WHERE nick IS '" + nick.lower() + "'"
        hostQuery = "UPDATE nicks SET act = ?, time = ? WHERE host IS '" + host.lower() + "'"

        self.__openDB()
        self.db.execute(nickQuery, data)
        self.db.execute(hostQuery, data)
        self.__closeDB()

    def saveHost(self, nick, host):
        '''Saves the nick and host to the database.'''
        hosts = self.loadHosts(nick)

        if hosts is None:
            hosts = [host.lower()]
            data = [nick.lower(), ",".join(hosts), 0, ""]
            query = "INSERT INTO hosts VALUES (?, ?, ?, ?)"
        else:
            if not (host.lower() in map(str.lower, hosts)):
                hosts.append(host.lower())
                if len(hosts) > 20:
                    hosts = hosts[-20:]
            data = [nick.lower(), ",".join(hosts)]
            query = "UPDATE hosts SET nick = ?, hosts = ? WHERE nick IS '" + nick.lower() + "'"

        self.__openDB()
        self.db.execute(query, data)
        self.__closeDB()

    def saveNick(self, nick, host):
        '''Saves the nick and host to the database.'''
        nicks = self.loadNicks(host)

        self.__openDB()

        if nicks is None:
            nicks = [nick]
            data = [host.lower(), ",".join(nicks), 0, ""]
            query = "INSERT INTO nicks VALUES (?, ?, ?, ?)"
        else:
            if not (nick.lower() in map(str.lower, nicks)):
                nicks.append(nick)
                if len(nicks) > 30:
                    nicks = nicks[-30:]
            data = [host.lower(), ",".join(nicks)]
            query = "UPDATE nicks SET host = ?, nicks = ? WHERE host IS '" + host.lower() + "'"

        self.db.execute(query, data)

        self.__closeDB()

    def searchNicks(self, nick):
        '''Search through the nicks in the DB'''
        result = []
        self.__openDB()

        query = "SELECT nicks FROM nicks"

        self.db.execute(query)
        data = self.db.fetchall()

        for row in data:
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
        '''Takes a list and removes the duplicates, case insenetive.'''
        result = []

        for item in lst:
            if not (item.lower() in map(str.lower, result)):
                result.append(item)

        return result

    def cleanDB(self):
        '''Cleans the database of possible errors.'''
        nickQuery = "SELECT host, nicks FROM nicks"
        hostQuery = "SELECT nick, hosts FROM hosts"
        saveDB = False

        self.__openDB()
        self.db.execute(nickQuery)
        nickData = self.db.fetchall()
        self.db.execute(hostQuery)
        hostData = self.db.fetchall()
        self.__closeDB()

        for row in nickData:
            host = row[0]
            if (not ('@' in host)) or (' ' in host):
                query = "DELETE FROM nicks WHERE host IS '" + host + "'"
                self.__openDB()
                self.db.execute(query)
                self.__closeDB()
            else:
                nickList = row[1].split(',')
                delIndex = []

                if len(nickList) > 30:
                    nickList = nickList[-30:]
                    saveDB = True

                for x in range(len(nickList)):
                    if nickList[x][0] == ':':
                        nickList[x] = nickList[x][1:]
                        saveDB = True
                    if (nickList[x] == '') or (' ' in nickList[x]):
                        delIndex.append(x)
                        saveDB = True

                if saveDB:
                    if not (delIndex == []):
                        for idx in delIndex:
                            del nickList[idx]
                    data = [host, ",".join(nickList)]
                    query = "UPDATE nicks SET host = ?, nicks = ? WHERE host IS '" + host.lower() + "'"
                    self.__openDB()
                    self.db.execute(query, data)
                    self.__closeDB()

        for row in hostData:
            nick = row[0]
            if (nick[0] == ":") or (' ' in nick):
                query = "DELETE FROM hosts WHERE nick IS '" + nick + "'"
                self.__openDB()
                self.db.execute(query)
                self.__closeDB()
            else:
                hostList = row[1].split(',')
                delIndex = []

                if len(hostList) > 20:
                    hostList = hostList[-20:]
                    saveDB = True

                for x in range(len(hostList)):
                    if hostList[x][0] == ':':
                        hostList[x] = hostList[x][1:]
                        saveDB = True
                    if (not ('@' in hostList[x])) or (hostList[x] == '') or (' ' in hostList[x]):
                        delIndex.append(x)
                        saveDB = True

                if saveDB:
                    if not (delIndex == []):
                        for idx in delIndex:
                            del hostList[idx]
                    data = [nick, ",".join(hostList)]
                    query = "UPDATE hosts SET nick = ?, hosts = ? WHERE nick IS '" + nick.lower() + "'"
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

        initNicks = "CREATE TABLE IF NOT EXISTS hosts (nick TEXT PRIMARY KEY, hosts TEXT, time INTEGER, act TEXT)"
        initHosts = "CREATE TABLE IF NOT EXISTS nicks (host TEXT PRIMARY KEY, nicks TEXT, time INTEGER, act TEXT)"

        self.db.execute(initNicks)
        self.db.execute(initHosts)

        self.__closeDB()

    def __openDB(self):
        '''Opens the user database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
