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

import sqlite3
import os.path
import hashlib
import base64
import re

class Users:
    def __init__(self, network, table = "global"):
        self.network = network
        self.database = network.lower() + "-users.db"
        self.table = self.__cleanInput(table)
        self.conn = None
        self.db = None
        
        self.__initDB() # Make sure there is a database and it has the table.
        
    def __cleanInput(self, text):
        '''Cleans text of characters that are not allowed.'''
        text = text.replace('|', '')
        text = text.replace('-', '')
        text = text.replace('*', '')
        text = text.replace('/', '')
        text = text.replace('<', '')
        text = text.replace('>', '')
        text = text.replace(',', '')
        text = text.replace('=', '')
        text = text.replace('~', '')
        text = text.replace('~', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace(';', '')
        text = text.replace('`', '')
        return text
        
    def __cleanList(self, list):
        '''Cleans a list of strings.'''
        newList = []
        
        for item in list:
            item = self.__cleanInput(item)
            newList.append(item)
            
        return newList
        
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
            initCmd = "CREATE TABLE IF NOT EXISTS " + self.table + " (uid TEXT PRIMARY KEY, user TEXT UNIQUE, level INTEGER, approved TEXT, denied TEXT)"
        
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
        
        self.db.execute(query)
        data = self.db.fetchall()
        
        # Iterate through all entries in that list.
        for row in data:
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
        
        userName = self.__cleanInput(userName)
        
        query = "SELECT uid FROM " + self.table + " WHERE user IS '" + userName.lower() + "'"
        self.db.execute(query)
        data = self.db.fetchone()
        
        if not data == None:
            result = data[0]
        
        self.__closeDB()
        return result
    
    def uidExists(self, uid):
        '''Checks to see if a UID exists in the database already.'''
        self.__openDB()
        
        query = "SELECT uid FROM " + self.table + " WHERE uid IS '" + uid + "'"
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
        approved = ','.join(self.__cleanList(approvedList))
        denied = ','.join(self.__cleanList(deniedList))
        
        # Create a list to pass onto the function and store in the DB.
        if self.table == "global":
            data = [
                uid,
                self.__cleanInput(user.lower()),
                self.__passwordHash(password),
                masks,
                level,
                approved.lower(),
                denied.lower()
            ]
        else:
            data = [
                uid,
                self.__cleanInput(user.lower()),
                level,
                approved.lower(),
                denied.lower()
            ]
        
        # Create the SQL query line, using ?'s where the function will
        # fill in the data from the list.
        if self.table == "global":
            query = "INSERT INTO " + self.table + " VALUES (?, ?, ?, ?, ?, ?, ?)"
        else:
            query = "INSERT INTO " + self.table + " VALUES (?, ?, ?, ?, ?)"

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
        approved = ','.join(self.__cleanList(approvedList))
        denied = ','.join(self.__cleanList(deniedList))
        
        if self.table == "global":
            data = [
                self.__cleanInput(user.lower()),
                self.__passwordHash(password),
                masks,
                level,
                approved.lower(),
                denied.lower()
            ]
        else:
            data = [
                self.__cleanInput(user.lower()),
                level,
                approved.lower(),
                denied.lower()
            ]
        
        # Set the query.
        if self.table == "global":
            query = "UPDATE " + self.table + " SET user = ?, password = ?, hostmasks = ?, level = ?, approved = ?, denied = ? WHERE uid IS '" + uid + "'"
        else:
            query = "UPDATE " + self.table + " SET user = ?, level = ?, approved = ?, denied = ? WHERE uid IS '" + uid + "'"
        
        self.db.execute(query, data)
        
        self.__closeDB()
    
    def removeUser(self, uid):
        '''Remove a user by UID from the database.'''
        self.__openDB()
        
        # Build the query, then execute.
        query = "DELETE FROM " + self.table + " WHERE uid IS '" + uid + "'"
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

    def getUsers(self):
        '''Gets a list of all users.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT user, level, approved, denied FROM " + self.table
        
        self.db.execute(query)
        data = self.db.fetchall()
        
        if not data == None:
            result = data
        
        self.__closeDB()
        return result
        