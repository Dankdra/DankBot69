import discord
from discord.ext import commands
import random
import traceback
import asyncio
import random
import time
import math
import urllib.parse
import datetime
import json
import os
from collections import defaultdict

#from Tournament.tournament import *
#from cleverbot import Cleverbot

from Util.Question import *
from Util.FilePrinter import *
from Util.PokemonJson import *

from mcstatus import MinecraftServer

VERSION = "0.15.1.3"
description = '''A Bot whose sole Purpose is to serve Wertfuzzy77! Version {}
(Created by Wertfuzzy77)'''.format(VERSION)
bot = commands.Bot(command_prefix=';', description=description, pm_help = True)

LOG = open("./Logs./" + "log" + str(time.time()) + ".txt",'w')

#CLEVERBOT = Cleverbot()

voice = None
player = None

startTime = time.time()
afks = {}
inTrivia = False

def isStaff(ctx):
    for role in ctx.message.author.roles:
        if role.name == "Germans":
            return True
    return False

messageNum = 0
EXTENTIONS = ['Modules.StaffCmds', 'Modules.Interaction', 'Modules.Music', 'Modules.Games']

@bot.event
async def on_ready():
    #Log = open("./Logs./" +Fev "log" + str(time.time()) + ".txt",'w')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    for extension in EXTENTIONS:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    await bot.change_presence(game=discord.Game(name='with code.'))
    await bot.loop.create_task(changeIcons())

async def changeIcons():
    await bot.wait_until_ready()
    while not bot.is_closed:
        fp = open("Icons/" + random.choice(os.listdir("Icons")), 'rb')
        NewAvatar = fp.read()
        await bot.edit_profile(avatar = NewAvatar)
        fp.close()
        await asyncio.sleep(600)

@bot.command()
async def changeIcon():
        fp = open("Icons/" + random.choice(os.listdir("Icons")), 'rb')
        NewAvatar = fp.read()
        await bot.edit_profile(avatar = NewAvatar)
        fp.close()

@bot.command()
async def feedback():
    'Returns a link to a Google Forums, where you can leave feedback for the bot'
    await bot.say("**Use This Link to Give Feedback on me :D**\nhttp://goo.gl/forms/5o0YV1wbmXAhv6XT2")

@bot.command()
async def status():
    'Returns the Status of the Bot, along with Additional Information'
    await bot.say("UpTime: {}s".format(str(datetime.timedelta(seconds = round(time.time() - startTime,1)))))
    await bot.say("Total Messages: {}".format(messageNum))
    await bot.say("Servers Joined: {}".format(len(bot.servers)))

@bot.command(pass_context = True)
async def server(ctx, IP = "mc.limitlessmc.net"):
    'Returns Information on the Limitless MC server!'
    try:
        server = MinecraftServer.lookup(IP)
        status = server.status()
        await bot.say("**Server IP**: {}".format(IP))
        await bot.say("**Server Status**\n *Online Players*: {} players out of {}\n *Ping*: {} ms\n *MC Version*: {}".format(status.players.online, status.players.max, status.latency, status.version.name))
        await bot.say("**Pixelmon Version**: {}".format(status.raw['modinfo']['modList'][11]['version']))
        await bot.say("**Players Online**:\n *{}...*".format(", ".join([x.name for x in status.players.sample])))
    except Exception as e:
        await bot.say("*Server is Down :(*")

@bot.command()
async def source():
    'Returns a link to the source code for this bot'
    await bot.say("Get your own code nerd")

@bot.command(pass_context = True, hidden = True)
async def relog(ctx):
    '''Relogs The Bot'''
    if isStaff():
        return
    else:
        await bot.say("Relogging...")
        LOG.close()
        await bot.logout()		
        Popen("Start_Botfuzzy77.bat")

@bot.command()
async def invite():
    'Returns a Link to the Invite URL for this bot'
    await bot.say("https://discordapp.com/oauth2/authorize?client_id=187608834381053952&scope=bot&permissions=00000008")

@bot.event
async def on_member_join(member):
    server = member.server
    result = ("Welcome {0.mention} to {1.name}!")
    await bot.send_message(server, result.format(member, server))

@bot.event
async def on_member_update(before, after):
    return
    message = None
    #print(CONFIG[before.server.name]["Online"])
    try:
        if before.server.name in ["The Pleb Privateers"] or before.server.id in ["126122560596213760"]:
            return
        if str(before.status) == "offline" or str(before.status) == "idle" and str(after.status) == "online":
            message = await bot.send_message(before.server, "**{}**({}) is now Online!".format(before.name, before.top_role if before.top_role.name != "@everyone" else "No Role"))
            await asyncio.sleep(20)
            await bot.delete_message(message)
        if str(before.status) == "online" and str(after.status) == "offline":
            message = await bot.send_message(before.server, "**{}**({}) is now Offline!".format(before.name, before.top_role if before.top_role.name != "@everyone" else "No Role"))
            await asyncio.sleep(5)
            await bot.delete_message(message)
    except Exception as e:
        print(type(e).__name__, e)

    
