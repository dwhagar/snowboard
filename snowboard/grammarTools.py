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

'''A series of tools handy for having the bot use better grammar.'''


def list2text(lst, word = "and"):
    '''Takes a list object and returns a sentence ready string.'''
    listLen = len(lst)
    if listLen > 0:
        if listLen == 1:
            text = lst[0]
        elif listLen == 2:
            text = " " + word + " ".join(lst)
        else:
            text = ", " + word + " ".join([", ".join(lst[:-1])] + lst[-1:])

    return text
