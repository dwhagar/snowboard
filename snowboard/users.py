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

The user database will store a table for each channel where specific
privileges are stored, as well as a global table for global privileges.

Each table shall consist of a unique ID (uid), a user name, comma
seperated list of hostmasks, user level, comma seperated list of accepted
flags, comma seperated list of deny flags.

uid:
shall be unique and act as the primary key across all tables and will use
an sha1 hash of the network name and username to produce a UID.  This will
use base64 to represent the binary data in the database.

user:
shall be a username, usually set to the users default Nick but this is not
required.  Usernames must be unique in the system, as they are used to
generate the UID.

password:
shall be the sha512 hashed and base64 converted string.

hostmasks:
shall be stored with simple wildcards only, * or ? wich will
act as one would expect, a ? for a single character wildcard and a * for
many, any given item in this list shall be intended to directly go into
the match function.

level:
shall be an integer storing a simple number from 0 to 255 which
signifies the user level, 255 being the highest access and 0 being no access.

accepted:
shall be a comma seperated list, each item will be taken as a single flag
for which operations are approved for that user.

denied:
shall be a comma seperated list, each item will be taken as a single flag
for which operations are denied for that user.
'''

import sqlite3
import os.path
import hashlib
import base64
import re

class Users:
    def __init__(self, network, table = "global"):
        self.network = network
        self.database = network.lower() + "-users.db"
        self.table = table
        self.conn = sqlite3.connect(self.database)
        self.db = None
        
        self.__initDB() # Make sure there is a database and it has the table.
        
    def __openDB(self):
        '''Opens the user database up for use.'''
        self.db = self.conn.cursor()
        
    def __closeDB(self):
        '''Closes the user database.'''
        self.db = self.conn.commit()
        self.db = self.conn.close()

    def __initDB(self):
        '''Intended to initialize a database that doesn't yet exist.'''
        self.__openDB()
        
        initCmd = "CREATE TABLE IF NOT EXISTS " + self.table + " (uid TEXT PRIMARY KEY, user TEXT, password TEXT, hostmasks TEXT, level INTEGER, approved TEXT, denied TEXT)"
        
        self.db.execute(initCmd)
        
    def __uidHash(self, name):
        '''Creates a base64 encoded hash for the uid of a given user name.'''
        # Create the has.
        sha = hashlib.sha1()
        sha.update(name.lower().encode('utf-8'))
        sha.update(self.network.lower().encode('utf-8'))
        data = sha.digest()
        
        # Encode it for storage as a string.
        result = base64.b64encode(data).decode('utf-8')
        
        return result
        
    def __passwordHash(self, password):
        '''Creates a base64 encoded hash from a password.'''
        sha512 = hashlib.sha256()
        sha512.update(password.encode('utf-8'))
        data = sha512.digest()
        result = base64.b64encode(data).decode('utf-8')
        return result
        
    def passwordCheck(self, password, hash):
        '''Give a true/false result if a password is valid given a hash.'''
        result = False
        
        if self.__passwordHash(password) == hash:
            result = True
            
        return result
    
    def __convertWild(self, search):
        '''Converts a simple wildcard search into a regular expression.'''
        new = search.replace('?',".?")
        new = new.replace('*',".*")
        return new
    
    def findHost(self, hostmask):
        '''Finds a user based on a given hostmask.  Returns UID or None.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT uid, hostmask FROM ?"
        
        # Iterate through all entries in that list.
        for row in self.db.execute(query, self.table):
            for mask in row[1]:
                search = re.compile(self.__convertWild(mask))
                if not (search.match(hostmask) == None):
                    result = row[0]
                    break
            if not (result == None):
                break
        
        self.__closeDB()
        return result
        
    def addUser(self, user, password, hostmasks = [], level = 0,
                accepted = "", denied = ""):
        '''Adds a user record to the database'''
        self.__openDB()
        
        masks = ','.join(hostmasks)
        
        data = [
            self.__uidHash(user),
            user,
            self.__passwordHash(password),
            masks,
            level,
            accepted,
            denied
        ]
        
        query = "INSERT INTO " + self.table + " VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.db.execute(query, data)
        
        self.__closeDB()