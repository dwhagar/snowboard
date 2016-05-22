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

from . import connection
from . import config
from . import channel
from . import nick

class Network:
    def __init__(self, name, cfg):
        self.name = name
        self.config = cfg
        self.__connection = None
        self.channels = []
        self.nicks = []
        
    def connect(self):
        for server in self.config.servers:
            self.__connection.ssl = server.ssl
            self.__connection.sslVerify = self.config.sslVerify
            self.__connection(server)
            self.__connection.connect()