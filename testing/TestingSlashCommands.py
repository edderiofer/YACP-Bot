import os
import ast
import json
import discord
import urllib.request
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

# loads up environment variables like the Discord token and list of guild IDs
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# note: .env files don't support lists natively, so we have to use this code to turn the guild IDs into a list
GUILDS = ast.literal_eval(os.getenv('GUILD_IDS'))

client = discord.Client()
slash = SlashCommand(client, sync_commands=True)

# this and the next section prints to the command line that YACPBot is online and ready
@client.event
async def on_connect():
    print('YACPBot is online!')
    game = discord.Game("y!help")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_ready():
    print('YACPBot is ready!')


# gets the problem ID of the nth newest problem on YACPDB (if n < 1, clamps to 1)
# TODO: Add failsafe for if YACPDB has too few new problems for search (maybe load more latest edits (https://www.yacpdb.org/json.php?changes&p=2, https://www.yacpdb.org/json.php?changes&p=3, etc.) instead of just giving an error message?)
async def newProblemID(stip, n):
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?changes&p=1') as url:
        
        # loads JSON from https://www.yacpdb.org/json.php?changes&p=1 as a long dictionary, sifts through the "changes" array to find a problem with diff_len == 12 (indicates new problem and not edit to previous problem)
        data = json.loads(url.read().decode())
        changes = data.get("changes")
        
        # in case no such problem can be found, set problemid = 0
        problemid = 0
        i = 1
        for x in changes:
            # skip problems if a stipulation has been provided and the problem doesn't have that stipulation
            if not (stip == '-'):
                if not x.get("stipulation") == stip:
                    continue    
            # diff_len = 12 means that this is a new entry
            if x.get("diff_len") == '12':
                problemid = x.get("problem_id")

                # finds nth newest problem
                if i>=n:
                    break
                i += 1
    return problemid

# takes problem ID and info about y!newest/y!lookup commands, spits out a prettified embed of the problem in the channel where the command was run
async def prettifiedProblemEmbed(id, channel):
    id = str(id)
    print(id)
    print(str(type(id)))
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?entry&id='+id) as url:
        # sends a test ping to make sure this function is working(?)
        await channel.send("Ping!")

        # creates embed with title, link, and "test embed" as text
        embedVar = discord.Embed(title="TEST EMBED: YACPDB Problem >>"+id, description="test embed", url='https://www.yacpdb.org/#'+id)

        # sends embed
        await channel.send(embed=embedVar)

## NOTE TO ANYONE TRYING TO DEBUG THIS: The following two codeblocks (one for on_message(message) and one for newest(ctx) should have the same behaviour, but they don't and I don't understand why.

# main event loop
@client.event

# listens for new messages
async def on_message(message):
    # response to y!newest
    if message.content.startswith('y!newest'):
        print(message.content)
		
        # get new problem ID
        id = await newProblemID('-',0)
        print(id)
        print(str(type(id)))

        # send prettified problem as an embed
        await prettifiedProblemEmbed(id, message.channel)

	
@slash.slash(name="newest",
             description="Post the newest YACPDB problem",
             guild_ids=GUILDS)	
async def newest(ctx): # Defines a new "context" (ctx) command called "newest"
    print(ctx)

    # get new problem ID
    id = await newProblemID('-',0)
    #id = 549609
    print(id)
    print(str(type(id)))
    
    # await ctx.send('ping')

    # send prettified problem as an embed
    await prettifiedProblemEmbed(id, ctx)

		
client.run(TOKEN)
