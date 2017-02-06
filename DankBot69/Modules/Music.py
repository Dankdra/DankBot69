import discord
from discord.ext import commands
import asyncio
import random
import datetime
import json
from Util.FilePrinter import youtube
from Util.FilePrinter import nextSong


MIN_VIEWS = 5000
MAX_PERCENT_DISLIKE = 0.25
MAX_LENGTH = 1200
MAX_SONGS_SHOWN = 10
MAXLOOPS = 5
VERSION = "0.4.3"
OPTS = {
            'quiet': True,
    }

class ServerPlayer:
	def __init__(self, server):
		self.server = server
		self.voice = None
		self.player = None
		self.queue = []
		self.radio = False
		self.skipList = []
		self.requester = None
		self.previousLooper = "0"


class MusicPlayer:
	def isStaff(self, ctx):
	    for role in ctx.message.author.roles:
	        if role.name == "Staff":
	            return True
	    return False

	def __init__(self, bot):
		with open('Playlists.json', 'r') as f:
			self.playList = json.load(f)
		self.bot = bot
		self.serverPlayers = {}
		#self.bot.loop.create_task(self.useQueue())

	@commands.command()
	async def music(self):
		'Returns the current status of the Music Bot'
		await self.bot.say("Connected to voice channels in [{}] servers!".format(", ".join([x.server.name for x in self.serverPlayers.values()])))
 
	@commands.command(pass_context = True)
	async def songs(self, ctx):
		'Prints the songs in the queue'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		ret = ""
		if len(SP.queue) != 0: #There is something in the Queue
			count = 1
			if len(SP.queue) <= MAX_SONGS_SHOWN: #There are less than [MAX_SONGS_SHOWN] in the Queue
				await self.bot.say("**The Following songs are in the Queue**")
				for song in SP.queue:
					ret += str(count) + ". " + song[0].title + " **" + song[1] + "**\n\t<" + song[0].url + ">\n"
					count+=1
			else:
				await self.bot.say("**The Following songs are in the Queue, plus [{}] more**".format(len(SP.queue) - MAX_SONGS_SHOWN))
				for x in range(0,MAX_SONGS_SHOWN,1):
					ret += str(count) + ". " + SP.queue[x][0].title + " **" + SP.queue[x][1] + "**\n\t<" + SP.queue[x][0].url + ">\n"
					count+=1
		else:
			await self.bot.say("Queue is Empty")
			return
		ret += "Total Time is {}".format(str(datetime.timedelta(seconds = self.totalTime(SP.queue))))
		await self.bot.say(ret)


	def totalTime(self, queue):
		time = 0
		for elem in queue:
			time += elem[0].duration
		return time

	@commands.command(pass_context = True)
	async def shuffle(self, ctx):
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		'Shuffles the songs in the Queue'
		await self.bot.say("Shuffling songs...")
		random.shuffle(SP.queue)

	@commands.command(pass_context = True)
	async def remove(self, ctx, number : int):
		'removes a song from a queue by index'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		if(len(SP.queue) < number):
			await self.bot.say("The Queue isnt that long!")
			return
		currentName = SP.queue[number - 1][1]
		if currentName == ctx.message.author.name or ctx.message.author.id == "134441036905840640" or currentName == "Radio":
			current = SP.queue.pop(number - 1)[0]
			current.process.kill()
			await self.bot.say("Removed: " + current.title)
		else:
			await self.bot.say("You must be the requester of the song to remove it from queue!")

	@commands.command(hidden = True, pass_context = True)
	async def forceplay(self,ctx, link : str):
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		if(ctx.message.author.id != "134441036905840640"):
			return
		SP.requester = ctx.message.author.name
		current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
		if(SP.player != None):
			SP.player.stop()
		SP.player = current
		SP.player.start()
		SP.skipList = []

	@commands.command(pass_context = True)
	async def loop(self, ctx, num = 1):
		'Plays the current song again'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		ID = ctx.message.author.id
		if ID not in [x.id for x in SP.voice.channel.voice_members]:
			await self.bot.say("You need to be in the voice channel!")
			return
		if(num > MAXLOOPS and ctx.message.author.id != "134441036905840640"):
			await self.bot.say("Can not loop that many times!")
			return
		if(SP.previousLooper == ctx.message.author.id and len(SP.voice.channel.voice_members) > 2 and ctx.message.author.id != "134441036905840640"):
			await self.bot.say("You can not loop more than once in a row! Please wait for someone else to loop a song.")
			return
		SP.previousLooper = ctx.message.author.id

		current = await SP.voice.create_ytdl_player(SP.player.url, ytdl_options=OPTS)
		final = (current, ctx.message.author.name)
		for x in range(0,num,1):
			SP.queue.insert(0, final)
		await self.bot.say("Added '*{}*' **{}** more times".format(SP.player.title, num))

	@commands.command()
	async def playlists(self):
		'Shows all the current playlists'
		with open('Playlists.json', 'r') as f:
			self.playList = json.load(f)
		Names = []
		for name, songs in self.playList.items():
			if(songs != None and name != None):
				Names.append(name + "[" + str(len(songs)) + "]")
		await self.bot.say(", ".join(Names))

	@commands.command(pass_context = True)
	async def youtube(self,ctx, * links : str):
		'Adds a Song for the Bot to Play'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		ID = ctx.message.author.id
		if ID not in [x.id for x in SP.voice.channel.voice_members]:
			await self.bot.say("You need to be in the voice channel!")
			return

		if(SP.voice == None):
			await self.bot.say("I am not connected to a Voice Chat!")
			return

		for link in links:
			if("www.youtube.com/watch?v" not in link and "https://youtu.be/" not in link):
				await self.bot.say("Not a Valid Link, Please only use URLs from youtube.com")
				break
			try:
				current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
			except Exception as e:
				self.bot.say(e)
				break
			if(current.views < MIN_VIEWS):
				await self.bot.say("Sorry, that video has too little views to be Trustworthy. Needs [{}] but has [{}]".format(format(MIN_VIEWS, ",d"), format(current.views, ",d")))
				current.process.kill()
				break
			elif(current.dislikes / (current.dislikes + current.likes) > MAX_PERCENT_DISLIKE):
				await self.bot.say("Sorry, too many people dislike that video. Needs to be below [{}%] but was [{}%]".format(MAX_PERCENT_DISLIKE * 100, round(current.dislikes / (current.dislikes + current.likes) * 100,2)))
				current.process.kill()
				break
			elif(current.duration > MAX_LENGTH):
				await self.bot.say("Sorry, that video is too long, it must be under [{}] minutes!".format(MAX_LENGTH/60))
				current.process.kill()
				break
			await self.bot.say("Added {} to the queue".format(current.title))
			SP.queue.append((current, ctx.message.author.name))
			print("Added Song to Queue")
			#await asyncio.sleep(3)

		# self.player.start()
		#print(player.views, player.likes, player.dislikes)
	@commands.command(pass_context = True)
	async def search(self, ctx, * Pinput : str):
		'Searches for a song'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		ID = ctx.message.author.id
		if ID not in [x.id for x in SP.voice.channel.voice_members]:
			await self.bot.say("You need to be in the voice channel!")
			return
		if(SP.voice == None):
			await self.bot.say("I am not connected to a Voice Chat!")
			return

		count = 0
		link = youtube("+".join(Pinput), count)
		try:
			current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
			while(current == None or current.dislikes == None or current.likes == None or current.views < MIN_VIEWS or current.dislikes / (current.dislikes + current.likes) > MAX_PERCENT_DISLIKE or current.duration > MAX_LENGTH):
				current.process.kill()
				link = youtube("+".join(Pinput), count)
				current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
				count += 1
			await self.bot.say("Added {} to the queue".format(current.title))
			await self.bot.say(link)
			SP.queue.append((current, ctx.message.author.name))
		except:
			await self.bot.say("Sorry, couldnt find anything :(")

	async def useQueue(self, SP):
		await self.bot.wait_until_ready()
		print("Running Queue in {}".format(SP.server.name))
		while not self.bot.is_closed and SP.voice is not None:
			if len(SP.queue) != 0:
				if SP.player is None:
					song = SP.queue.pop(0)
					SP.requester = song[1]
					await self.playSong(song[0], SP)
				if SP.player.is_playing() is False:
					song = SP.queue.pop(0)
					SP.requester = song[1]
					await self.playSong(song[0], SP)
			else:
				if(SP.radio and SP.player is not None):
					link = nextSong(SP.player.url)
					current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
					count = 0
					while(current == None or current.likes == None or current.views < MIN_VIEWS or current.dislikes / (current.dislikes + current.likes) > MAX_PERCENT_DISLIKE or current.duration > MAX_LENGTH):
						current.process.kill()
						link = nextSong(SP.player.url, count)
						current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
						while(current.likes == None):
							current.process.kill()
							link = nextSong(SP.player.url, count)
							current = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
							count += 1						
						count += 1
					SP.queue.append((current, "Radio"))
			await asyncio.sleep(1)
		print("Finished Queue in {}".format(SP.server.name))


	async def playSong(self, current, SP):
		if(SP.player != None):
			SP.player.stop()
		link = current.url
		if not current.is_done():
			current.start()
		current.stop()
		SP.player = await SP.voice.create_ytdl_player(link, ytdl_options=OPTS)
		print("Playing {} in {}".format(SP.player.title, SP.server.name))
		SP.player.start()
		SP.player.volume = 0.6
		SP.skipList = []


	@commands.command(pass_context = True)
	async def join(self,ctx):
		'Joins the Voice channel you are currently in'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
			if SP.voice != None:
				await SP.bot.say("Sorry, I'm already connected to a channel")
				return
			else:
				channel = ctx.message.author.voice_channel
				if channel is None:
					await self.bot.say("You are not connected to a voice channel!")
				else:
					try:
						self.serverPlayers[ctx.message.server.id] = ServerPlayer(ctx.message.server)
						SP = self.serverPlayers[ctx.message.server.id]
						SP.voice = await self.bot.join_voice_channel(channel)
						await self.bot.say("Connected channel!")
					except:
						self.serverPlayers[ctx.message.server.id] = ServerPlayer(ctx.message.server)
						SP = self.serverPlayers[ctx.message.server.id]
						SP.voice = ctx.message.server.voice_client
						await self.bot.say("Reconnected channel!")
					await self.useQueue(SP)
		except:
			channel = ctx.message.author.voice_channel
			if channel is None:
				await self.bot.say("You are not connected to a voice channel!")
			else:
				try:
					self.serverPlayers[ctx.message.server.id] = ServerPlayer(ctx.message.server)
					SP = self.serverPlayers[ctx.message.server.id]
					SP.voice = await self.bot.join_voice_channel(channel)
					await self.bot.say("Connected channel!")
				except:
					self.serverPlayers[ctx.message.server.id] = ServerPlayer(ctx.message.server)
					SP = self.serverPlayers[ctx.message.server.id]
					SP.voice = ctx.message.server.voice_client
					await self.bot.say("Reconnected channel!")
				await self.useQueue(SP)

	@commands.command(pass_context = True)
	async def Radio(self, ctx):
		'Toggles Radio Mode'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		SP.radio = not SP.radio
		await self.bot.say("Radio Mode: {}".format(SP.radio))

	@commands.command(pass_context = True)
	async def leave(self, ctx):
		'Leaves the Join chat'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		for x in SP.queue:
			current = x[0]
			current.process.kill()
		SP.queue = []
		await SP.voice.disconnect()
		SP.voice = None

	@commands.command(pass_context=True, hidden=True)
	async def musicdebug(self, ctx, *, code : str):
	    IDs = ["134441036905840640", "126122455248011265"]
	    if(ctx.message.author.id not in IDs):
	        return
	    """Evaluates code."""
	    code = code.strip('` ')
	    python = '```py\n{}\n```'
	    result = None

	    try:
	        result = eval(code)
	    except Exception as e:
	        await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
	        return

	    if asyncio.iscoroutine(result):
	        result = await result

	    await self.bot.say(python.format(result))

	@commands.command(pass_context = True)
	async def clear(self, ctx):
		'Clears the Queue'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		for x in SP.queue:
			current = x[0]
			current.process.kill()
		SP.queue = []
		await self.bot.say("Cleared Queue!")

	@commands.command(pass_context = True)
	async def song(self, ctx):
		'Returns information about the current playing song'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		try:
			await self.bot.say("**Name**: " + str(SP.player.title) + "\n" + 
			"**Requester**: " + str(SP.requester) + "\n" +
			"**URL**: <" + str(SP.player.url) + ">\n" +  
			"```py\nTime: " + str(datetime.timedelta(seconds = SP.player.duration)) + "\n" +
			"Views: " + str(format(SP.player.views, ',d')) + "\n" +
			"Likes: " + str(format(SP.player.likes, ',d')) + ", " + str(round(SP.player.likes/(SP.player.likes + SP.player.dislikes) * 100, 2)) + "%\n" + 
			"Dislikes: " + str(format(SP.player.dislikes, ',d')) + ", " + str(round(SP.player.dislikes/(SP.player.likes + SP.player.dislikes) * 100, 2)) + "%\n" +
			"Skips: " + str(len(SP.skipList)) + "/" + str(int(2*(len(SP.voice.channel.voice_members)-1)/3)) + "```"
			)
		except Exception as e:
			await self.bot.say("ERROR, [{}]".format(e))

	@commands.command(pass_context = True)
	async def desc(self, ctx):
		'Decription of the Current playing song'
		SP = self.serverPlayers[ctx.message.server.id]
		if SP == None:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		await self.bot.say("Current Song Description:\n{}".format(SP.player.description[:1000]))

	@commands.command(pass_context = True)
	async def skip(self, ctx):
		'Skips the Current song'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		ID = ctx.message.author.id

		# Only people in the channel can mute
		if ID not in [x.id for x in SP.voice.channel.voice_members]:
			await self.bot.say("You need to be in the voice channel!")
			return

		# Requester wants to skip
		if ctx.message.author.name == SP.requester:
			await self.bot.say("Skipping {} by request of the requester".format(SP.player.title))
			SP.player.stop()
			SP.skipList = []
			return

		# Its a Radio Song 
		if SP.requester == "Radio":
			await self.bot.say("Skipping {} by request (Radio Song)".format(SP.player.title))
			SP.player.stop()
			SP.skipList = []
			return

		NeededToSkip = int(2*(len(SP.voice.channel.voice_members)-1)/3)

		# Add a new `Skipper` to the list
		if ID not in SP.skipList:
			SP.skipList.append(ID)
			await self.bot.say("{}/{} votes to skip".format(len(SP.skipList), NeededToSkip))
		# If Enough votes, skip the song
		if len(SP.skipList) >= NeededToSkip:
			await self.bot.say("Skipping {} by popular vote.".format(SP.player.title))
			SP.player.stop()
			SP.skipList = []
	# Playlist Stuff

	@commands.command(pass_context = True)
	async def playlist(self, ctx, *names : str):
		'Adds songs from a predefined playlist to the songs list'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		with open('Playlists.json', 'r') as f:
			self.playlist = json.load(f)
		for name in names:
			random.shuffle(self.playList[name])
			for song in self.playList[name]:
				try:
					current = await SP.voice.create_ytdl_player(song, ytdl_options=OPTS)
					SP.queue.append((current, ctx.message.author.name))
				except Exception as e:
					print("Could Not Add a Song... Skipping it: <{}>".format(e))

		#print("Added playlist(s) to {}".format(SP.server.name))					
		await self.bot.say("Finished Adding songs from playlist(s)")

	@commands.command()
	async def makeplaylist(self, name, *links : str):
		'Makes a custom playlist for the bot to save'
		with open('Playlists.json', 'r') as f:
			self.playList = json.load(f)
		if(name in self.playList.keys()):
			await self.bot.say("Playlist already exists")
			return
		self.playList[name] = list(links)
		with open('Playlists.json', 'w') as f:
			json.dump(SP.playList, f)
		await self.bot.say("Created Playlist {} with {} songs".format(name, len(list(links))))

	@commands.command(pass_context = True)
	async def viewplaylist(self, name):
		'Views the songs of a playlists'
		try:
			SP = self.serverPlayers[ctx.message.server.id]
		except:
			await self.bot.say("The Bot isnt connected in this server!")
			return
		with open('Playlists.json', 'r') as f:
			self.playList = json.load(f)
		if(name not in self.playList.keys()):
			await self.bot.say("Playlist does not exists")
			return
		try:
			songNames = await self.getNames(self.playList[name], SP)
		except Exception as e:
			await self.bot.say(e)
			return
		await self.bot.say("\n".join(songNames))

	async def getNames(self, names, SP):
		cleanNames = []
		for name in names:
			try:
				song = await SP.voice.create_ytdl_player(name)
				cleanNames.append(song.title + " <{}>".format(song.url))
				song.start()
				song.stop()
			except Exception as e:
				print("{}\nBAD SONG IN A PLAYLIST".format(e))
		return cleanNames


	@commands.command()
	async def extendplaylist(self, name, *links : str):
		'Extends a custom playlist'
		with open('Playlists.json', 'r') as f:
			self.playList = json.load(f)
		if(name not in self.playList.keys()):
			await self.bot.say("Playlist does not exists")
			return
		self.playList[name].extend(list(links))
		with open('Playlists.json', 'w') as f:
			json.dump(self.playList, f)

	@commands.command(hidden = True)
	async def removeplaylist(self, name):
		'Removes a custom playlist'
		with open('Playlists.json', 'r') as f:	
			self.playList = json.load(f)
		if(name not in self.playList.keys()):
			await self.bot.say("Playlist does not exists")
			return			
		del self.playList[name]
		with open('Playlists.json', 'w') as f:
			json.dump(self.playList, f)
		await self.bot.say("Removed {}".format(name))



def setup(bot):
	bot.add_cog(MusicPlayer(bot))

	
