from Redeem.RedeemUtil import *
from Redeem.Rewards import *


class RewardTable():
	def __init__(self):
		self.RList = RewardList()
		self.RList.makeTable()
		self.TypeTable = self.RList.tTable
		self.DropTable = DropTable()

	def getDrop(self, Value:str):
		drop = self.DropTable.getDrop(Value)

		ret = {
			'TM':self.TypeTable.TM.getReward(),
			'Item':self.TypeTable.Item.getReward(),
			'Money':self.TypeTable.Money.getReward(),
			'Pack':self.TypeTable.Pack.getReward(),
			'Legendary':self.TypeTable.Legendary.getReward(),
			'Jackpot':self.TypeTable.Jackpot.getReward()
		}.get(drop)
		return ret

	def getValues(self):
		return(self.TypeTable.values())

	def getPercents(self):
		return str(self.DropTable)

	def printDrops(self, name:str):
		TM = ["TM", "Tm", "tm","TMs", "Tms", "tms"]
		ITEM = ["ITEM", "Item", "item", "ITEMS", "Items", "items"]
		MONEY = ["MONEY", "Money", "money"]
		PACK = ["PACK", "Pack", "pack", "PACKS", "Packs", "packs"]
		LEGEND = ["LEGENDARY", "Legendary", "legendary", "LEGEND", "Legend", "legend"]
		JACKPOT = ["JACKPOT", "Jackpot", "jackpot"]
		if name in TM:
			return self.TypeTable.TM.all()
		elif name in ITEM:
			return self.TypeTable.Item.all()
		elif name in MONEY:
			return self.TypeTable.Money.all()
		elif name in PACK:
			return self.TypeTable.Pack.all()
		elif name in LEGEND:
			return self.TypeTable.Legendary.all()
		elif name in JACKPOT:
			return self.TypeTable.Jackpot.all()

	def __str__(self):
		ret = "## DropRates\n"
		ret += str(self.DropTable)
		ret += "\n\n## TMs\n"
		ret += self.TypeTable.TM.all()
		ret += "\n## ITEMS\n"
		ret += self.TypeTable.Item.all()
		ret += "\n## MONEY\n"
		ret += self.TypeTable.Money.all()
		ret += "\n## PACK\n"
		ret += self.TypeTable.Pack.all()
		ret += "\n## LEGENDARY\n"
		ret += self.TypeTable.Legendary.all()
		ret += "\n## JACKPOT\n"
		ret += self.TypeTable.Jackpot.all()
		return ret

