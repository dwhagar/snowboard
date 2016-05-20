# Scripts for testing...

def quitTest(message):
	print(message)
	commands = []
	if message == "quit now":
		commands.append("*QUIT*")
	return commands