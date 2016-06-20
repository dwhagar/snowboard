# snowboard
Project Snowboard - an IRC bot written in Python for the Modern IRC communities.

## Purpose
There are a lot of IRC bots out there but many of them are very old code, or working on an old code-base.  What this project aims to do is to provide a flexible bot that works with the modern IRC server, where services and such are common place.

We are writing this in Python because it allows everyone to make their own edits without the need to recompile.

## Current To Do
All we have right now is to-do, as we're just starting, so this is going to be pretty simple and not sound like a good bot until we get the basics in place and can really start expanding into different features.

* Self-Identify to NickServ on supported networks
** Leverage use of NickServ on supported networks
** NickServ or Q/X/Z ID Support for Ops
* Finish basic user management suite
** removeuser command
** modifyuser command
** searchusers command
* Basic channel management suite
** op/deop
** voice/devoice
** ban/unban
** kick
** invite

See Issues for more to-dos.

## Version History
v0.0.1 - Early pre-Alpha
* Unreleased version.
* Still not operational as a full-time bot.
* User Management under development.
** adduer command written
** listusers command written
* Connection self-managed.
* Timer framework in place.
* Scripting framework in place.
