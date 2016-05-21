import telnetlib

class Connection:
    """Connection context manager.
    
    The `telnetlib.Telnet` class does not support the context manager before
    Python 3.6. This is a bummer. To remedy that, this is a simply wrapper
    class that turns `telnetlib.Telnet` into a context manager.
    
    To use, simply convert:
        conn = telnetlib.Telnet("irc.server.net")
        # do stuff with conn
        conn.close()
    to:
        with Connection("irc.server.net") as conn:
                # do stuff with conn
    """
     
    def __init__(self, server, port=6667):
        """Prepare connection.
        """
        self._server = server
        self._port   = port
        
        self._conn = None
    
    def __enter__(self):
        """Connect to a server.
        """
        self._conn = telnetlib.Telnet(self._server, port=self._port)
        return self._conn
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close server connection.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None
