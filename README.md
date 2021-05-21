# AChannel

## Purpose

**AChannel** helps you customize a bit more your voice channels dedicated to a specific activity. 
The point is to create an **auto-channel** that will create a sub voice channel upon connection and move the user on it.
The name of the sub voice channel is chosen **randomly** among the list the user gave for this auto-channel (see **add** or **add-f** command).

## Commands

* `help ["command"]`
  
  Display general help, or help for a command.

* `create "auto-channel(s)"`
  
  **Administrator**
  
  Create one or several auto-channels. The auto-channel and the sub voice channel created cannot be seen unless the user possess the role associated.
  A role associated to the auto-channel is created in the process.

* `delete "auto-channel(s)"`

  **Administrator**

  Delete one or several auto-channels. The auto-channel will be erased along with the names the users gave and the role associated.

* `add "auto-channel" "channel_name(s)"`

  **Administrator**

  Add voice channel names for an auto-channel.

* `add-f "auto-channel"`
  
  **Administrator**

  Same thing than add but you can create a text file that has a name for the auto-channel per line. 

* `list-ac`

  List all auto-channels inside the guild.

* `list-cn "auto-channel"`

  List all voice channel names for an auto-channel.

* `join "role"`

  Join a role associated to an auto-channel.

## Warnings

* The bot is designed in a way that you cannot add a voice channel **permanently** inside the category created. If all users connected disconnects from it then it will be deleted.

## Resources

* [Discord py](https://discordpy.readthedocs.io/en/stable/)

* [Pipenv](https://pypi.org/project/pipenv/)
