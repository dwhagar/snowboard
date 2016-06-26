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

from . import passwordTools
from .user import User

class Users:
    def __init__(self, network):
        self.network = network
        self.database = network.lower() + "-users.db"
        self.conn = None
        self.db = None
        
        self.__initDB() # Make sure there is a database and it has the table.

    def addUser(self, user, password = None):
        '''Adds a user record to the database'''
        
        if user.level > 255:
            user.level = 255
        elif user.level < 0:
            user.level = 0
        
        if not password == None:
            user.pwHash = passwordTools.passwordHash(password)

        self.__openDB()
        
        # Convert the lists into string format.
        masks = user.saveHostmasks()
        flags = user.flags.toString()
        channels = user.saveChannels()
        
        # Change the username for the database.
        user.name = self.__cleanInput(user.name.lower())
        
        # Create a list to pass onto the function and store in the DB.
        data = [
            user.uid,
            user.name,
            user.pwHash,
            masks,
            user.level,
            flags,
            channels
        ]
        
        # Create the SQL query line, using ?'s where the function will
        # fill in the data from the list.
        query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)"

        self.db.execute(query, data)
        
        self.__closeDB()

    def getUsers(self):
        '''Gets a list of all users.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT uid, user, password, hostmasks, level, flags, channels FROM users"
        
        self.db.execute(query)
        data = self.db.fetchall()
        
        userList = []
        
        if len(data) > 0:
            for item in data:
                newUser = User()
                newUser.uid = item[0]
                newUser.user = item[1]
                newUser.pwHash = item[2]
                newUser.loadHostmasks(item[3])
                newUser.level = int(item[4])
                newUser.flags.toData(item[5])
                newUser.loadChannels(item[6])
                
                userList.append(newUser)
        
        return userList

    def matchHost(self, hostmask):
        '''Finds a user based on a given hostmask.  Returns UID or None.'''
        result = None
        
        self.__openDB()
        
        query = "SELECT uid, hostmasks FROM users"
        
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
        
        query = "SELECT uid FROM users WHERE user IS '?'"
        self.db.execute(query, userName)
        data = self.db.fetchone()
        
        if not data == None:
            result = data[0]
        
        self.__closeDB()
        return result

    def removeUser(self, uid):
        '''Remove a user by UID from the database.'''
        self.__openDB()
        
        # Build the query, then execute.
        query = "DELETE FROM users WHERE uid IS '" + uid + "'"
        self.db.execute(query)
        
        self.__closeDB()
    
    def uidExists(self, uid):
        '''Checks to see if a UID exists in the database already.'''
        self.__openDB()
        
        query = "SELECT uid FROM users WHERE uid IS '" + uid + "'"
        self.db.execute(query)
        data = self.db.fetchone()
        
        if data == None:
            result = False
        else:
            result = True
        
        return result
        
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
        
        if user.level > 255:
            user.level = 255
        elif user.level < 0:
            user.level = 0

        if not password == None:
            user.pwHash = passwordTools.passwordHash(password)

        self.__openDB()
        
        # Convert the lists into string format.
        masks = user.saveHostmasks()
        flags = user.flags.toString()
        channels = user.saveChannels()

        # Change the username for the database.
        user.name = self.__cleanInput(user.name.lower())
        
        # Create a list to pass onto the function and store in the DB.
        data = [
            user.name,
            user.pwHash,
            masks,
            user.level,
            flags,
            channels
        ]
        
        # Set the query.
        query = "UPDATE users SET user = ?, password = ?, hostmasks = ?, level = ?, flags = ?, channels = ? WHERE uid IS '" + user.uid + "'"
        
        self.db.execute(query, data)
        
        self.__closeDB()

    def userInformation(self, uid):
        '''Retreives user information from the database given a uid.'''
        # Open the DB
        self.__openDB()
        
        # Retrieve everything about a user from the DB.
        query = "SELECT user, hostmasks, level, flags, channels FROM users WHERE uid IS '" + uid + "'"
        
        # Actually do the search.
        self.db.execute(query)
        data = self.db.fetchone()
        
        # Process the data.
        if data == None:
            result = None
        else:
            result = User()
            result.uid = item[0]
            result.user = item[1]
            result.pwHash = item[2]
            result.loadHostmasks(item[3])
            result.level = int(item[4])
            result.flags.toData(item[5])
            result.loadChannels(item[6])
        
        self.__closeDB()
        
        return result

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
    
    def __closeDB(self):
        '''Closes the user database.'''
        self.conn.commit()
        self.conn.close()
        self.conn = None

    def __convertWild(self, search):
        '''Converts a simple wildcard search into a regular expression.'''
        new = search.replace('.', "\.")
        new = new.replace('?',".?")
        new = new.replace('*',".*")
        return new

    def __initDB(self):
        '''Intended to initialize a database that doesn't yet exist.'''
        self.__openDB()
        
        initCmd = "CREATE TABLE IF NOT EXISTS users (uid TEXT PRIMARY KEY, user TEXT UNIQUE, password TEXT, hostmasks TEXT, level INTEGER, flags TEXT, channels TEXT)"
        
        self.db.execute(initCmd)
        
        self.__closeDB()

    def __openDB(self):
        '''Opens the user database up for use.'''
        self.conn = sqlite3.connect(self.database)
        self.db = self.conn.cursor()