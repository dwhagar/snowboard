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
Centralized place for flags to be granted based on user level, able to be
called by Nick and Channel objects.
'''

def grantFlags(level):
    '''Grant flags based on user level.'''
    flags = []
    
    if level == 255:
        flags.append("admin")
    if level >= 200:
        flags.append("usermanager")
    
    return flags