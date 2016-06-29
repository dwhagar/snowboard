# snowboard
Project Snowboard - an IRC bot written in Python for the Modern IRC communities.

## Purpose
There are a lot of IRC bots out there but many of them are very old code, or working on an old code-base.  What this project aims to do is to provide a flexible bot that works with the modern IRC server, where services and such are common place.

We are writing this in Python because it allows everyone to make their own edits without the need to recompile.

## Current To Do
All we have right now is to-do, as we're just starting, so this is going to be pretty simple and not sound like a good bot until we get the basics in place and can really start expanding into different features.

* Leverage use of NickServ on supported networks
 * Try to use ChanServ/NickServ to help identify users (not sure how this would work)
* Auto-Request Ops from ChanServ or Q/X/Z
* Finish basic user management suite
 * searchusers
 * whoami (to get ones own username)
 * whois (to get the username of a nick)
 * ident support for unrecognized host (username/password authe)
* Basic channel management suite
 * op/deop
 * voice/devoice
 * ban/unban
 * kick
 * invite
 * topic keeper
* learn module
* seen module

## Version History
v0.0.2 - Early pre-Alpha
* Unrelased version.
* Identifies self to NickServ.
* Finished moduser commands.
 * level
  * Can be used with channel permissions.
 * password
 * addhosts / delhosts / sethosts
 * addflags / delflags / setflags
  * Can be used with channel permissions.
 * rmchan
* userinfo supports channels
* listusers supports channels

v0.0.1 - Early pre-Alpha
* Unreleased version.
* Still not operational as a full-time bot.
* User Management under development.
 * adduer command written
 * ident command written
 * deluser command written
 * listusers command written
 * moduser command written
* New quit command written
* Sever and CTCP Ping Support
* Ping request support ('pingme' / 'ping me' command)
* Connection self-managed.
* Timer framework in place.
* Scripting framework in place.
* Complete rewrite of database architecture
