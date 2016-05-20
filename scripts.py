# Configuration file for scripts to be used and their triggers.

from test import *

# Run the scripts
def runScripts(raw):
    commands = []
    response = raw.split()
    message = " ".join(response[3:])
    message = message.strip(':')
    
    if response[1] == "PRIVMSG":
        commands = quitTest(message)
        
    return commands