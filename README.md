# YACPBot
A repository for YACPBot, a Discord bot that posts problems from [YACPDB](https://www.yacpdb.org/).

# To run this:
1. Download the repository.
2. Put your environment variables into the `.env` file.
3. Make sure the bot has the right permissions in the Discord Developer Portal (see `Required Permissions.txt`), and invite it to any server necessary.
4. Run YACPBot.py.
5. Type /help in Discord to start things off.

# FAQ:
**Q: Why aren't you using FEN to store the positions/PGN to store the solutions?**

A: YACPBot doesn't just post orthodox chess problems. It also posts fairy problems with nonstandard pieces (e.g. Nightrider, Grasshopper, Camel), fairy conditions (e.g. Circe, Madrasi, Take & Make), and seriesmovers (where one side moves multiple times in a row). FEN and PGN simply aren't compatible with these sorts of problems. Further, YACPBot pulls from YACPDB, which already uses its own notation systems. It's fine, just leave it.

**Q: The diagrams look ugly! Can I have CBurnett or Merida pieces instead of Good Companion pieces?**

A: This is a consequence of the above. YACPDB's xfen-to-image converter is one of only two converters I know of that supports all the fairy pieces in YACPDB. The other one is janko.at, and it's harder to get working. If you know of any other chess position image converter that's compatible with fairy pieces and rotated pieces, please let me know.

**Q: Could you please add the ability for Discord users to solve the problem move by move (like with other Discord chess puzzle bots)?**

A: This is infeasible for the time being. The primary reason is that YACPDB is rather patchy when it comes to solution formatting; some problems in YACPDB don't even have a solution recorded, and many more have their solution recorded in the wrong format. Secondarily, this would require me to code up a way for the bot to choose Black's move, and probably to choose a refutation for Black if the user gives the wrong solution. Come back in a few years, when people have fixed the holes in YACPDB, and when I've gotten much better at programming, and then maybe I'll entertain this idea.

**Q: I'm having trouble understanding some of these stipulations.**

A: See "Planned future updates" below.

**Q: Your bot is slow!**

A: Yes, it unfortunately is. If you know how to make it faster, please let me know. Otherwise, 

**Q: Your bot's code is messy and amateurish!**

A: Yes, I'm an amateur coder. If you're willing to help improve my code at your own expense, please let me know.

# Planned future updates:
The following is a rough outline of planned future updates. This is not set in stone and very much subject to change.

v1.5: Add reaction-commands, so that users can delete the bot's responses to them.
v1.6: Prettify stipulations into more readable English (for the benefit of people who don't do chess problems very often).
v1.7: Fully implement `/search`, using reaction commands to page results.

v2.0: Transition the bot to a permanent host instead of running it off my own computer.
v2.1: Hook up the bot to cache YACPDB using something like MongoDB, to improve the speed of the bot.






