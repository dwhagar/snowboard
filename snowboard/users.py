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
seperated list of hostmasks, user level, comma seperated list of approved
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

approved:
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
        self.conn = None
        self.db = None
        
        self.__initDB() # Make sure there is a database and it has the table.
        
    def __openDB(self):
        '''Opens the user database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()
        
    def __closeDB(self):
        '''Closes the user database.'''
        self.conn.commit()
        self.conn.close()
        self.conn = None

    def __initDB(self):
        '''Intended to initialize a database that doesn't yet exist.'''
        self.__openDB()
        
        if self.table == "global":
            initCmd = "CREATE TABLE IF NOT EXISTS " + self.table + " (uid TEXT PRIMARY KEY, user TEXT UNIQUE, password TEXT, hostmasks TEXT, level INTEGER, approved TEXT, denied TEXT)"
        else:
            initCmd = "CREATE TABLE IF NOT EXISTS " + self.table + " (uid TEXT PRIMARY KEY, level INTEGER, approved TEXT, denied TEXT)"

        self.db.execute(initCmd)
        
        self.__closeDB()
        
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
        
    def __passwordHash(self, password):
        '''Creates a base64 encoded hash from a password.'''
        sha512 = hashlib.sha256()
        sha512.update(password.encode('utf-8'))
        data = sha512.digest()
        result = base64.b64encode(data).decode('utf-8')
        return result
        
    def __passwordCheck(self, password, hash):
        '''Give a true/false result if a password is valid given a hash.'''
        result = False
        
        if self.__passwordHash(password) == hash:
            result = True
            
        return result
    
    def __convertWild(self, search):
        '''Converts a simple wildcard search into a regular expression.'''
        new = search.replace('.', "\.")
        new = new.replace('?',".?")
        new = new.replace('*',".*")
        return new
    
    def matchHost(self, hostmask):
        '''Finds a user based on a given hostmask.  Returns UID or None.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT uid, hostmasks FROM " + self.table
        
        # Iterate through all entries in that list.
        for row in self.db.execute(query):
            uid, masks = row
            maskList = masks.split(',')
            for mask in maskList:
                if re.search(self.__convertWild(mask), hostmask):
                    result = uid
                    break
            if not (result == None):
                break
        
        self.__closeDB()
        return result
        
    def matchUser(self, userName):
        '''Finds a user based on a given user name.  Returns UID or None.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT uid FROM " + self.table + " WHERE user IS '" + userName + "' COLLATE NOCASE"
        self.db.execute(query)
        data = self.db.fetchone()
        
        if not data == None:
            result = data[0]
        
        self.__closeDB()
        return result
    
    def uidExists(self, uid):
        '''Checks to see if a UID exists in the database already.'''
        self.__openDB()
        
        query = "SELECT uid FROM " + self.table + " WHERE uid IS '" + uid + "' COLLATE NOCASE"
        self.db.execute(query)
        data = self.db.fetchone()
        
        if data == None:
            result = False
        else:
            result = True
        
        return result
        
    def addUser(self, uid, user = None, password = None, hostmasks = [],
                level = 0, approvedList = [], deniedList = []):
        '''Adds a user record to the database'''
        
        if level > 255:
            level = 255
        elif level < 0:
            level = 0

        self.__openDB()
        
        # Convert the lists into CSV format.
        masks = ','.join(hostmasks)
        approved = ','.join(approvedList)
        denied = ','.join(deniedList)
        
        # Create a list to pass onto the function and store in the DB.
        if self.table == "global":
            data = [
                uid,
                user,
                self.__passwordHash(password),
                masks,
                level,
                approved.lower(),
                denied.lower()
            ]
        else:
            data = [
                uid,
                level,
                approved.lower(),
                denied.lower()
            ]
        
        # Create the SQL query line, using ?'s where the function will
        # fill in the data from the list.
        if self.table == "global":
            query = "INSERT INTO " + self.table + " VALUES (?, ?, ?, ?, ?, ?, ?)"
        else:
            query = "INSERT INTO " + self.table + " VALUES (?, ?, ?, ?)"

        self.db.execute(query, data)
        
        self.__closeDB()
        
        return uid
        
    def updateUser(self, uid, user = None, password = None, hostmasks = [], level = 0,
                approvedList = [], deniedList = []):
        self.__openDB()
        
        if level > 255:
            level = 255
        elif level < 0:
            level = 0
        
        # Convert the lists into CSV format.
        masks = ','.join(hostmasks)
        approved = ','.join(approvedList)
        denied = ','.join(deniedList)
        
        if self.table == "global":
            data = [
                uid,
                user,
                self.__passwordHash(password),
                masks,
                level,
                approved.lower(),
                denied.lower()
            ]
        else:
            data = [
                uid,
                level,
                approved.lower(),
                denied.lower()
            ]

        
        # Set the query.
        if self.table == "global":
            query = "UPDATE " + self.table + " SET user = ?, password = ?, hostmasks = ?, level = ?, approved = ?, denied = ? WHERE uid IS '" + uid + "'"
        else:
            query = "UPDATE " + self.table + " SET level = ?, approved = ?, denied = ? WHERE uid IS '" + uid + "'"
        
        self.db.execute(query, data)
        
        self.__closeDB()
    
    def removeUser(self, uid):
        '''Remove a user by UID from the database.'''
        self.__openDB()
        
        # Build the query, then execute.
        query = "DELETE FROM " + self.table + " WHERE uid IS '" + uid + "'"
        print(query)
        self.db.execute(query)
        
        self.__closeDB()
    
    def verifyUser(self, uid, password):
        '''Verifies a user password against that which is in the database.'''
        result = False
        
        # Open the DB
        self.__openDB()
        
        query = "SELECT password FROM " + self.table + " WHERE uid IS '" + uid + "'"
        
        # Look up the UID in the database, retrieve the password.
        self.db.execute(query)
        data = self.db.fetchone()
        
        # If there is data, check it.
        if not data == None:
            data = data[0]
            result = self.__passwordCheck(password, data)
        
        # Close the DB    
        self.__closeDB()
        
        return result
        
    def userInformation(self, uid):
        '''Retreives user information from the database given a uid.'''
        # Open the DB
        self.__openDB()
        
        # Retrieve everything about a user from the DB.
        if self.table == "global":
            query = "SELECT user, hostmasks, level, approved, denied FROM " + self.table + " WHERE uid IS '" + uid + "'"
        else:
            query = "SELECT level, approved, denied FROM " + self.table + " WHERE uid IS '" + uid + "'"
        
        # Actually do the search.
        self.db.execute(query)
        data = self.db.fetchone()
        
        # Process the data.
        if data == None:
            result = None
        else:
            # Split up the data as needed.
            if self.table == "global":
                user, hostmasks, level, approved, denied = data
                hostmaskList = hostmasks.split(',')
            else:
                level, approved, denied = data

            approvedList = approved.split(',')
            deniedList = denied.split(',')

            if self.table == "global":
                result = (user, hostmaskList, level, approvedList, deniedList)
            else:
                result = (level, approvedList, deniedList)
        
        self.__closeDB()
        
        return result