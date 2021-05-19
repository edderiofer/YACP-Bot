# bot.py

### TODO LIST:
#   * Allow bot to handle fairy/rotated pieces. (Big problem right now is that there's no canonical mapping from piece abbreviations (what YACPDB uses in "algebraic") to FFEN piece options. Dmitri might need to update API to also show the FEN below, or you might need to scrape the webpage to get the FEN and modify it to FFEN. For now, I've just added an error message.)
#   * Fix up dateDict in sourceDict not displaying correctly.
#   * Add failsafe for if YACPDB has too few new problems for search (maybe load more latest edits?)
#   * Add ability to search YACPDB. (This may require work on Dmitri's part to extend the API. Currently at the halfway point of looking through Newest Edits, and returning the nth problem with a given stipulation)

import random
import os
import json
import discord
import urllib.request
import xfen2img
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_connect():
    print('{client} is online!')
    game = discord.Game("y!help")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_ready():
    print('{client} is ready!')

# converts piece from algebraic list format to FEN
async def AlgToFFEN(alg, message):
    # start with an array of 1s, then get the piece coordinates and write them to the array one by one
    position = [[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]

    # set "valid position?" flag (immediately halts this process if this flag turns out to be false)
    valid = True

    # matrix of pieces (alg -> FFEN)

    piecesMatrix = {
        '15':'*3n', '16':'*3n', '24':'*3n', '25':'*3n', '35':'*3n', '36':'*3n', '37':'*3n', 'al':'*3b', 'am':'t', 'an':'*1n', 'ao':'*1n', 'ar':'*2b', 'b':'b', 'b1':'c', 'b2':'c', 'b3':'c', 'be':'c', 'bh':'*2b', 'bi':'c', 'bk':'*1n', 'bl':'*3b', 'bm':'c', 'bn':'*2n', 'bo':'c', 'bp':'*2p', 'br':'c', 'bs':'*2p', 'bt':'c', 'bu':'*1n', 'bw':'c', 'c':'*1b', 'ca':'*3n', 'cg':'*1q', 'ch':'*3n', 'cp':'*3p', 'cr':'*3n', 'ct':'c', 'cy':'c', 'da':'*1r', 'db':'*1b', 'dg':'*1q', 'dk':'*1r', 'do':'*3q', 'dr':'c', 'ds':'c', 'du':'*1p', 'ea':'*3q', 'eh':'*1q', 'ek':'c', 'em':'*2r', 'eq':'s', 'et':'c', 'f':'c', 'fe':'*3b', 'fr':'c', 'g':'*2q', 'g2':'*1q', 'g3':'*3q', 'ge':'c', 'gf':'c', 'gh':'*1n', 'gi':'*1n', 'gl':'c', 'gn':'*1n', 'gr':'c', 'gt':'c', 'ha':'*3q', 'k':'k', 'ka':'*3q', 'kl':'*3q', 'kh':'*2k', 'kl':'*1q', 'ko':'c', 'kp':'*2n', 'l':'*1q', 'lb':'*1b', 'le':'*3q', 'lh':'c', 'li':'*3q', 'ln':'*1n', 'lr':'*1r', 'ls':'x', 'm':'c', 'ma':'*1n', 'mg':'c', 'mh':'c', 'ml':'c', 'mm':'c', 'mo':'*3n', 'mp':'*3p', 'ms':'*3n', 'n':'*2n', 'na':'*3n', 'nd':'*3b', 'ne':'s', 'nh':'*3n', 'nl':'*3n', 'o':'c', 'oa':'*1n', 'ok':'c', 'or':'*1s', 'p':'p', 'pa':'*3r', 'po':'*3k', 'pp':'*2p', 'pr':'*2b', 'q':'q', 'qe':'s', 'qf':'s', 'qn':'c', 'qq':'c', 'r':'r', 'ra':'c', 'rb':'*3b', 're':'*1r', 'rf':'c', 'rh':'*2r', 'rk':'c', 'rl':'*3r', 'rm':'*1r', 'rn':'x', 'rp':'x', 'ro':'x', 'rr':'c', 'rt':'*1q', 'rw':'c', 's':'n', 's1':'*2n', 's2':'*2n', 's3':'*2n', 's4':'*2n', 'sh':'c', 'si':'*3q', 'sk':'t', 'so':'c', 'sp':'*1p', 'sq':'c', 'ss':'c', 'sw':'c', 'th':'c', 'tr':'*3r', 'uu':'c', 'va':'*3b', 'wa':'c', 'we':'*2r', 'wr':'c', 'z':'*3n', 'zh':'c', 'zr':'*1n', 'ze':'c', 'ms':'*3n', 'fa':'*1r', 'se':'*1q', 'sa':'*1n', 'lo':'*1b'
    }
    
    
    # getting white piece coordinates (TODO: revamp this to handle fairy/rotated pieces)
    White = alg.get("white")
    for x in White:
        piece = x[0:len(x)-2].lower()
        
        file = ord(x[-2]) - 97
        # WARNING: Remember to turn "10" back into "8" here.
        rank = 8 - int(x[-1])
        
        # convert piece into FFEN piece format
        try:
            piece = piecesMatrix[piece].upper()
        except KeyError:
            await message.channel.send("Warning: Piece 'white " + piece + "' in diagram not recognised. Replacing with 'x'.")
            piece = 'x'

        # check to make sure there aren't any fairy pieces, throw an exception if there are
        # if not piece in ['K','Q','R','B','S','P']:
            # await message.channel.send("Either something has gone VERY wrong with the code, or this problem contains a fairy piece!")
            # valid = False
            # break
        # convert S to N (aarrghhh inconsistent piece notation!)
        # if piece == 'S': piece = 'N'
		
        # replacing 1s with pieces
        try:
            position[rank][file] = piece
        # throw an error if the board is somehow NOT an 8x8 board
        except IndexError: 
            await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started s upporting non-8x8 boards.")
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
                await message.channel.send("Warning: Piece 'black " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            # if not piece in ['k','q','r','b','s','p']:
                # await message.channel.send("Either something has gone VERY wrong with the code, or this problem contains a fairy piece!")
                # valid = False
                # break
            # if piece == 's': piece = 'n'
            try:
                position[rank][file] = piece
            except IndexError: 
                await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
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
                piece = '-' + piecesMatrix[piece].lower()
            except KeyError:
                await message.channel.send("Warning: Piece 'neutral " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            # if not piece in ['k','q','r','b','s','p']:
                # await message.channel.send("Either something has gone VERY wrong with the code, or this problem contains a fairy piece!")
                # valid = False
                # break
            # if piece == 's': piece = 'n'
            try:
                position[rank][file] = piece
            except IndexError: 
                await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
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

# converts piece from algebraic list format to XFEN
async def AlgToXFEN(alg, message):
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
            await message.channel.send("Warning: Piece 'white " + piece + "' in diagram not recognised. Replacing with 'x'.")
            piece = 'x'
        # bracket piece if multiple characters long
        if len(piece) > 1:
            piece = "(" + piece + ")"
		
        # replacing 1s with pieces
        try:
            position[rank][file] = piece
        # throw an error if the board is somehow NOT an 8x8 board
        except IndexError: 
            await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started s upporting non-8x8 boards.")
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
                await message.channel.send("Warning: Piece 'black " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            if len(piece) > 1:
                piece = "(" + piece + ")"
                
            try:
                position[rank][file] = piece
            except IndexError: 
                await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
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
                await message.channel.send("Warning: Piece 'neutral " + piece + "' in diagram not recognised. Replacing with 'x'.")
                piece = 'x'
            if len(piece) > 1:
                piece = "(" + piece + ")"
            try:
                position[rank][file] = piece
            except IndexError: 
                await message.channel.send("The board is not 8x8! Either something has gone VERY wrong with the code, or YACPDB has started supporting non-8x8 boards.")
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
                if i>=n:break
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

# takes problem ID and info about !problem/!lookup commands, spits out a prettified embed of the problem in the channel where the command was run
async def prettifiedProblemEmbed(id, message):
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?entry&id='+id) as url:
        
        # gets data about the problem (TODO: Add fairy condition support, e.g. >>1015 >>258194 for testing)
        data = json.loads(url.read().decode())

        # gets authors; if multiple authors, then concatenate into a string with each author on its own line
        authorsArray = data.get('authors')
        authors = '\n'.join("**" + str(x) + "**" for x in authorsArray)
        authors = authors + "\n"

        # finds source and spits it out as a dictionary; if it doesn't exist, indicates so
        if data.get('source'):
            sourceDict = data.get('source')
        else:
            sourceDict = {"name":"Source Unknown Or Not Added"}
        sourcedate = sourceDict.get('date')
        sourcedate = await prettifyDate(sourcedate)
        # DEBUG PURPOSES
        print(sourceDict)
        print(sourcedate)
        if sourceDict['date']: sourceDict['date'] = sourcedate
        
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
        awardDict['tourney'] = tourney
        # concatenates dictionary into a string, hopefully (TODO: Tinker with this so that subdictionaries like "date" don't break)
        if awardDict:
            award = ', '.join(str(awardDict.get(x)) for x in awardDict) + '\n\n'
        else:
            award = '\n'
        
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

        # converts position from algebraic into FEN
        position = data.get("algebraic")
        # FEN = await AlgToFEN(position, message)
        FFEN = await AlgToFFEN(position, message)
        XFEN = await AlgToXFEN(position, message)

        # creates embed with title, author, source, stipulation, and position as image (NOTE: Doesn't really seem possible to increase image size. :C)
        embedVar = discord.Embed(title="YACPDB Problem >>"+id, description=\
                                authors + source\
                                + award\
                                + stip\
                                + options\
                                + legend\
                                + twins\
                                , url='https://www.yacpdb.org/#'+id)
        # embedVar.set_image(url='https://www.janko.at/Retros/d.php?ff='+FFEN)
        embedVar.set_image(url='https://yacpdb.org/xfen/?'+XFEN)

        # sends embed
        await message.channel.send(embed=embedVar)

# takes problem ID and info about !sol command, spits out a prettified embed of the problem in the channel where the command was run
async def prettifiedSolutionEmbed(id, message):
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?entry&id='+id) as url:
        
        # gets data about the problem
        data = json.loads(url.read().decode())

        # gets stipulation
        solution = data.get('solution')

        # reformatting * to \* so it doesn't screw with Discord's formatting
        solution = solution.replace("*", "\*")
		
        # adding spoiler tags
        solution = '||' + solution + '||'

        # creates embed with solution
        embedVar = discord.Embed(title="YACPDB Problem >>"+id, description=solution, url='https://www.yacpdb.org/#'+id)

        # sends embed
        await message.channel.send(embed=embedVar)

# main event loop
@client.event

# listens for new messages
async def on_message(message):
    print(message.content)

    # response to !lookup
    if message.content.startswith('y!lookup'):
        
        # turns on typing indicator
        await message.channel.trigger_typing()

        # splits !problem messages into command + arguments
        input = message.content
        input = input.split()
        # DEBUG PURPOSES
        print(input)

        # pass yacpdb ID to other functions (if doesn't exist, throw error)
        try:	
            if len(input) == 1:	
                await message.channel.send('**WARNING**: No YACPDB problem ID specified. Syntax is `!lookup [problem id]`.')	
        # else send prettified problem as an embed	
            else:	
                problemid = str(input[1])	
                await prettifiedProblemEmbed(problemid, message)	
        except TimeoutError:	
            await message.channel.send('**WARNING**: Timeout error. Please check that YACPDB isn\'t down, then try again.')	
        except urllib.error.URLError:	
            await message.channel.send('**WARNING**: URL Error. Please check that YACPDB isn\'t down, then try again.')	
            

    # response to !problem
    if message.content.startswith('y!problem'):
        
        # turns on typing indicator
        await message.channel.trigger_typing()

        # splits !problem messages into command + arguments
        input = message.content
        input = input.split()
        # DEBUG PURPOSES
        print(input)

        # if number is supplied, as in "!problem 3", process number to give nth latest problem when calling newProblemID; else set n = 0
        stip = '-'
        n = 0
        if len(input) > 1:
            stip = input[1]
        if len(input) > 2:
            n = int(input[2])

        # get new problem
        problemid = await newProblemID(stip,n)

        # throw error if no new problems
        if problemid == 0:
            await message.channel.send('**Warning: no new problems matching stipulation found in the last 100 edits to YACPDB.**')

        # else send prettified problem as an embed
        else:
            await prettifiedProblemEmbed(problemid, message)
            
    # response to !sol
    if message.content.startswith('y!sol'):
        
        # turns on typing indicator
        await message.channel.trigger_typing()

        # splits !problem messages into command + arguments
        input = message.content
        input = input.split()
        # DEBUG PURPOSES
        print(input)

        # pass yacpdb ID to other functions (if doesn't exist, throw error)
        if len(input) == 1:
            await message.channel.send('**WARNING**: No YACPDB problem ID specified. Syntax is `!sol [problem id]`.')

        # else send prettified problem as an embed
        else:
            problemid = str(input[1])
            await prettifiedSolutionEmbed(problemid, message)

    # response to !help
    if message.content.startswith('y!help'):

        # turns on typing indicator
        await message.channel.trigger_typing()

        # help file (TODO: Expand documentation)

        embedVar = discord.Embed(title="YACPBot Help")
        embedVar.add_field(name="YACPBot Commands", value="`y!problem`: Get the latest problem from YACPDB. \n\
        `y!problem [stipulation] [n]`: Get the [n]th latest problem with stipulation [stipulation] ([stipulation] may optionally be replaced with -).\n\
        `y!sol [n]`: Gives the solution to YACPDB problem >>n in spoilers.\n\
        `y!lookup [n]`: Displays the nth problem in the database.\n\
        `y!help`: Displays these commands.")
		
	# random server+payment advertisement!
        if (random.randint(1,200) == 1) & (not message.guild.id == 758334446591410196):
            embedVar.add_field(name="Created by",value="@edderiofer#0713",inline=True)
            embedVar.add_field(name="Lucky Advertisement!",value="You've hit a lucky advertisement (it only has a 0.5% chance of turning up)! \
                                                                    Join the Chess Problems & Studies Discord today! http://discord.me/chessproblems \n\
                                                                    Also, if you're enjoying my bot, pay me! https://ko-fi.com/edderiofer",inline=True)
        else:
            embedVar.add_field(name="Created by",value="@edderiofer#0713",inline=False)
        
        await message.channel.send(embed=embedVar)

client.run(TOKEN)
