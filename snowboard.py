#!/bin/env python3

# Snowboard - IRC Bot Written in Python 3
# See:  https://github.com/dwhagar/snowboard for more information.

import sys
import time
import telnetlib

# Import configuration files.
from config import *
from channels import *

# Global place to store the name of the server you're actually on.
SERVERNAME = ""

# Define a global message buffer.
MSGBUFF = []

# Send a message to the server.
# TODO - Implement sending queue here later
def serverSend(conn, message):
	print(message)
	message = message + "\n"
	conn.write(message.encode('utf-8'))
	return

# Retrieve a string from the server, one line at a time.
def serverLine(conn):
	line = conn.read_until('\r\n'.encode('utf-8'))
	print(line)
	line = line.decode('utf-8')
	line = line.strip(':')
	line = line.replace('\r','')
	line = line.replace('\n','')
	return line

# Join a channel.
def joinChannel(conn, chan):
	serverSend(conn, "JOIN " + chan)	
	return channel

# Get the users host from the server
def getHost(conn, name):
	# TODO, Need to implement
	pass

# Pase channel names from a server and return a list of Names
def parseNames(conn, raw):
	names = []
	responce = raw.split()
	responce = responce[4:]
	for name in responce:
		oped = False
		voiced = False
		
		name = name.strip(':')
		if name[0] == '@' or name[1] == '@':
			oped = True
			name.replace('@','')
		if name[0] == '+' or name[1] == '+':
			voiced = True
			name.replace('+','')
		
		#newHost = getHost(conn, name)
		newNick = Nick(name)
		newNick.setOp(oped)
		newNick.setVoice(voiced)
		
		names.append(newNick)
		
	return names

# Connect to the server.
# TODO - Error handling needs to be done
def serverConnect():
	# Open the initial connection.
	conn = telnetlib.Telnet(SERV, port=SERVPORT)

	temp = conn.read_until(b'\r\n').split()
	SERVERNAME = conn.read_until(b'\r\n').split()[0][1:].decode('utf-8')

	# Log into IRC
	nickLine = "NICK " + BOTNICK
	userLine = "USER " + BOTNICK + " 0 * :" + REALNAME
	
	serverSend(conn, nickLine)
	serverSend(conn, userLine)
		
	return conn

# Disconnect from the server properly.
def serverDisconnect(conn):
	quitLine = "QUIT :" + QUITMSG
	serverSend(conn, quitLine)
	conn.close()
	return

# Join the configured channels.
def joinChannels(conn):
	channels = []
	for chan in BOTCHANS:
		joinChannel(conn, chan)
	return channels
	
def main(args):
	result = 0	# Define a result value, so we can pass it back to the shell
	
	# Open the initial connection.
	conn = serverConnect()
	channels = joinChannels(conn)
	nothing = input(":")
	serverDisconnect(conn)
	
	return result

main(sys.argv)