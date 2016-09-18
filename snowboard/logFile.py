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

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

import time
from os import makedirs, remove
from os.path import isfile, isdir, abspath

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

        if not name == "motd":
            self.path += name
            self.name = time.strftime("%Y-%m-%d")

        if not isdir(self.path):
            makedirs(self.path, exist_ok = True)

        self.path = abspath(self.path)
        self.fileName = self.path + "/" + self.name + ".log"

        # Only keep one MOTD file.
        if self.name == "motd":
            if isfile(self.fileName):
                remove(self.fileName)

    def writeLog(self, message):
        message += "\r\n"
        self.open()
        self.file.write(message)
        self.close()

    def close(self):
        self.file.close()

    def open(self):
        self.file = open(self.fileName, "a")
