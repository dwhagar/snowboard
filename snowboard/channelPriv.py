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
ChannelPriv class, provides a structure to store privileges of a single nick
on a particular channel.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

class ChannelPriv:
    '''
    Stores information about a single user on a single channel.

    Public Data Members:
        op:
            Boolean object, is the user opped or not?
        voice:
            Boolean object, is the user voiced or not?
        halfop:
            Boolean object, is the user halfopped or not?
    '''

    def __init__(self, isop = False, isvoice = False, ishalfop = False):
        self.op = isop
        self.voice = isvoice

        # TODO: Be able to process halfops!
        self.halfop = ishalfop
