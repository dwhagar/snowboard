I'm running into a problem having the system join a channel.  The bot needs to wait until the MOTD and other things have been received before sending the command to join a channel.  So, to parse that, I'm going to need to create a message buffer for the system to process in main, probably a while loop to just keep dumping lines into the buffer, not sure exactly though.

I have to think about it.

So far, the code does not work at all.  It will join IRC but won't join the channels from the config file.