@bot.event
async def on_message(message):
    #Logging
    global messageNum
    try:
        LOG.write("{1} : {0.server}, {0.channel}, {0.author}, {0.clean_content}\n".format(message, time.strftime("%d %b %Y %H:%M:%S", time.gmtime())))
    except Exception as e:
        print("Someting wong\n", type(e).__name__, e)

    # Dont DO anything if message author is Bot
    if(message.author.id == bot.user.id):
        return

    for member in message.mentions:
        #print(member.name, afks)
        if member in afks:
            await bot.send_message(message.channel, "{} is afk for reason:\n**{}**".format(member.name, afks[member]))

    messageNum += 1

    #print(message.content + "\n" + message.content.upper())
    if(len(message.content) > 20 and message.content.upper() == message.content and message.content.isalpha()):
        await bot.delete_message(message)
        #print("removing caps message")
        return

    # if Parsable as Limitless URL
    if("http://limitlessmc.net/f/viewtopic.php?" in message.content):
        await bot.send_message(message.channel, ForumPost(message.content))

    Ids = [x.id for x in message.mentions]
    if(bot.user.id in Ids):
        #print(message.content.replace("<@!187609093001838602>", ""))
        await bot.send_message(message.channel, "I'm sorry, but the Cleverbot API has changed... I can no longer speak to you :(")
        # response = CLEVERBOT.ask(message.content.replace("<@!{}>".format(bot.user.id), ""))
        # await bot.send_message(message.channel, response)
        return
    # Easter Egg, returns "From the other side" if someone types Hello
    if(message.content == "Hello" or message.content == "hello"):
        await bot.send_message(message.channel, "*From The Other Side*")
        return
        
    if(message.content == "Hail" or message.content == "hail"):
        await bot.send_message(message.channel, "**Hail mein Furher**")
        return

    if(message.content == "Ayy" or message.content == "ayy"):
        await bot.send_message(message.channel, "Lmao")
        return

    if(message.content == "^"):
        await bot.send_message(message.channel, "^")
        return

    # if(message.content == "Bet" or message.content == "bet"):
    #     await bot.send_message(message.channel, "bet")
    #     return
    # Normal IF Statement
    # if(message.channel.id != '148202028244402176' or message.author.name == "Wertfuzzy77"):
    #     #print("{0.author}, {0.content}".format(message))

    try:
        await bot.process_commands(message)
    except Exception as e:
        return

@bot.command(pass_context=True, hidden=True)
async def debug(ctx, *, code : str):
    IDs = ["134441036905840640"]
    if(ctx.message.author.id not in IDs):
        return
    """Evaluates code.""" 
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None

    try:
        result = eval(code)
    except Exception as e:
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return

    if asyncio.iscoroutine(result):
        result = await result

    await bot.say(python.format(result))

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    raw_date = member.joined_at

    await bot.say('{0.name} joined in {1}'.format(member, raw_date))
    

@bot.command()
async def ev(*playerInput : str):
    for inp in playerInput:
        ret = "**" + inp + "**\n```py\n" + getEVs(inp) + "```"
        await bot.say(ret)

@bot.command()
async def pokemon(pkmn = "charizard"):
    '''Returns Links to Pokemon pages'''
    await bot.say("Pixelmon Page: http://pixelmonmod.com/wiki/index.php?title={}".format(pkmn))
    await bot.say("Bulbapedia Page: http://bulbapedia.bulbagarden.net/wiki/{}".format(pkmn))
    await bot.say("Pokemon DB: http://pokemondb.net/pokedex/{}".format(pkmn))
    await bot.say("Smogon: http://www.smogon.com/dex/bw/pokemon/{}".format(pkmn))

@bot.command(pass_context = True)
async def afk(ctx, * reason : str):
    '''Sets you as AFK, and the Bot will auto Reply for you with the Given Reason. (Put no Reason to Un-Afk)'''
    if(len(reason) == 0):
        del afks[ctx.message.author]
        await bot.say('''{} is no Longer AFK'''.format(ctx.message.author.name))
    else:
        addAfk(ctx.message.author, ' '.join(reason))
        await bot.say('''{} is now AFK for reason:\n**{}**'''.format(ctx.message.author.name, ' '.join(reason)))

def addAfk(user, message):
    try:
        afks[user] = message
        return 1
    except Exception as e:
        return 0

if __name__ == '__main__':
bot.run('MTg3NjA5MDkzMDAxODM4NjAy.Ck93eA.9z44cXnLO7B6glZNjaCOvqQfX6M')
