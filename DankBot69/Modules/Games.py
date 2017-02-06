import discord
from discord.ext import commands
import asyncio
from collections import defaultdict
import time
import random
import operator
import time
import json
import math

from Util.PokemonJson import *

COOLDOWN = 90
TCOOLDOWN = 3600
SCOOLDOWN = 21600
GCOOLDOWN = 120
NUM_MOVES = 8
NEWPLAYER = {"Name" : "BLANK", "Level": 5, "XP": 0, "Large_Damage" : 0, "Takedowns" : 0, "Pokemon" : [], "Type" : "Normal"}
BOSSRESPAWN = 120
TYPES = ['normal', 'water', 'fire', 'grass', 'poison', 'dragon', 'steel', 'electric', 'bug', 'ice']

HelpMessage = """Welcome to the **Pokemon Battle Sim**!
Here you fight together against Pokemon Bosses. There are 4 areas, *Easy*, *Medium*, *Hard* and *Insane*.
To fight a boss, you use the command `;pokebattle`, a set of moves you will fight the boss with, and a location you want to fight in. (The bot will default to the area best suited for you level if left blank)
An example of this is the following:
`;pokebattle ngfse easy`
which means you will be fighting the easy boss with battle combo of Normal, Grass, Fire, Steel, and Electric.
You can use any combination of the 10 moves which can be found on `;types`"""

