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
Defines a class to store, retreieve, alter, and delete records in a user
database.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import contextlib
import sqlite3
import os.path
import hashlib
import base64
import re

from . import passwordTools
from .user import User

_BAD_CHARACTERS = "|-*/<>,=~();`"

_SQL_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        uid       TEXT PRIMARY KEY,
        user      TEXT UNIQUE,
        password  TEXT,
        hostmasks TEXT,
        level     INTEGER,
        flags     TEXT,
        channels  TEXT
    )
"""

_SQL_CHECK_UID_EXISTS = "SELECT 1 from users WHERE uid = :uid LIMIT 1"

_SQL_DELETE_BY_UID = "DELETE FROM users WHERE uid = :uid"

_SQL_INSERT = """
    INSERT INTO users
        (uid, user, password, hostmasks, level, flags, channels)
        VALUES
        (:uid, :user, :password, :hostmasks, :level, :flags, :channels)
"""

_SQL_SELECT_BY_UID = """
    SELECT uid, user, password, hostmasks, level, flags, channels
        FROM users
        WHERE uid = :uid
        LIMIT 1
"""

_SQL_SELECT_BY_USER = """
    SELECT uid, user, password, hostmasks, level, flags, channels
        FROM users
        WHERE user = :user
        LIMIT 1
"""

_SQL_SELECT_UIDS_AND_HOSTMASKS = "SELECT uid, hostmasks FROM users"

_SQL_SELECT_USERS = "SELECT uid, user, password, hostmasks, level, flags, channels FROM users"

_SQL_UPDATE = """
    UPDATE users
        SET user = :user, password = :password, hostmasks = :hostmasks,
            level = :level, flags = :flags, channels = :channels
        WHERE uid = :uid
"""

class Users:
    def __init__(self, network):
        self.network = network
        self.__dbname = network.lower() + ".db"

        # Make sure there is a database and it has the table.
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_CREATE_TABLE)

    def addUser(self, user, password = None):
        '''Adds a user record to the database'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_INSERT, self.__userToDbRow(user))

    def getUsers(self):
        '''Gets a list of all users.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            connection.row_factory = sqlite3.Row
            with connection as cursor:
                return [ self.__userFromDbRow(row) for row in cursor.execute(_SQL_SELECT_USERS) ]

    def matchHost(self, hostmask):
        '''Finds a user based on a given hostmask.  Returns UID or None.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_UIDS_AND_HOSTMASKS):
                    uid, masks = row
                    maskList = masks.split(",")
                    for mask in maskList:
                        if re.search(self.__convertWild(mask), hostmask, flags = re.IGNORECASE):
                            return uid
        return None

    def matchUser(self, userName):
        '''Finds a user based on a given user name.  Returns UID or None.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_BY_USER, {"user" : self.__cleanInput(userName)}):
                    return row[0]
        return None

    def removeUser(self, uid):
        '''Remove a user by UID from the database.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_DELETE_BY_UID, { "uid" : uid })

    def uidExists(self, uid):
        '''Checks to see if a UID exists in the database already.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                for row in cursor.execute(_SQL_CHECK_UID_EXISTS, { "uid" : uid }):
                    return True
        return False

    def uidHash(self, name):
        '''Creates a base64 encoded hash for the uid of a given user name.'''
        # Create the hash.
        sha = hashlib.sha1()
        sha.update(name.lower().encode('utf-8'))
        sha.update(self.network.lower().encode('utf-8'))
        data = sha.digest()

        # Encode it for storage as a string.
        result = base64.b64encode(data).decode('utf-8')

        return result

    def updateUser(self, user, password = None):
        '''Updates a user record in the database'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            with connection as cursor:
                cursor.execute(_SQL_UPDATE, self.__userToDbRow(user))

    def userInformation(self, uid):
        '''Retreives user information from the database given a uid.'''
        with contextlib.closing(sqlite3.connect(self.__dbname)) as connection:
            connection.row_factory = sqlite3.Row
            with connection as cursor:
                for row in cursor.execute(_SQL_SELECT_BY_UID, {"uid" : uid}):
                    return self.__userFromDbRow(row)
        return None

    def __cleanInput(self, text):
        '''Cleans text of characters that are not allowed.'''
        for c in _BAD_CHARACTERS:
            text = text.replace(c, "")
        return text

    def __cleanList(self, lst):
        '''Cleans a list of strings.'''
        return [ self.__cleanInput(s) for s in lst ]

    def __convertWild(self, search):
        '''Converts a simple wildcard search into a regular expression.'''
        search = re.escape(search)
        search = search.replace("\?", ".")
        search = search.replace("\*", ".*")
        return search

    def __userFromDbRow(self, row):
        '''Create a user object from a users DB row (or equivalent dictionary).'''
        user = User()
        user.uid = row["uid"]
        user.user = row["user"]
        user.pwHash = row["password"]
        user.loadHostmasks(row["hostmasks"])
        user.level = int(row["level"])
        user.flags.toData(row["flags"])
        user.loadChannels(row["channels"])
        return user

    def __userToDbRow(self, user):
        '''Create a DB row dictionary from a user object.'''
        # Clamp user level
        user.level = min(255, max(user.level, 0))

        if password is not None:
            user.pwHash = passwordTools.passwordHash(password)

        # Change the username for the database.
        user.user = self.__cleanInput(user.user.lower())

        return {
            "uid"       : user.uid,
            "user"      : user.user,
            "password"  : user.pwHash,
            "hostmasks" : user.saveHostmasks(),
            "level"     : user.level,
            "flags"     : user.flags.toString(),
            "channels"  : user.saveChannels()
        }