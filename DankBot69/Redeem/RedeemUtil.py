from Redeem.ActiveCodes import *
#from Redeem.RewardTable import *
import random

RDCodes = []

def CollectRDCodes():
	f = open("./Redeem./Resc./" + "Usedcodes.txt", 'r')
	#RDCodes = []
	for line in f:
		if(int(line[:9]) not in RDCodes):
			RDCodes.append(int(line[:9]))
	f.close()

def isValid(Code:int):
	#print(RDCodes)
	if Code in Codes and Code not in RDCodes:
		if Code in HalfCodes:
			return "HALF"
		elif Code in OneCodes:
			return "ONE"
		elif Code in TwoCodes:
			return "TWO"
		elif Code in FiveCodes:
			return "FIVE"
		return "WRONG"
	elif Code in RDCodes:
	 	return "USED"
	elif Code < 0:
		return "TEST"
	else:
		return "INVALID"

def getPrice(res:str):
	return {
	"One" : "$1000",
	"Two" : "$2000",
	"Five" : "$5000",
	"TESTONE" : "TESTING $1000",
	"TESTTWO" : "TESTING $2000",
	"TESTFIVE" : "TESTING $5000",
	}.get(res, "$0")

# Reward Objects
# Lowest Level Object
class Reward():
	def __init__(self, name, contents, value):
		self.Value = value
		self.Name = name
		self.Contents = contents

	def getValue(self):
		return self.Value
	def getContents(self):
		return self.Contains
	def getName(self):
		return self.Name
	def __str__(self):
		if(len(self.Contents) != 0):
			ret = ""
			ret += "### {}, ${}".format(self.Name, self.Value)
			ret += "\n#### Contains: "
			for x in self.Contents:
				ret += "\n"
				ret += str(x)
			ret += "\n"
		else:
			ret = ""
			ret += "- {}, ${}".format(self.Name, self.Value)
		return ret

# Type Objects
# Contains Individual Rewards
class Type():
	def __init__(self):
		self.Rewards = []
		self.AvgValue = 0

	def getAverageValue(self):
		global AvgValue
		AvgValue = 0
		for r in self.Rewards:
			AvgValue += r.getValue()
		AvgValue = AvgValue / len(self.Rewards)
		return AvgValue

	def add(self, reward:Reward):
		self.Rewards.append(reward)

	def all(self):
		ret = ""
		for x in self.Rewards:
			ret += str(x) + "\n"
		return ret

	def getReward(self):
		return random.choice(self.Rewards)
	
class DropTable():
	DropRates = {
	"HALF" :	[150,38,5 ,3 ,2 ,1 ],
	"ONE"  : 	[47 ,37,10,3 ,2 ,1 ],
	"TWO"  : 	[31 ,26,21,14,7 ,1 ],
	"FIVE" : 	[7  ,15,18,21,33,6 ]
	}

	def getDrop(self, Price:str):
		rate = self.DropRates[Price]
		return random.choice(["TM"]*rate[0] + ["Item"]*rate[1] + ["Money"]*rate[2] + ["Pack"]*rate[3] + ["Legendary"]*rate[4] + ["Jackpot"]*rate[5])

	def printValues(self, Price:str):
		rate = self.DropRates[Price]
		if(Price != "HALF"):
			return "**{}**: TM: {}%, Item: {}%, Money: {}%, Pack: {}%, Legendary: {}%, Jackpot: {}%".format(Price, rate[0],rate[1],rate[2],rate[3],rate[4],rate[5])
		else:
			return "**{}**: TM: {}%, Item: {}%, Money: {}%, Pack: {}%, Legendary: {}%, Jackpot: {}%".format(Price, rate[0]/2,rate[1]/2,rate[2]/2,rate[3]/2,rate[4]/2,rate[5]/2)

	def markdownPrintValues(self, Price:str):
		rate = self.DropRates[Price]
		if(Price != "HALF"):
			return """#### {}: 
TM: {}%, Item: {}%, Money: {}%, Pack: {}%, Legendary: {}%, Jackpot: {}%""".format(Price, rate[0],rate[1],rate[2],rate[3],rate[4],rate[5])
		else:
			return """#### {}: 
TM: {}%, Item: {}%, Money: {}%, Pack: {}%, Legendary: {}%, Jackpot: {}%""".format(Price, rate[0]/2,rate[1]/2,rate[2]/2,rate[3]/2,rate[4]/2,rate[5]/2)

	def __str__(self):
		return self.markdownPrintValues("HALF") + '\n' + self.markdownPrintValues("ONE") + '\n' + self.markdownPrintValues("TWO") + '\n' + self.markdownPrintValues("FIVE")
			

class TypeTable():
	def __init__(self):
		self.TM = Type()
		self.Item = Type()
		self.Money = Type()
		self.Pack = Type()
		self.Legendary = Type()
		self.Jackpot = Type()

	def values(self):
		return(
"""Values: 
TM:\t{}
Items:\t{}
Money:\t{}
Pack:\t{}
Legendary:\t{}
Jackpot:\t{}""".format(round(self.TM.getAverageValue(),2),round(self.Item.getAverageValue(),2),round(self.Money.getAverageValue(),2),round(self.Pack.getAverageValue(),2),round(self.Legendary.getAverageValue(),2),round(self.Jackpot.getAverageValue(),2))
)