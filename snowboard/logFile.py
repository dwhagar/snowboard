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
Object to handle logging output to a single log file.
'''

from os import makedirs
from os.path import isdir, abspath


class LogFile:
    def __init__(self, network, name, channel = False, pm = False):
        self.channel = channel
        self.file = None
        self.name = name.lower()
        self.path = "./logs/" + network + "/"
        self.pm = pm

        if self.channel:
            self.path += "channels/"
        elif self.pm:
            self.path += "messages/"

        if not isdir(self.path):
            makedirs(self.path, exist_ok = True)

        self.path = abspath(self.path)
        self.fileName = self.path + self.name + ".log"

    def writeLog(self, message):
        message += "\r\n"
        self.__open()
        self.file.write(message)
        self.__close()

    def __close(self):
        self.file.close()

    def __open(self):
        self.file = open(self.fileName, "a")
