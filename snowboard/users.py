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
shall be the sha512 hashed and base64 converted password.

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

class Users:
    def __init__(self, network, table = "global"):
        self.network = network
        self.database = network + "-users.db"
        self.table = table
        
        initDB() # Make sure there is a database and it has the table.

    def initDB(self):
        '''Intended to initialize a database that doesn't yet exist.'''
        conn = sqlite3.connect(self.database)
        c = conn.cusor()
        
        initCmd = "CREATE TABLE IF NOT EXISTS" + self.table + " (uid TEXT PRIMARY KEY, user TEXT, password BLOB, hostmasks TEXT, level INTEGER, approved TEXT, denied TEXT")
        
        c.execute(initCmd)
        
        conn.commit()
        conn.close()
        
    def uidHash(self, name)
        # Create the has.
        sha = hashlib.sha1()
        sha.update(name)
        sha.update(self.network)
        data = sha.digest()
        
        # Encode it for storage as a string.
        result = base64.b64encode(data)
        
        return result