class Games:
	def __init__(self, bot):
		self.bot = bot
		self.BossCooldown = {}
		self.AUTO_RESPAWN = True
		self.training = {}
		self.Gamble = {}
		self.Locations = ["easy", "medium", "hard", "insane"]
		self.EASY_MAX = (1, 10)
		self.MEDIUM_MAX = (10, 50)
		self.HARD_MAX = (50, 80)
		self.INSANE_MAX = (80, 99)
		self.bosses = {"easy" : Boss(self.EASY_MAX), "medium" : Boss(self.MEDIUM_MAX), "hard" : Boss(self.HARD_MAX), "insane" : Boss(self.INSANE_MAX)}

	@commands.command(pass_context = True)
	async def pokebattle(self, ctx, moves = "", area = ""):
		'Fights a Pokemon Boss'
		# Checks Location

		if area == "":
			area = await self.BestArea(ctx.message.author)

		area = area.lower()
		if area not in self.Locations:
			await self.bot.say("The Available Locations are {}".format(", ".join(self.Locations)))
			return

		if not await self.AvailableToBattle(ctx.message.author, area):
			await self.bot.say("You are not a high enough level to be in this area!")
			if area == "easy":
				neededLevel = 0
			elif area == "medium":
				neededLevel = self.MEDIUM_MAX[0]
			elif area == "hard":
				neededLevel = self.HARD_MAX[0]
			else:
				neededLevel = self.INSANE_MAX[0]
			await self.bot.say("You need to be atleast Level {}".format(neededLevel))
			return

		# Check cooldown on players
		if ctx.message.author.id in list(self.BossCooldown.keys()):
			if self.BossCooldown[ctx.message.author.id] + COOLDOWN > time.time():
				await self.bot.say("Please wait {} seconds before you can fight the boss again.".format(round(self.BossCooldown[ctx.message.author.id] + COOLDOWN - time.time()), 0))
				return


		boss = self.bosses[area]
		moves = moves.upper()
		if moves == "" or len(moves) is not boss.Moves:
			await self.bot.say("Please use a Combination of **{}** Types. `;types`".format(boss.Moves))
			return
		for x in moves:
			if x not in ["N","F","W","G","P","D","S","E","B","I"]:
				await self.bot.say("Please use a Combination of **{}** Types. `;types`".format(boss.Moves))
				return


		# Respawn boss or say is Dead.
		if boss.isDefeated and self.AUTO_RESPAWN:
			if area == "easy":
				self.bosses[area] = Boss(self.EASY_MAX)
			elif area == "medium":
				self.bosses[area] = Boss(self.MEDIUM_MAX)
			elif area == "hard":
				self.bosses[area] = Boss(self.HARD_MAX)
			else:
				self.bosses[area] = Boss(self.INSANE_MAX)
			boss = self.bosses[area]

		if boss.isDefeated:
			await self.bot.say("Level {} Boss **{}** has been defeated!".format(boss.level, boss.Name))
			await self.bot.say("A new Boss will summon in {}".format(round(self.Bossrespawn[area] + BOSSRESPAWN - time.time(), 0)))

		if not boss.hasBeenRevealed:
			await self.bot.say("A Level {} Boss **{}** has appeared in the {} zone!\nIt has {:,} Health.".format(boss.level, boss.Name, area.capitalize(), boss.Health))

			f = open('BossImage{}.jpg'.format(area),'wb')
			f.write(requests.get(boss.Image).content)
			f.close()

			await self.bot.send_file(ctx.message.channel, 'BossImage{}.jpg'.format(area))
			boss.hasBeenRevealed = True
			boss.summoner = ctx.message.author.name
		else:
			await self.bot.say("Level {} Boss **{}** in {} has {:,} health left.".format(boss.level, boss.Name, area.capitalize(), boss.Health))
			await self.bot.send_file(ctx.message.channel, 'BossImage{}.jpg'.format(area))
		correctOnes = [boss.combination[x] == moves[x] for x in range(0, boss.Moves, 1)]

		Pinput = [":regional_indicator_{}:".format(value.lower()) for value in moves]
		output = [":white_check_mark:" if value else ":x:" for value in correctOnes]
		await self.bot.say(" ".join(Pinput) + "\n" + " ".join(output))
		boss.lastUsedCombo = " ".join(Pinput) + "\n" + " ".join(output)
		# Calculate Damage done, Varies from 75% - 125%

		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			pre = ALLPLAYERS[ctx.message.author.id]
			player = await self.checkLevel(pre)
			if pre['Level'] is not player['Level']:
				await self.bot.say("You Have Leveled up from {} to {}".format(pre['Level'], player['Level']))
		except: 
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER
			player = ALLPLAYERS[ctx.message.author.id]

		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

		# Deal Damage
		dmg = player['Level']
		if dmg == 0:
			dmg = 1

		m = ""
		Total_Damage = [dmg * 1.25 if value else 0 for value in correctOnes]
		Total_Damage = sum(Total_Damage)
		if random.random() < 0.10:
			m += "Its a Critical Strike\n"
			Total_Damage = Total_Damage * 2
		if correctOnes.count(True) == boss.Moves - 1:
			m += "Its Super Effective! The Boss has switched 1/4 of the Super Effective Moves!\n"
			Total_Damage = Total_Damage * 10
			boss.changeQuarter()
		elif correctOnes.count(True) == boss.Moves:
			m += "Its a Perfect Combo. The Boss has switched 1/2 of the Super Effective Moves!\n"
			Total_Damage = Total_Damage * 25
			boss.changeHalf()
		elif correctOnes.count(True) > boss.Moves / 2:
			m += "Its Sort-Of Effective\n"
			Total_Damage = Total_Damage * 1.25 * (correctOnes.count(True) + 1) / (boss.Moves / 2)


		if area == "easy":
			maxLevel = self.EASY_MAX[1]
		elif area == "medium":
			maxLevel = self.MEDIUM_MAX[1]
		elif area == "hard":
			maxLevel = self.HARD_MAX[1]
		else:
			maxLevel = self.INSANE_MAX[1]

		if player['Level'] > maxLevel:
			Total_Damage = Total_Damage * boss.level / player["Level"]
			m += "*Low level boss penalty...*\n"

		if boss.summoner == ctx.message.author.name:
			m += "Rival Bonus!\n"
			Total_Damage = Total_Damage * 1.25

		Type = await self.getPlayer(ctx.message.author)
		Type = Type['Type'].upper()
		STABcount = 0
		for x in range(0, boss.Moves, 1):	
			if Type[0] == moves[x] and correctOnes[x] == True:
				Total_Damage *= 1.1
				STABcount += 1
		if STABcount >= 1:
			m += "STAB bonus damage for {} type ({}x)\n".format(Type.capitalize(), STABcount)

		if Total_Damage is not 0:
			Total_Damage = int(Total_Damage * random.randrange(75, 125, 5) / 100 + 1)

		await self.dealDamage(ctx.message.author, Total_Damage)
		GivenXP = int(Total_Damage/10) if int(Total_Damage/10) > 1 else 1
		m += "Your moves did **{:,}** damage\n".format(Total_Damage)
		m += "Your gained **{:,}** XP".format(GivenXP)
		await self.bot.say(m)
		boss.Health = boss.Health - Total_Damage
		await self.giveXP(ctx.message.author, GivenXP, ctx.message.channel)
		try: 
			boss.Damage[ctx.message.author] = boss.Damage[ctx.message.author] + Total_Damage
		except:
			boss.Damage[ctx.message.author] = Total_Damage

		# Boss is ded
		if boss.Health <= 0:
			await self.takeDown(ctx.message.author)
			await self.bot.say("Level {} Boss **{}** has been defeated!".format(boss.level, boss.Name))
			sorted_Damage = sorted(boss.Damage.items(), key=operator.itemgetter(1), reverse=True)
			try:
				await self.bot.say("Most Damage by **{}** with **{:,}** damage".format(sorted_Damage[0][0].name, sorted_Damage[0][1]))
			except:
				await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[0][1]))
			if len(sorted_Damage) >= 2:
				try:
					await self.bot.say("2nd most Damage by *{}* with *{:,}* damage".format(sorted_Damage[1][0].name, sorted_Damage[1][1]))
				except:
					await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[1][1]))
			if len(sorted_Damage) >= 3:
				try:
					await self.bot.say("3rd most Damage by *{}* with *{:,}* damage".format(sorted_Damage[2][0].name, sorted_Damage[2][1]))
				except:
					await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[2][1]))
			if len(sorted_Damage) >= 4:
				await self.bot.say("Assisted by {}".format(", ".join([sorted_Damage[x][0].name for x in range(3, len(sorted_Damage), 1)])))
			boss.isDefeated = True

			# XP
			await self.giveXP(sorted_Damage[0][0], int(boss.StartingHealth*.50) + int(boss.Damage[sorted_Damage[0][0]]/2) + 1, ctx.message.channel)
			if len(sorted_Damage) >= 2:
				await self.giveXP(sorted_Damage[1][0], int(boss.StartingHealth*.20) + int(boss.Damage[sorted_Damage[1][0]]/3) + 1, ctx.message.channel)
			if len(sorted_Damage) >= 3:
				await self.giveXP(sorted_Damage[2][0], int(boss.StartingHealth*.10) + int(boss.Damage[sorted_Damage[2][0]]/5) + 1, ctx.message.channel)
			if len(sorted_Damage) >= 4:
				members = [sorted_Damage[x][0] for x in range(3, len(sorted_Damage), 1)]
				for member in members:
					await self.giveXP(member, int(boss.StartingHealth * 0.05) + 1)

			for member in boss.Damage.items():
				self.players[member.id] = 0

		else:
			await self.bot.say("Level {} Boss **{}** has {:,} health left.".format(boss.level, boss.Name, boss.Health))
			self.BossCooldown[ctx.message.author.id] = time.time()

	async def dealDamage(self, member, damage):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[member.id] = NEWPLAYER
			player = ALLPLAYERS[member.id]
		if(player['Large_Damage'] < damage):
			ALLPLAYERS[member.id]['Large_Damage'] = damage
		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	async def takeDown(self, member):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[member.id] = NEWPLAYER
			player = ALLPLAYERS[member.id]
		ALLPLAYERS[member.id]['Takedowns'] += 1
		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	async def AvailableToBattle(self, member, area):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(member.name))
			NEWPLAYER['Name'] = member.name
			ALLPLAYERS[member.id] = NEWPLAYER	
			player = ALLPLAYERS[member.id]

		if area == "easy":
			neededLevel = 0
		elif area == "medium":
			neededLevel = self.MEDIUM_MAX[0]
		elif area == "hard":
			neededLevel = self.HARD_MAX[0]
		else:
			neededLevel = self.INSANE_MAX[0]

		return player['Level'] >= neededLevel

	async def BestArea(self, member):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(member.name))
			NEWPLAYER['Name'] = member.name
			ALLPLAYERS[member.id] = NEWPLAYER	
			player = ALLPLAYERS[member.id]

		if player['Level'] >= self.INSANE_MAX[0]:
			return "insane"
		elif player['Level'] >= self.HARD_MAX[0]:
			return 'hard'
		elif player['Level'] >= self.MEDIUM_MAX[0]:
			return 'medium'
		else:
			return 'easy'

	@commands.command(pass_context = True)
	async def pokeboss(self, ctx, area = ""):
		'Displays Boss Info'
		if area == "":
			area = await self.BestArea(ctx.message.author)

		if area not in self.Locations:
			await self.bot.say("wut")
			return
		boss = self.bosses[area]

		if boss.isDefeated and self.AUTO_RESPAWN and self.Bossrespawn[area] + BOSSRESPAWN < time.time():
			if area == "easy":
				self.bosses[area] = Boss(self.EASY_MAX)
			elif area == "medium":
				self.bosses[area] = Boss(self.MEDIUM_MAX)
			elif area == "hard":
				self.bosses[area] = Boss(self.HARD_MAX)
			else:
				self.bosses[area] = Boss(self.INSANE_MAX)
			boss = self.bosses[area]

		if not boss.hasBeenRevealed:
			await self.bot.say("Boss has not been Revealed!\nPlease use ;pokebattle <moves> {} to fight and reveal the boss.".format(area))
			return
		if boss.isDefeated:
			await self.bot.say("Level {} Boss **{}** has been defeated!".format(boss.level, boss.Name))
			await self.bot.say("A new Boss will summon in {}".format(round(self.Bossrespawn[area] + BOSSRESPAWN - time.time(), 0)))
		else:
			await self.bot.say("-= **{4} Boss Pokemon** =-\n*Name*: {0.Name}\n*Health*: {0.Health:,}/{0.StartingHealth} ({1}%)\n*Level*: {2}\nLast Combo:\n{3}".format(boss, round(100*boss.Health / boss.StartingHealth, 2), boss.level, boss.lastUsedCombo, area.capitalize()))
			await self.bot.send_file(ctx.message.channel, "BossImage{}.jpg".format(area))
		sorted_Damage = sorted(boss.Damage.items(), key=operator.itemgetter(1), reverse=True)
		try:
			await self.bot.say("Most Damage by **{}** with **{:,}** damage".format(sorted_Damage[0][0].name, sorted_Damage[0][1]))
		except:
			await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[0][1]))
		if len(sorted_Damage) >= 2:
			try:
				await self.bot.say("2nd most Damage by *{}* with *{:,}* damage".format(sorted_Damage[1][0].name, sorted_Damage[1][1]))
			except:
				await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[1][1]))
		if len(sorted_Damage) >= 3:
			try:
				await self.bot.say("3rd most Damage by *{}* with *{:,}* damage".format(sorted_Damage[2][0].name, sorted_Damage[2][1]))
			except:
				await self.bot.say("Most Damage by *UNKNOWN* with **{:,}** damage".format(sorted_Damage[2][1]))
		if len(sorted_Damage) >= 4:
			await self.bot.say("Assisted by {}".format(", ".join([sorted_Damage[x][0].name for x in range(3, len(sorted_Damage), 1)])))

	@commands.command(pass_context = True)
	async def cd(self, ctx):
		'Shows your Cooldowns'
		msg = ""
		msg += "**Battle**\n"
		if ctx.message.author.id in list(self.BossCooldown.keys()):
			if self.BossCooldown[ctx.message.author.id] + COOLDOWN > time.time():
				msg += "You need to wait {} seconds\n".format(round(self.BossCooldown[ctx.message.author.id] + COOLDOWN - time.time()), 0)
			else:
				msg += "You can battle right now!\n"
		else:
			msg += "You can battle right now!\n"

		msg += "**Train** (*Note: Must be Level 5 to use ;train*)\n"
		if ctx.message.author.id in list(self.training.keys()):
			if self.training[ctx.message.author.id] + TCOOLDOWN > time.time():
				msg += "You need to wait {:,} seconds\n".format(round(self.training[ctx.message.author.id] + TCOOLDOWN - time.time()), 0)
			else:
				msg += "You can Train right now!\n"
		else:
			msg += "You can Train right now!\n"


		msg += "**Gamble** (*Note: Must be Level 5 to use ;gamble*)\n"
		if ctx.message.author.id in list(self.Gamble.keys()):
			if self.Gamble[ctx.message.author.id] + GCOOLDOWN > time.time():
				msg += "You need to wait {} seconds".format(round(self.Gamble[ctx.message.author.id] + GCOOLDOWN - time.time()), 0)
			else:
				msg += "You can Gamble right now!"
		else:
			msg += "You can Gamble right now!"
		m = await self.bot.say(msg)
		await asyncio.sleep(5)
		await self.bot.delete_messages([m, ctx.message])

	@commands.command()
	async def pokehelp(self):
		'Pokemon Battle Sim Help'
		await self.bot.say(HelpMessage)

	@commands.command(pass_context = True)
	async def level(self, ctx):
		'Displays your Current Information'
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[ctx.message.author.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER	
			player = ALLPLAYERS[ctx.message.author.id]
		# \//\
		if "Type" not in list(ALLPLAYERS[ctx.message.author.id].keys()):
			ALLPLAYERS[ctx.message.author.id]['Type'] = "Normal"
			player = ALLPLAYERS[ctx.message.author.id]
		await self.bot.say("**Name**: *{}*\n**Level**: {}".format(player['Name'], player['Level']))
		await self.bot.send_file(ctx.message.channel, 'small/s_{}_en.png'.format(ALLPLAYERS[ctx.message.author.id]['Type'].lower()))
		await self.bot.say("**XP**: {:,}/{:,}\n**Boss Takedowns**: {}\n**Most Dmg in an Attack**: {:,}".format(player['XP'], await self.ToLevel(int(player['Level']) + 1), player['Takedowns'], player['Large_Damage']))
		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	@commands.command(pass_context = True)
	async def lookup(self, ctx, member  : discord.Member):
		'Displays your Current Information'
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			await self.bot.say("Could Not find that player!")
			return
		if "Type" not in list(ALLPLAYERS[ctx.message.author.id].keys()):
			ALLPLAYERS[ctx.message.author.id]['Type'] = "Normal"
			player = ALLPLAYERS[ctx.message.author.id]
		await self.bot.say("**Name**: *{}*\n**Level**: {}".format(player['Name'], player['Level']))
		await self.bot.send_file(ctx.message.channel, 'small/s_{}_en.png'.format(ALLPLAYERS[member.id]['Type'].lower()))
		await self.bot.say("**XP**: {:,}/{:,}\n**Boss Takedowns**: {}\n**Most Dmg in an Attack**: {:,}".format(player['XP'], await self.ToLevel(int(player['Level']) + 1), player['Takedowns'], player['Large_Damage']))
		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	@commands.command(pass_context = True)
	async def gamble(self, ctx, amount : int = 0):
		if ctx.message.author.id in list(self.Gamble.keys()):
			if self.Gamble[ctx.message.author.id] + GCOOLDOWN > time.time():
				await self.bot.say("Please wait {} seconds before you can gamble again.".format(round(self.Gamble[ctx.message.author.id] + GCOOLDOWN - time.time()), 0))
				return
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[ctx.message.author.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER	
			player = ALLPLAYERS[ctx.message.author.id]

		if amount < await self.ToLevel(player['Level'] + 1) / 16:
			await self.bot.say("You need to gamble atleast {:,} XP".format(int(await self.ToLevel(player['Level'] + 1) / 16) + 1))
			return
		if player['Level'] < 5:
			await self.bot.say("You must be Level 5 to use ;train")
			return
		if player['XP'] < amount:
			await self.bot.say("You don't have that much XP")
			return

		option = random.random() * 100
		if option < 55:
			await self.bot.say("You have lost your offering...")
			await self.takeXP(ctx.message.author, amount)
		elif option < 95:
			await self.bot.say("You have gained back your offering and more!")
			await self.giveXP(ctx.message.author, int(amount*1.5), ctx.message.channel)
		else:
			# If amount is more than 1/2 level, give back train, else nothing
			if amount > await self.ToLevel(player['Level'] + 1) / 8:
				await self.bot.say("Your offering has refreshed ;train for you!")
				self.training[ctx.message.author.id] = 0
			else:
				await self.bot.say("It looks like your offering was going to do something, but you must not have given a big enough sacrifice. (Needed {:,})".format(int(await self.ToLevel(player['Level'] + 1) / 8)))
		if random.random() < 0.25:
			self.Gamble[ctx.message.author.id] = time.time()
			await self.bot.say("You are exhausted from Gambling... ")

	@commands.command()
	async def ranking(self):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		sorted_players = sorted(ALLPLAYERS.items(), key=self.getLevel, reverse=True)
		ret = ""
		# 1st
		first = sorted_players[0][1]
		ret += ":first_place: **{}** Level **{}**\n".format(first['Name'], first['Level'])

		second = sorted_players[1][1]
		ret += ":second_place: **{}** Level **{}**\n".format(second['Name'], second['Level'])

		third = sorted_players[2][1]
		ret += ":third_place: **{}** Level **{}**\n".format(third['Name'], third['Level'])

		for x in range(3, 10, 1):
			ply = sorted_players[x][1]
			ret += ":medal: {} Level {}\n".format(ply['Name'], ply['Level'])	

		await self.bot.say(ret)
		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	def getLevel(self, dict):
		return dict[1]['Level']

	async def giveXP(self, member , XP : int, channel):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = await self.checkLevel(ALLPLAYERS[member.id])
		except:
			print("NEW PLAYER: {}".format(member.name))
			NEWPLAYER['Name'] = member.name
			ALLPLAYERS[member.id] = NEWPLAYER
				
		ALLPLAYERS[member.id]["XP"] = ALLPLAYERS[member.id]["XP"] + XP

		if ALLPLAYERS[member.id]['Level'] < 5:
			ALLPLAYERS[member.id]['Level'] = 5

		pre = ALLPLAYERS[member.id]['Level']
		ALLPLAYERS[member.id] = await self.checkLevel(ALLPLAYERS[member.id])
		if pre is not ALLPLAYERS[member.id]['Level']:
			await self.bot.send_message(channel, "You Have Leveled up from **{}** to **{}**!".format(pre, ALLPLAYERS[member.id]['Level']))

		with open('Players.json', 'w') as f:
				json.dump(ALLPLAYERS, f)

	async def takeXP(self, member , XP : int):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER	
				
		ALLPLAYERS[member.id]["XP"] = ALLPLAYERS[member.id]["XP"] - XP

		with open('Players.json', 'w') as f:
				json.dump(ALLPLAYERS, f)

	@commands.command(pass_context = True)
	async def settype(self, ctx, Type = "none"):
		member = ctx.message.author
		if Type.lower() not in TYPES:
			await self.bot.say("You must pick a type from ;types")
			return

		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER
		try:
			chosen = ALLPLAYERS[member.id]["Type"]
		except:
			ALLPLAYERS[member.id]["Type"] = ["Normal"]
			chosen = ALLPLAYERS[member.id]["Type"]

		if ALLPLAYERS[member.id]['Level'] < 5:
			await self.bot.say("You must be Level 5 to pick a type!")
			return

		ALLPLAYERS[member.id]["Type"] = Type
		await self.bot.say("You are now a {} type".format(Type.capitalize()))

		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

	@commands.command(pass_context = True)
	async def train(self, ctx):
		"Fights Pokemon for XP"
		if ctx.message.author.id in list(self.training.keys()):
			if self.training[ctx.message.author.id] + TCOOLDOWN > time.time():
				await self.bot.say("Please wait {:,} seconds before you can train again.".format(round(self.training[ctx.message.author.id] + TCOOLDOWN - time.time()), 0))
				return
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[ctx.message.author.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER	
			player = ALLPLAYERS[ctx.message.author.id]

		if player['Level'] < 5:
			await self.bot.say("You must be Level 5 to use ;train")
			return


		# Fight (LEVEL/4 + 1 to LEVEL Pokemon)
		# Levels from 1 to 2 * LEVEL
		# Percent to win = LEVEL / 2 / level * 100

		Enemies = [Enemy(getRandomName(), random.randrange(int(player['Level']/2), 2*player['Level'])) for x in range(int(player['Level']/4), int(player['Level']/2) + 1, 1)]
		beatEnemies = []
		toPrint = ""
		XP = 0
		for enemy in Enemies:
			percent_to_kill = player['Level'] / 2 / enemy.level * 100
			if percent_to_kill > 90:
				percent_to_kill = 90
			if random.random() * 100 < percent_to_kill:
				beatEnemies.append(enemy)
				kill_xp = int(player['Level'] * (100 - percent_to_kill) * 0.8)
				# kill_xp = int(math.pow(enemy.level, 3) / 5) if int(math.pow(enemy.level, 3) / 10) not 0 else 1
				XP += kill_xp
				toPrint += "You **Beat** a Level {} **{}** for {:,} XP ({}% to beat)\n".format(enemy.level, enemy.name, kill_xp, int(percent_to_kill))
			else:
				toPrint += "You *Lost* to a Level {} **{}** ({}% to beat)\n".format(enemy.level, enemy.name, int(percent_to_kill))

		if random.random() <= 0.33:
			toPrint += "You use a **Lucky Egg** to gain more XP!\n"
			XP = XP * 1.5

		pokelootText = ""
		pokeloot = 0
		if random.random() <= 0.50:
			pokeloot += await self.ToLevel(player['Level'] + 1) * 0.05 + 1
			pokelootText += "You Find a **Pokeloot** worth {:,} XP\n".format(int(await self.ToLevel(player['Level'] + 1) * 0.05 + 1))
		if random.random() <= 0.10:
			pokeloot += await self.ToLevel(player['Level'] + 1) * 0.12 + 1
			pokelootText += "You Find a **Ultra Pokeloot** worth {:,} XP\n".format(int(await self.ToLevel(player['Level'] + 1) * 0.12 + 1))
		if random.random() <= 0.03:
			pokeloot += await self.ToLevel(player["Level"] + 1) * 0.30 + 1
			pokelootText += "You Find an **Master Pokeloot** worth {:,} XP\n".format(int(await self.ToLevel(player["Level"] + 1) * 0.30 + 1))
		if random.random() <= 0.005:
			pokeloot += await self.ToLevel(player["Level"] + 1)
			pokelootText += "You Find an **Rare candy** and you gain a level!\n"
		toPrint += pokelootText
		XP += pokeloot

		await self.addPokedex(ctx.message.author, beatEnemies)
		XP = int(XP)
		await self.bot.say(toPrint)
		await self.giveXP(ctx.message.author, XP, ctx.message.channel)
		await self.bot.say("You trained for {:,} XP!".format(XP))
		self.training[ctx.message.author.id] = time.time()

	@commands.command(pass_context=True)
	async def pokedex(self, ctx, search = ""):
		member = ctx.message.author
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER

		try:
			defeated = ALLPLAYERS[member.id]["Pokemon"]
		except:
			ALLPLAYERS[member.id]["Pokemon"] = [" "]
			defeated = ALLPLAYERS[member.id]["Pokemon"]

		pokemon = ALLPLAYERS[member.id]["Pokemon"]
		if search == "":
			await self.bot.say("Your Pokedex is {}% complete!".format(round((len(pokemon)-1) / 801 * 100, 2)))
		elif search.lower() == "list":
			await self.bot.send_message(member, "Your Pokedex contains the following pokemon: {}".format(", ".join(pokemon[1:])))
		else:
			if search.capitalize() in pokemon:
				await self.bot.say("You **have** beat a {}".format(search.capitalize()))
			else:
				await self.bot.say("You have not beat a {}".format(search.capitalize()))

	async def addPokedex(self, member, enemies):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = ALLPLAYERS[member.id]
		except:
			print("NEW PLAYER: {}".format(ctx.message.author.name))
			NEWPLAYER['Name'] = ctx.message.author.name
			ALLPLAYERS[ctx.message.author.id] = NEWPLAYER
		names = []
		for enemy in enemies:
			names.append(enemy.name)

		try:
			defeated = ALLPLAYERS[member.id]["Pokemon"]
		except:
			ALLPLAYERS[member.id]["Pokemon"] = [" "]
			defeated = ALLPLAYERS[member.id]["Pokemon"]

		pokemon = ALLPLAYERS[member.id]["Pokemon"]
		for name in names:
			if name not in defeated:
				pokemon.append(name)

		ALLPLAYERS[member.id]["Pokemon"] = pokemon

		with open('Players.json', 'w') as f:
				json.dump(ALLPLAYERS, f)

	async def getPlayer(self, member):
		with open('Players.json', 'r') as f:
			ALLPLAYERS = json.load(f)
		try:
			player = await self.checkLevel(ALLPLAYERS[member.id])
		except:
			print("NEW PLAYER: {}".format(member.name))
			NEWPLAYER['Name'] = member.name
			ALLPLAYERS[member.id] = NEWPLAYER
			player = ALLPLAYERS[member.id]

		with open('Players.json', 'w') as f:
			json.dump(ALLPLAYERS, f)

		return player


	@commands.command()
	async def types(self):
		val = """ -= **Possible Types ** =-
:regional_indicator_n: ormal\n:regional_indicator_f: ire
:regional_indicator_w: ater\n:regional_indicator_g: rass
:regional_indicator_p: oison\n:regional_indicator_d: ragon
:regional_indicator_s: teel\n:regional_indicator_e: lectric
:regional_indicator_b: ug\n:regional_indicator_i: ce"""
		await self.bot.say(val)

	async def ToLevel(self, level):
		if level >= 100:
			return 0
		return int(math.pow(level, 3))

	async def checkLevel(self, player):
		while player['XP'] >= await self.ToLevel(int(player['Level']) + 1) and player['Level'] is not 100:
			player['XP'] -= await self.ToLevel(int(player['Level']) + 1)
			player['Level'] += 1
		return player

class Boss:
	def __init__(self, level):
		self.level = random.randrange(level[0], level[1], 1)
		if self.level < 10:
			self.Moves = 5
		elif self.level < 50:
			self.Moves = 8
		elif self.level < 80:
			self.Moves = 10
		else:
			self.Moves = 15
		
		self.Health = int(1000 * self.level * self.Moves / 8 * random.randrange(75, 125, 1) / 100)
		self.StartingHealth = self.Health
		self.Name = getRandomName()
		self.Image = getImage(self.Name)
		self.Name = self.Name.capitalize()
		self.Damage = {}
		self.isDefeated = False
		self.hasBeenRevealed = False
		self.combination = [random.choice(["N","F","W","G","P","D","S","E","B","I"]) for x in range(0, self.Moves, 1)]
		self.lastUsedCombo = ""
		self.summoner = ""

	def change1(self):
		choose = random.choice(range(0, self.Moves, 1))
		self.combination[choose] = random.choice(["N","F","W","G","P","D","S","E","B","I"])

	def changeHalf(self):
		choose = random.sample(range(0, self.Moves, 1), int(self.Moves/2))
		for x in choose:
			choice = random.choice(["N","F","W","G","P","D","S","E","B","I"])
			while choice == self.combination[x]:
				choice = random.choice(["N","F","W","G","P","D","S","E","B","I"])
			self.combination[x] = choice

	def changeQuarter(self):
		choose = random.sample(range(0, self.Moves, 1), int(self.Moves/4))
		for x in choose:
			choice = random.choice(["N","F","W","G","P","D","S","E","B","I"])
			while choice == self.combination[x]:
				choice = random.choice(["N","F","W","G","P","D","S","E","B","I"])
			self.combination[x] = choice

class Enemy:
	def __init__(self, name, level):
		self.name = name.capitalize()
		self.level = level

def setup(bot):
	bot.add_cog(Games(bot))