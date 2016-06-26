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
Useful functions for dealing with passwords.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import hashlib
import base64

def passwordHash(password):
    '''Creates a base64 encoded hash from a password.'''
    sha512 = hashlib.sha256()
    sha512.update(password.encode('utf-8'))
    data = sha512.digest()
    result = base64.b64encode(data).decode('utf-8')
    return result