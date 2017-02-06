from Redeem.RedeemUtil import TypeTable, Reward

class RewardList():
	def __init__(self):
		self.tTable = TypeTable()

	### Rewards for Packs
	def makeTable(self):
		Ranch_Block = Reward("Ranch Block", [], 50)
		Ranch_Upgrade = Reward("Ranch Upgrade", [], 600)
		Everstone = Reward("Everstone", [], 125)
		Destiny_Knot = Reward("Destiny Knot", [], 125)
		Stack_Of_Pokeballs = Reward("Choice of any Stack of Pokeballs (Not MBall, Cherish, or Park Ball)", [], 500)
		Park_Ball = Reward("Park Ball", [], 2500)
		Stack_Of_Quartz = Reward("Stack of Quartz Blocks", [], 150)
		Stack_Of_Temple_Blocks = Reward("Stack Of Temple Blocks", [], 300)
		Stack_Of_Sea_Lantern = Reward("Stack Of Sea Lantern", [], 600)
		Stack_Of_Glowstone = Reward("Stack of Glowstone", [], 150)
		Eight_Rare_Candy = Reward("Eight Rare Candy", [], 400)
		Power_Ankelt = Reward("Power Anklet", [], 300)
		Power_Band = Reward("Power Band", [], 250)
		Power_Belt = Reward("Power Belt", [], 250)
		Power_Bracer = Reward("Power Bracer", [], 275)
		Power_Lens = Reward("Power Lens", [], 275)
		Power_Weight = Reward("Power Weight", [], 275)
		Lucky_Egg = Reward("Lucky Egg", [], 400)
		Quarter_Stack_Of_Diamond = Reward("16 Diamond", [], 560)
		Half_Stack_Of_Gold = Reward("32 Gold Ingot", [], 650)
		Stack_Of_Iron = Reward("Stack of Iron Ingot", [], 400)
		Stack_Of_Lapis = Reward("Stack of Lapis", [], 100)
		Stack_Of_Redstone = Reward("Stack of Redstone", [], 75)
		Stack_Of_Coal = Reward("Stack of Coal", [], 50)
		Pixelmon_Gem_Block = Reward("Pixelmon Gem Block", [], 40)
		Horse_Egg = Reward("Horse Egg", [], 750)
		Wolf_Egg = Reward("Wolf Egg", [], 750)
		Ocelot_Egg = Reward("Ocelot Egg", [], 750)
		Beacon = Reward("Beacon", [], 2500)
		FiveK = Reward("$5000", [], 5000)
		Ditto = Reward("Ditto", [], 1200)
		Diamond_Hammer = Reward("Diamod Hammer", [], 75)



		### Legendaries
		self.tTable.Legendary.Rewards = [
		Reward('Rayquaza',[],10000),
		Reward('Groudon',[],8000),
		Reward('Kyogre',[],8000),
		Reward('Articuno',[],2000),
		Reward('Mewtwo',[],8000),
		Reward('Entei',[],5000),
		Reward('Suicune',[],6000),
		Reward('Raikou',[],5000),
		Reward('Zapdos',[],3000),
		Reward('Celebi',[],4000),
		Reward('Cloned Mew',[],6000),
		Reward('Ho-oh',[],10000),
		Reward('Lugia',[],8000),
		Reward('Moltres',[],4000),
		Reward('UnCloned Mew',[],22000),
		Reward('Registeel', [], 10000),
		Reward('Regirock', [], 10000),
		Reward('Regice', [], 10000),
		Reward('Regigias', [], 140000)
		]

		Random_Legendary = Reward("Random Legendary", [], round(self.tTable.Legendary.getAverageValue(),2))

		self.tTable.Item.Rewards = [
		Reward("Choice Scarf", [], 250),
		Reward("Choice Band", [], 250),
		Reward("Choice Specs", [], 250),
		Destiny_Knot,
		Reward("Eviolite", [], 200),
		Reward("Exp. Share", [], 450),
		Reward("Expert Belt", [], 200),
		Reward("Focus Sash", [], 400),
		Reward("Leftovers", [], 400),
		Reward("Life orb", [], 550),
		Lucky_Egg,
		Reward("Muscle Band", [], 200),
		Power_Ankelt,
		Power_Band,
		Power_Bracer,
		Power_Lens,
		Power_Weight,
		Power_Belt,
		Reward("Rocky Helmet", [], 500),
		Reward("Wise Glasses", [], 300),
		Reward("Master Ball", [], 2000),
		Park_Ball
		]

		self.tTable.TM.Rewards = [
		Reward("TM02: Dragon Claw", [], 50),
		Reward("TM03: Psyshock", [], 400),
		Reward("TM04: Calm Mind", [], 200),
		Reward("TM05: Roar", [], 10),
		Reward("TM06: Toxic", [], 50),
		Reward("TM07: Hail", [], 50),
		Reward("TM08: Bulk Up", [], 10),
		Reward("TM10: Hidden Power", [], 10),
		Reward("TM11: Sunny Day", [], 10),
		Reward("TM12: Taunt", [], 100),
		Reward("TM13: Ice Beam", [], 1000),
		Reward("TM14: Blizzard", [], 100),
		Reward("TM15: Hyper Beam", [], 60),
		Reward("TM16: Light Screen", [], 50),
		Reward("TM17: Protect", [], 500),
		Reward("TM18: Rain Dance", [], 200),
		Reward("TM22: SolarBeam", [], 400),
		Reward("TM24: Thunderbolt", [], 500),
		Reward("TM25: Thunder", [], 400),
		Reward("TM26: Earthquake", [], 1200),
		Reward("TM27: Return", [], 50),
		Reward("TM29: Psychic", [], 750),
		Reward("TM30: Shadow Ball", [], 750),
		Reward("TM31: Brick Break", [], 400),
		Reward("TM33: Reflect", [], 50),
		Reward("TM34: Sludge Wave", [], 10),
		Reward("TM35: Flamethrower", [], 600),
		Reward("TM36: Sludge Bomb", [], 50),
		Reward("TM37: Sandstorm", [], 20),
		Reward("TM38: Fire Blast", [], 50),
		Reward("TM42: Facade", [], 70),
		Reward("TM43: Flame Charge", [], 30),
		Reward("TM44: Rest", [], 80),
		Reward("TM45: Attract", [], 20),
		Reward("TM50: Overheat", [], 60),
		Reward("TM52: Focus Blast", [], 200),
		Reward("TM53: Energy Ball", [], 300),
		Reward("TM54: False Swipe", [], 300),
		Reward("TM55: Scald", [], 600),
		Reward("TM61: Will-O-Wisp", [], 100),
		Reward("TM62: Acrobatics", [], 200),
		Reward("TM64: Explosion", [], 50),
		Reward("TM65: Shadow Claw", [], 100),
		Reward("TM66: Payback", [], 50),
		Reward("TM68: Giga Impact", [], 70),
		Reward("TM69: Rock Polish", [], 20),
		Reward("TM71: Stone Edge", [], 300),
		Reward("TM72: Volt Switch", [], 50),
		Reward("TM73: Thunder Wave", [], 200),
		Reward("TM74: Gyro Ball", [], 50),
		Reward("TM75: Swords Dance", [], 200),
		Reward("TM80: Rock Slide", [], 100),
		Reward("TM81: X-Scissor", [], 150),
		Reward("TM82: Dragon Tail", [], 70),
		Reward("TM84: Poison Jab", [], 80),
		Reward("TM86: Grass Knot", [], 100),
		Reward("TM87: Swagger", [], 50),
		Reward("TM89: U-Turn", [], 100),
		Reward("TM90: Substitute", [], 100),
		Reward("TM91: Flash Cannon", [], 50),
		Reward("TM92: Trick Room", [], 60),
		Reward("TM93: Wild Charge", [], 30),
		Reward("TM98: Whirlwind", [], 10),
		Reward("TM99: Mega Kick", [], 40),
		Reward("TM100: Horn Drill", [], 30),
		Reward("TM101: Body Slam", [], 20),
		Reward("TM103: Double-Edge", [], 20),
		Reward("TM108: Counter", [], 100),
		Reward("TM113: Fissure", [], 70),
		Reward("TM123: Sky Attack", [], 20),
		Reward("TM126: DynamicPunch", [], 70),
		Reward("TM128: Curse", [], 100),
		Reward("TM130: Zap Cannon", [], 40),
		Reward("TM133: Icy Wind", [], 10),
		Reward("TM134: Giga Drain", [], 100),
		Reward("TM136: Iron Tail", [], 20),
		Reward("TM139: Ice Punch", [], 50),
		Reward("TM140: Sleep Talk", [], 10),
		Reward("TM142: Thunder Punch", [], 60),
		Reward("TM143: Detect", [], 100),
		Reward("TM145: Fire Punch", [], 40),
		Reward("TM148: Focus Punch", [], 40),
		Reward("TM155: Roost", [], 50),
		Reward("TM157: Dragon Pulse", [], 70),
		Reward("TM158: Drain Punch", [], 60),
		Reward("TM161: Avalanche", [], 20),
		Reward("TM162: Stealth Rock", [], 200),
		Reward("TM164: Dark Pulse", [], 200),
		Reward("HM02: Fly", [], 10),
		Reward("HM03: Surf ", [], 20),
		Reward("HM07: Waterfall",[], 100)
		]

		self.tTable.Money.Rewards = [
		Reward('$1000', [], 1000),
		Reward('$1100', [], 1100),
		Reward('$1200', [], 1200),
		Reward('$1300', [], 1300),
		Reward('$1400', [], 1400),
		Reward('$1500', [], 1500),
		Reward('$1600', [], 1600),
		Reward('$1700', [], 1700),
		Reward('$1800', [], 1800),
		Reward('$1900', [], 1900),
		Reward('$2000', [], 2000),
		Reward('$2100', [], 2100),
		Reward('$2200', [], 2200),
		Reward('$2300', [], 2300),
		Reward('$2400', [], 2400),
		Reward('$2500', [], 2500),
		Reward('$2600', [], 2600),
		Reward('$2700', [], 2700),
		Reward('$2800', [], 2800),
		Reward('$2900', [], 2900),
		Reward('$3000', [], 3000),
		Reward('$3100', [], 3100),
		Reward('$3200', [], 3200),
		Reward('$3300', [], 3300),
		Reward('$3400', [], 3400),
		Reward('$3500', [], 3500),
		Reward('$3600', [], 3600),
		Reward('$3700', [], 3700),
		Reward('$3800', [], 3800),
		Reward('$3900', [], 3900),
		Reward('$4000', [], 4000),
		Reward('$4100', [], 4100),
		Reward('$4200', [], 4200),
		Reward('$4300', [], 4300),
		Reward('$4400', [], 4400),
		Reward('$4500', [], 4500),
		Reward('$4600', [], 4600),
		Reward('$4700', [], 4700),
		Reward('$4800', [], 4800),
		Reward('$4900', [], 4900),
		Reward('$5000', [], 5000)
		]

		self.tTable.Pack.Rewards = [
		Reward("Breeding Pack", 
			[Ditto] + [Ranch_Block] + [Ranch_Upgrade]*4 + [Everstone] + [Destiny_Knot], 
			Ditto.Value + Ranch_Block.Value + Ranch_Upgrade.Value*4 + Everstone.Value + Destiny_Knot.Value),
		Reward("PokeBall Pack", 
			[Stack_Of_Pokeballs]*2+ [Park_Ball] + [Diamond_Hammer],
			Stack_Of_Pokeballs.Value * 2 + Park_Ball.Value + Diamond_Hammer.Value),
		Reward("Building Pack", 
			[Stack_Of_Quartz]*10 + [Stack_Of_Temple_Blocks]*2 + [Stack_Of_Sea_Lantern] + [Stack_Of_Glowstone], 
			Stack_Of_Quartz.Value*10 + Stack_Of_Temple_Blocks.Value*2 + Stack_Of_Sea_Lantern.Value + Stack_Of_Glowstone.Value),
		Reward("Training Pack", 
			[Eight_Rare_Candy]*2+ [Power_Belt,Power_Ankelt,Power_Band,Power_Bracer,Power_Lens,Power_Weight] + [Lucky_Egg], 
			Eight_Rare_Candy.Value*2+ Power_Belt.Value + Power_Ankelt.Value + Power_Band.Value +Power_Bracer.Value +Power_Lens.Value +Power_Weight.Value + Lucky_Egg.Value),
		Reward("Treasure Pack", 
			[Quarter_Stack_Of_Diamond] + [Half_Stack_Of_Gold] + [Stack_Of_Iron] + [Stack_Of_Lapis]*2 + [Stack_Of_Redstone]*2 + [Stack_Of_Coal]*4 + [Pixelmon_Gem_Block]*4, 
			Quarter_Stack_Of_Diamond.Value + Half_Stack_Of_Gold.Value + Stack_Of_Iron.Value + Stack_Of_Lapis.Value*2 + Stack_Of_Redstone.Value*2 + Stack_Of_Coal.Value*4 + Pixelmon_Gem_Block.Value*4),
		Reward("Companion Pack", 
			[Horse_Egg]*2 + [Wolf_Egg]*2 + [Ocelot_Egg]*2, 
			Horse_Egg.Value*2 + Wolf_Egg.Value*2 + Ocelot_Egg.Value*2)
		]

		Random_Pack = Reward("Random Pack", [], round(self.tTable.Pack.getAverageValue(),2))

		self.tTable.Jackpot.Rewards = [
		Reward("Jackpot Prize", [Beacon, FiveK, Random_Legendary, Random_Pack], Beacon.Value + FiveK.Value + round(Random_Legendary.Value,2) + round(Random_Pack.Value,2))
		]

		#print(self.tTable.values())
	def Table():
		return self.tTable