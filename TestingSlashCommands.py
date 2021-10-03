import os
import ast
import discord
from dotenv import load_dotenv
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = ast.literal_eval(os.getenv('GUILD_IDS'))

client = discord.Client()
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print("Ready!")

@slash.slash(name="ping", guild_ids=GUILDS)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    await ctx.send(f"Pong! ({client.latency*1000}ms)")

@slash.slash(name="test1",
             description="This is just a test command, nothing more.", guild_ids=GUILDS)
async def test(ctx):
  await ctx.send(content="Hello World!")
	
@slash.slash(name="test2",
             description="This is just a test command, nothing more.",
             options=[
               create_option(
                 name="optone",
                 description="This is the first option we have.",
                 option_type=3,
                 required=False
               )
             ], guild_ids=GUILDS)
async def test(ctx, optone: str):
  await ctx.send(content=f"I got you, you said {optone}!")

@slash.slash(name="lookup",
             description="Look up a YACPDB entry by ID",
             options=[
               create_option(
                 name="id",
                 description="Input your ID after this",
                 option_type=3,
                 required=True
               )
             ], guild_ids=GUILDS)
async def lookup(ctx, id: int): # Defines a new "context" (ctx) command called "lookup"
    print("lookup: " + id)

        
    # turns on typing indicator
    #await message.channel.trigger_typing()
    # throw an error if problemid isn't an integer; else, get prettified problem as embed
    try: 
        await prettifiedProblemEmbed(id, message)
    except ValueError:
        await ctx.send('**WARNING**: Specified YACPDB problem ID "' + problemid + '" is not an integer! If this is a stipulation, perhaps you mean `y!newest ' + problemid + '` instead?')
        print(problemid)
    except UnboundLocalError:
        await ctx.send('**WARNING**: Something went wrong, but I\'m not sure what! Please report this to @edderiofer#0713!')
        print(problemid)
    except TimeoutError:    
        await ctx.send('**WARNING**: Timeout error. Please check that YACPDB isn\'t down, then try again.')    
    except urllib.error.URLError:    
        await ctx.send('**WARNING**: URL Error. Please check that YACPDB isn\'t down, then try again.')

  
client.run(TOKEN)
