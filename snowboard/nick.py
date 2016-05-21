# Stores information about a nick.
class Nick:
    def __init__(self, nick, host = "", priv = None):
        self.nick = nick
        self.host = host
        self.priv = priv # NickPriv object
