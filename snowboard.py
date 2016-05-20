#!/bin/env python3

# Snowboard - IRC Bot Written in Python 3
# See:  https://github.com/dwhagar/snowboard for more information.

import sys
import time
import telnetlib

# Import configuration files.
from config import *
from channels import *
from scripts import *

# Global place to store the name of the server you're actually on.
SERVERNAME = ""

# Send a message to the server.
# TODO - Implement sending queue here later
def serverSend(conn, message):
	print(message)
	message = message + "\n"
	conn.write(message.encode('utf-8'))
	return

# Retrieve a string from the server, one line at a time.
def serverLine(conn):
	try:
		line = conn.read_until('\r\n'.encode('utf-8'))
	except:
		return False
		
	line = line.decode('utf-8')
	line = line.strip(':')
	line = line.replace('\r','')
	line = line.replace('\n','')
	return line

# Join a channel.
def joinChannel(conn, chan):
	serverSend(conn, "JOIN " + chan)	
	channel = Channel(chan)
	return channel

# Get the users host from the server
def getHost(conn, name):
	# TODO, Need to implement
	pass

# Pase channel names from a server and return a list of Names
def parseNames(conn, raw):
	names = []
	response = raw.split()
	response = response[5:]
	for name in response:
		oped = False
		voiced = False
		
		name = name.strip(':')
		if name[0] == '@' or name[1] == '@':
			oped = True
			name = name.replace('@','')
		if name[0] == '+' or name[1] == '+':
			voiced = True
			name = name.replace('+','')
		
		#newHost = getHost(conn, name)
		newNick = Nick(name)
		newNick.setOp(oped)
		newNick.setVoice(voiced)
		
		names.append(newNick)
		
		serverSend(conn, "WHO " + name)
		
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
	connected = False
	conn = serverConnect()
	message = serverLine(conn)
	
	while not connected:
		response = message.split()
		if response[1] == "396":
			connected = True
		
		message = serverLine(conn)
	
	# Join all the configured channels.
	channels = joinChannels(conn)
	
	# Process IRC messages.
	while connected:
		message = serverLine(conn)
		if message == False:
			connected = False
			continue
		
		response = message.split()
		
		#print(message)
		
		# Process WHO responses to get hostnames.
		if response[1] == "352":
			for channel in channels:
				for name in channel.names:
					if name.nick.lower() == response[4].lower():
						name.setHost(response[5])
		# Process NAMES responses to get all names for channels joined.
		elif response[1] == "353":
			names = parseNames(conn, message)
			for channel in channels:
				if channel.name.lower() == response[4].lower():
					channel.updateNames(names)
		elif response[0] == "PING":
			serverSend(conn, "PONG " + response[1])
		
		# Get the list of commands to perform from the scripts
		commands = runScripts(message)

		# Execute commands
		for command in commands:
			if command == "*QUIT*":
				serverDisconnect(conn)
			else:
				serverSend(conn, commands)
	
	# Disconnect
	conn.close()
	
	# Print the message about disconnection.
	print("Disconnected from the server.")
	
	return result

main(sys.argv)