import os
import ast
import sys
import json
import discord
import urllib.request
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

# this is to make sure that any olive-gui functions i call work properly; it's crude and will almost certainly break at some point, but i don't know any other solution
sys.path.append(os.path.join(os.path.dirname(__file__), 'olive_gui_master'))

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

# converts piece from algebraic list format to XFEN
async def AlgToXFEN(alg, channel):
    # start with an array of 1s, then get the piece coordinates and write them to the array one by one
    position = [[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]

    # set "valid position?" flag (immediately halts this process if this flag turns out to be false)
    valid = True

    # matrix of pieces (alg -> XFEN)

    piecesMatrix = {
        '15':'s3', '16':'s3', '24':'s3', '25':'s3', '35':'s3', '36':'s3', '37':'s3', 'al':'b3', 'am':'a', 'an':'s1', 'ao':'s1',
        'ar':'b2', 'b':'b', 'b1':'o', 'b2':'o', 'b3':'o', 'be':'o', 'bh':'b2', 'bi':'o', 'bk':'s1', 'bl':'b3', 'bm':'o',
        'bn':'s2', 'bo':'o', 'bp':'p2', 'br':'o', 'bs':'p2', 'bt':'o', 'bu':'s1', 'bw':'o', 'c':'b1', 'ca':'s3', 'cg':'q1',
        'ch':'s3', 'cp':'p3', 'cr':'s3', 'ct':'o', 'cy':'o', 'da':'r1', 'db':'b1', 'dg':'q1', 'dk':'r1', 'do':'q3', 'dr':'o',
        'ds':'o', 'du':'p1', 'ea':'q3', 'eh':'q1', 'ek':'o', 'em':'r2', 'eq':'e', 'et':'o', 'f':'o', 'fe':'b3', 'fr':'o',
        'g':'q2', 'g2':'q1', 'g3':'q3', 'ge':'o', 'gf':'o', 'gh':'s1', 'gi':'s1', 'gl':'o', 'gn':'s1', 'gr':'o', 'gt':'o',
        'ha':'q3', 'k':'k', 'ka':'q3', 'kl':'q3', 'kh':'k2', 'kl':'q1', 'ko':'o', 'kp':'s2', 'l':'q1', 'lb':'b1', 'le':'q3',
        'lh':'o', 'li':'q3', 'ln':'s1', 'lr':'r1', 'ls':'f', 'm':'o', 'ma':'s1', 'mg':'o', 'mh':'o', 'ml':'o', 'mm':'o',
        'mo':'s3', 'mp':'p3', 'ms':'s3', 'n':'s2', 'na':'s3', 'nd':'b3', 'ne':'e', 'nh':'s3', 'nl':'s3', 'o':'o', 'oa':'s1',
        'ok':'o', 'or':'e1', 'p':'p', 'pa':'r3', 'po':'k3', 'pp':'p2', 'pr':'b2', 'q':'q', 'qe':'e', 'qf':'e', 'qn':'o',
        'qq':'o', 'r':'r', 'ra':'o', 'rb':'b3', 're':'r1', 'rf':'o', 'rh':'r2', 'rk':'o', 'rl':'r3', 'rm':'r1', 'rn':'f',
        'rp':'f', 'ro':'f', 'rr':'o', 'rt':'q1', 'rw':'o', 's':'s', 's1':'s2', 's2':'s2', 's3':'s2', 's4':'s2', 'sh':'o',
        'si':'q3', 'sk':'a', 'so':'o', 'sp':'p1', 'sq':'o', 'ss':'o', 'sw':'o', 'th':'o', 'tr':'r3', 'uu':'o', 'va':'b3',
        'wa':'o', 'we':'r2', 'wr':'o', 'z':'s3', 'zh':'o', 'zr':'s1', 'ze':'o', 'ms':'s3',
        'fa':'r1','se':'q1','sa':'s1','lo':'b1'
    };
    
    
    # getting white piece coordinates
    White = alg.get("white")
    for x in White:
        piece = x[0:len(x)-2].lower()
        
        file = ord(x[-2]) - 97
        # WARNING: Remember to turn "10" back into "8" here.
        rank = 8 - int(x[-1])
        
        # convert piece into XFEN piece format
        try:
            piece = piecesMatrix[piece].upper()
        except KeyError:
            await channel.send("Warning: Piece 'white " + piece + "' in diagram not recognised. Replacing with 'x'.")
            piece = 'x'
        # bracket piece if multiple characters long
        if len(piece) > 1:
            piece = "(" + piece + ")"
        
        # replacing 1s with pieces
        try:
            position[rank][file] = piece
        # throw an error if the board is somehow NOT an 8x8 board
        except IndexError: 
            await channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started s upporting non-8x8 boards.")
            valid = False
            break

        #ditto for black
    if valid:
        Black = alg.get("black")
        for x in Black:
            piece = x[0:len(x)-2].lower()
            
            file = ord(x[-2]) - 97
            rank = 8 - int(x[-1])
            
            try:
                piece = piecesMatrix[piece].lower()
            except KeyError:
                await channel.send("Warning: Piece 'black " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            if len(piece) > 1:
                piece = "(" + piece + ")"
                
            try:
                position[rank][file] = piece
            except IndexError: 
                await channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
                valid = False
                break

        #ditto for neutral
    if valid and alg.get("neutral"):
        Neutral = alg.get("neutral")
        for x in Neutral:
            piece = x[0:len(x)-2].lower()
            file = ord(x[-2]) - 97
            rank = 8 - int(x[-1])
            try:
                piece = '!' + piecesMatrix[piece].lower()
            except KeyError:
                await channel.send("Warning: Piece 'neutral " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            if len(piece) > 1:
                piece = "(" + piece + ")"
            try:
                position[rank][file] = piece
            except IndexError: 
                await channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
                valid = False
                break
        
    if not valid:
        FEN = '8/8/8/8/8/8/8/8'
    else:
        # concatenates the board into a FEN-like string (maybe with lines of 1s)
        for i in range(8):
            position[i] = ''.join(str(x) for x in position[i])
            #print(position[i])
        FEN = '/'.join(str(x) for x in position)
    
        # cleans up lines of 1s in case some program decides that "11" is to be read as "eleven" and not "one, one"
        for i in range(8,1,-1):
            FEN=FEN.replace('1'*i,str(i))
    return(FEN)
    
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
    
    
# takes date as dict, returns prettified date as string
async def prettifyDate(date):

    #if date is blank, return date
    if date == '': return date

    #otherwise return date in d/m/y form as far as these exist
    if date.get('year'):
        prettyDate = str(date.get('year'))
        if date.get('month'):
            prettyDate = str(date.get('month')) + "/" + prettyDate
            if date.get('day'):
                prettyDate = str(date.get('day')) + "/" + prettyDate
    
    try:
        return prettyDate
	#otherwise throw some error if the date is invalid (not sure why it ever would be though)
    except UnboundLocalError:
        print('INVALID DATE ERROR')
        return 'INVALID DATE ERROR'

# takes tourney as dict, returns prettified tourney as string 
async def prettifyTourney(tourney):
    print(tourney)
    if not tourney: return ''
    if tourney == 'ditto': return 'ditto'
    if tourney.get('name'):
        prettyTourney = str(tourney.get('name'))
        if tourney.get('date'):
            prettyTourney = prettyTourney + ", " + await prettifyDate(tourney.get('date'))
    try:
        return prettyTourney
    except UnboundLocalError:
        print('INVALID TOURNEY ERROR')
        return 'INVALID TOURNEY ERROR'

# takes problem ID, returns any error keywords
async def prettifyKeywords(keywords):
    print(keywords)
    if not keywords: return ''
    errorWords = []
    badKeywords = ["Cooked", "Attention", "To delete", "No solution", "Unsound", "Shortmate", "Position?", "Stipulation?", "Source?", "Plagiarism?", "Name?", "Wrong diagram?", "Twins?", "Author?"]
    for x in keywords:
        if x in badKeywords:
            errorWords.append(x)
    print(errorWords)
    return errorWords

# takes problem ID and info about y!newest/y!lookup commands, spits out a prettified embed of the problem in the channel where the command was run
async def prettifiedProblemEmbed(id, channel):
    id = str(id)
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?entry&id='+id) as url:
        
        # gets data about the problem (TODO: Add fairy condition support, e.g. >>1015 >>258194 for testing)
        data = json.loads(url.read().decode())
        # print("data = " + str.(data))
        try:
            ash = data.get('ash') + '1'
        except TypeError:
            await channel.send('Problem ID not found. If you performed y!lookup, please ensure the problem is in the database. If you performed y!newest, something has gone horribly wrong with this bot\'s code.')

        # gets authors; if multiple authors, then concatenate into a string with each author on its own line
        authorsArray = data.get('authors')
        try:
            authors = '\n'.join("**" + str(x) + "**" for x in authorsArray)
        except Exception:
            authors = "**WARNING: AUTHOR UNKNOWN**"
        authors = authors + "\n"
        # print(authors)

        # finds source and spits it out as a dictionary; if it doesn't exist, indicates so
        if data.get('source'):
            sourceDict = data.get('source')
            sourcedate = sourceDict.get('date')
            sourcedate = await prettifyDate(sourcedate)
            print(sourcedate)
        else:
            sourceDict = {"name":"Source Unknown Or Not Added"}
        # DEBUG PURPOSES
        # print(sourceDict)
        if sourceDict.get('date'):
            sourceDict['date'] = sourcedate
        
        # concatenates dictionary into a string, hopefully
        source = ', '.join(str(sourceDict.get(x)) for x in sourceDict) + '\n'
        
        # finds awards and spits them out as a dictionary
        if data.get('award'):
            awardDict = data.get('award')
        else:
            awardDict = {}
        tourneyDict = awardDict.get('tourney')
        tourney = await prettifyTourney(tourneyDict)
        if tourney == 'ditto':
            tourney = source
        # DEBUG PURPOSES
        print(awardDict)
        print(tourney)
        # concatenates dictionary into a string, hopefully (TODO: Tinker with this so that subdictionaries like "date" don't break)
        if awardDict:
            awardDict['tourney'] = tourney
            award = ', '.join(str(awardDict.get(x)) for x in awardDict) + '\n\n'
        else:
            award = '\n'
            
        if data.get('keywords'):
            keywordsArray = data.get('keywords')
            badWordsArray = await prettifyKeywords(keywordsArray)
            if badWordsArray:
                keywords = 'Bad Keywords: ' + ', '.join("**" + str(x) + "**" for x in badWordsArray) + '\n\n'
            else:
                keywords = ''
        else:
            keywords = ''
        
        # gets stipulation and no. of solutions (if multiple)
        stip = data.get('stipulation')

        # tacks on no. of intended solutions, if multiple (replacing * with \* is required due to Discord formatting)
        if data.get('intended-solutions'):
            intendedSols = str(data.get('intended-solutions')) + ' solutions'
            stip = "**" + stip.replace("*", "\*") + ", " + intendedSols + "**\n"
        # else doesn't tack anything on
        else:
            stip = "**" + stip.replace("*", "\*") + "**\n"
        
        # gets options (e.g. duplex)
        if data.get('options'):
            optionsArray = data.get('options')
            options = ', '.join("" + str(x) + "" for x in optionsArray)
            options = options + "\n"
        else:
            options = ''
        
        # gets legend (piece names)
        if data.get('legend'):
            legendDict = data.get('legend')
            print(legendDict)
            for x in legendDict:
                legendDict[x] = ", ".join(legendDict[x])
            legend = ',\n'.join("**" + x + "**: " + str(legendDict.get(x)) for x in legendDict)
            legend = legend + "\n"
        else:
            legend = ''

        # gets twins
        if data.get('twins'):
            twinsDict = data.get('twins')
            twins = '\n'.join(x + ") " + str(twinsDict.get(x)) + "" for x in twinsDict)
        else:
            twins = ''
        
        # gets solution
        solution = data.get('solution')
        # calls parser
        from p2w.parser import parser
        try:
            solution = parser.parse(data["solution"], debug=0)
            solutionWarning = ""
        except Exception as ex:
          # we could not parse it, write id to file
          solutionWarning = "\n\
            **WARNING! Problem's solution is not in Popeye Output Format! Please edit the entry accordingly.**\
			\n"

        # converts position from algebraic into FEN
        position = data.get("algebraic")
        # FEN = await AlgToFEN(position, channel)
        XFEN = await AlgToXFEN(position, channel)

        # creates embed with title, author, source, stipulation, and position as image (NOTE: Doesn't really seem possible to increase image size. :C)
        embedVar = discord.Embed(title="YACPDB Problem >>"+id, description=\
                                authors + source\
                                + award\
                                + keywords\
                                + stip\
                                + options\
                                + legend\
                                + twins\
                                + solutionWarning\
                                , url='https://www.yacpdb.org/#'+id)
        # embedVar.set_image(url='https://www.janko.at/Retros/d.php?ff='+FFEN)
        embedVar.set_image(url='https://yacpdb.org/xfen/?'+XFEN)

        # sends embed
        await channel.send(embed=embedVar)

# main event loop
@client.event

# listens for new messages
async def on_message(message):

    # response to y!lookup
    if message.content.startswith('y!lookup'):
        print(message.content)

        
        # turns on typing indicator
        await message.channel.trigger_typing()

        # splits y!lookup messages into command + arguments
        input = message.content
        input = input.split()
        # DEBUG PURPOSES
        print(input)

        # pass yacpdb ID to other functions (if doesn't exist, throw error)
        try:    
            if len(input) == 1:    
                await message.channel.send('**WARNING**: No YACPDB problem ID specified. Syntax is `y!lookup [problem id]`.')    
        # else send prettified problem as an embed    
            else:
                problemid = str(input[1])
                # throw an error if problemid isn't an integer; else, get prettified problem as embed
                try: 
                    int(str(input[1]))
                    await prettifiedProblemEmbed(problemid, message.channel)
                except ValueError:
                    await message.channel.send('**WARNING**: Specified YACPDB problem ID "' + problemid + '" is not an integer! If this is a stipulation, perhaps you mean `y!newest ' + problemid + '` instead?')
                    print(problemid)
                except UnboundLocalError:
                    await message.channel.send('**WARNING**: Something went wrong, but I\'m not sure what! Please report this to @edderiofer#0713!')
                    print(problemid)
        except TimeoutError:    
            await message.channel.send('**WARNING**: Timeout error. Please check that YACPDB isn\'t down, then try again.')    
        except urllib.error.URLError:    
            await message.channel.send('**WARNING**: URL Error. Please check that YACPDB isn\'t down, then try again.')    
    
    # response to y!newest
    if message.content.startswith('y!newest'):
        print(message.content)
        
        # turns on typing indicator
        await message.channel.trigger_typing()
		
        # get new problem
        problemid = await newProblemID('-',0)

        # throw error if no new problems
        if problemid == 0:
            await message.channel.send('**Warning: no new problems matching stipulation `' + stip + '` found in the last 100 edits to YACPDB.**')

        # else send prettified problem as an embed
        else:
            await prettifiedProblemEmbed(problemid, message.channel)

	
@slash.slash(name="newest",
             description="Post the nth newest YACPDB problem with a given stipulation",
             guild_ids=GUILDS)	
async def newest(ctx): # Defines a new "context" (ctx) command called "newest"
        
    # turns on typing indicator
    await ctx.channel.trigger_typing()
    # throw an error if problemid isn't an integer; else, get prettified problem as embed
    try: 
        id = int(await newProblemID('-',0))
        #id = 549319
        print(id)
        print(str(type(id)))
        # await ctx.send('ping')
        if id == 0:
            await ctx.channel.send('**Warning: no new problems matching stipulation `' + stip + '` found in the last 100 edits to YACPDB.**')
        else:
            print("Pre-success!")
            await prettifiedProblemEmbed(id, ctx)
            print("Success!")
	
	
	
		
client.run(TOKEN)
