import time;
import threading
import pymem
import pyttsx3
from random import sample, randint

class GoldHack(object):
	_name = "Gold Thieves"
	pointer = 0x141CDA5A8
	offsets = [ 0x60, 0x00 ]
	addrLoc = 0x00;
	factor = .925;
	
	def __init__(self, game):
		self.addrLoc = game.read_ulonglong(game.read_ulonglong(self.pointer)+self.offsets[0])+self.offsets[1]
		
	def Trigger(self, game, votes):
		gold = game.read_int(self.addrLoc)
		for i in range(0, votes):
			gold *= self.factor;
		game.write_int(self.addrLoc, int(gold));

class PowerHack(object):
	_name = "Power Outage"
	pointer = 0x141CDA540
	offsets = [ 0xA0, 0xC8 ]	
	addrLocs = [];
	FUNTIME = 60;
	
	def __init__(self, game):		
		for o in self.offsets:
			self.addrLocs.append(game.read_ulonglong(self.pointer)+o)
	
	def Restore(self, game):
		time.sleep(self.FUNTIME)
		self.tmpPower += game.read_int(self.addrLocs[0])
		self.tmpEmerg += game.read_int(self.addrLocs[1])
		game.write_int(self.addrLocs[0], self.tmpPower)
		game.write_int(self.addrLocs[1], self.tmpEmerg)
		
	tmpPower = 0;
	tmpEmerg = 0;
	def Trigger(self, game):		
		self.tmpPower = game.read_int(self.addrLocs[0])
		self.tmpEmerg = game.read_int(self.addrLocs[1])
		game.write_int(self.addrLocs[0], 0)
		game.write_int(self.addrLocs[1], 0)
		p = threading.Thread(target=self.Restore, args=[game])
		p.start()
		
#class RadioHack(object):

class Patch(object):
	_name = "Patch"
	locs = [];
	data = [];
	FUNTIME = 60;
	
	def writeNops(self, game, addr, data):
		if(isinstance(addr, int)):			
			l = len(data)
			game.write_bytes(addr, bytes([0x90 for j in range(l)]), l)
		else:
			for i in range(0,len(addr)):
				l = len(data[i])
				game.write_bytes(addr[i], bytes([0x90 for j in range(l)]), l)

	def writeData(self, game, addr, data):
		if(isinstance(addr, int)):			
			game.write_bytes(addr, data, len(data))
		else:
			for i in range(0,len(addr)):
				game.write_bytes(addr[i], data[i], len(data[i]))
			
	# UPDATE: Check these bytes when the game gets updated
	cw_dat = bytes([ 0x74, 0x07 ])
	def closeWindows(self, game):
		self.writeNops(game, 0x14083956B, self.cw_dat)
		time.sleep(.01)
		self.writeData(game, 0x14083956B, self.cw_dat)
	
	def __init__(self, game, name, locs, sizes):		
		self._name = name
		self.locs = locs;		
		for i in range(0,len(locs)):
			self.data.append(game.read_bytes(self.locs[i], sizes[i]))
			
	def Restore(self, game):
		time.sleep(self.FUNTIME)
		self.writeData(game, self.locs, self.data)
		
	def Trigger(self, game):
		self.closeWindows(game)
		time.sleep(.032)
		self.writeNops(game, self.locs, self.data)
		p = threading.Thread(target=self.Restore, args=[game])
		p.start()
	
class PatchInstructions(Patch):
	_name = "PatchAdv"
	locs = [];
	data = [];
	hack = [];
	
	def __init__(self, game, name, locs, sizes, hack):
		self._name = name
		self.hack = hack;
		super(PatchInstructions, self).__init__(game, name, locs, sizes)
	
	def Restore(self, game):
		time.sleep(.01)
		self.writeData(game, self.locs, self.data)
	
	def Trigger(self, game):
		self.closeWindows(game)
		time.sleep(.032)
		self.writeData(game, self.locs, self.hack)
		p = threading.Thread(target=self.Restore, args=[game])
		p.start()
		
class SpawnSuperAgent():
	_name = "Super Agent"
	pointer = 0x141B07730
	offset = 0x3C
	locs = [ 0x1407940C0, 0x1407940D1, 0x1408757F8, 0x1408758AC, 0x140868BAE ]
	hack = [
		bytes([ 0x90, 0x90 ]),
		bytes([ 0x90, 0x90 ]), 
		bytes([ 0xE9, 0xA5, 0x00, 0x00, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 ]), 
		bytes([ 0xB8, 0x4, 0x3, 0x2, 0x1, 0x90 ]), 
		bytes([ 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x88, 0x05, 0x08, 0x24, 0x47, 0x01, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 ])
	]
	sizes = [ 2, 2, 12, 6, 20 ]
	
	patch = None;	
	
	def __init__(self, game):
		self.patch = PatchInstructions(game, self._name, self.locs, self.sizes, self.hack)
	
	last_refAgent = None
	def Trigger(self, game):
		
		baseAddress = game.read_ulonglong(self.pointer) + self.offset;
		try:
			refAgent = game.read_bytes(baseAddress, 4)
		except pymem.exception.MemoryReadError:
			print("Failed to lure a super agent...")
				
		if((self.last_refAgent == game.read_int(baseAddress)) | (game.read_int(baseAddress) == 0xEB830AD8)):
			return
			
		self.last_refAgent = refAgent;		
		self.hack[3] = bytes([ 0xB8, refAgent[0], refAgent[1], refAgent[2], refAgent[3], 0x90 ])		
		self.patch.Trigger(game, self.hack)
		time.sleep(.1)
		self.patch.closeWindows(game)

class EvilHacks(object):
		
	locsFreezeCam = [ 0x14064DB4C, 0x14064F11A ]
	sizeFreezeCam = [ 10, 13 ]
	locsResearch = [ 0x14059B6A5, 0x158D0BC7F ]
	sizeResearch = [ 24, 21 ]
	hackResearch = [
		bytes( [ 0xBF, 0x60, 0x80, 0x00, 0x00, 0x41, 0xBC, 0x0A, 0x80, 0x00, 0x00, 0x8B, 0xC7, 0x90, 0x90, 0x90, 0x90, 0x90, 0xE9, 0x77, 0x01, 0x00, 0x00, 0x90 ] ),
		bytes( [ 0x45, 0x31, 0xC0, 0x41, 0xFF, 0xC0, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 ] )
	]
	
	goldInsults = [ 
		"Say goodbye to your gold, that's what you get. Try not to cry",
		"Bend over and prepare your anus, it's tax time!",
		"You won't miss this gold, right? Too bad, dickhead"
	]

	researchInsults = [
		"Who needs science anyways, certainly not you! Loser",
		"This is what happens when you believe in a flat earth you idiot",
		"Your scientists are on strike, maybe you should pay them more"
	]

	powerInsults = [
		"What? did you forget to pay your electric bill? Sucks to be you, loser!",
		"No amount of generators is going the save you from your own stupidity",
		"Power out again? You must be really bad at this game if that keeps happening..."
	]
	
	freezeInsults = [
		"Take a break, maybe you can figure out why you suck so bad at this game",
		"Caught by the camera police again? Stop taking so many dabs and this wouldn't happen",
		"They broke the camera, you have to suffer. Tis the circle of Twitch pain"
	]
	
	agentInsults = [
		"I hope you've prepared your anus for the fucking you're about to receive",
		"The ass pounding you ordered has arrived, bend over and take it",
		"World domination? That's a paddling, drop your trousers and get ready"
	]
	
	evilgame = None;
	tts = None;
	evil_hacks = [];
	initialized = False;	
	
	def __init__(self):	
		self.tts = pyttsx3.init()
		try:
			self.evilgame = pymem.Pymem("evilgenius_dx12.exe")
		except pymem.exception.ProcessError:
			print("Evil Genius 2 isn't running...")
			print("You gotta have the game open first dingus!")
			exit()
		
		self.evil_hacks = [
			GoldHack(self.evilgame), # Gold Thieves
			PowerHack(self.evilgame), # Power Outage
			PatchInstructions(self.evilgame, "Revoke Funding", self.locsResearch, self.sizeResearch, self.hackResearch), # Revoke Funding
			Patch(self.evilgame, "Freeze Frame", self.locsFreezeCam, self.sizeFreezeCam), # Freeze Frame
			SpawnSuperAgent(self.evilgame) # Super Agents
		]		
		initialized = True;
		
	def speak(self, txt):
		self.tts.say(txt)
		self.tts.runAndWait()
	
	def Trigger(self, hack, votes):
		if(hack._name == self.evil_hacks[0]._name):
			self.speak(sample(self.goldInsults, 1))		
			hack.Trigger(self.evilgame, votes)
		elif(hack._name == self.evil_hacks[1]._name):
			self.speak(sample(self.powerInsults, 1))
			hack.Trigger(self.evilgame)
		elif(hack._name == self.evil_hacks[2]._name):
			self.speak(sample(self.researchInsults, 1))
			hack.Trigger(self.evilgame)
		elif(hack._name == self.evil_hacks[3]._name):
			self.speak(sample(self.freezeInsults, 1))
			hack.Trigger(self.evilgame)
		elif(hack._name == self.evil_hacks[4]._name):
			self.speak(sample(self.agentInsults, 1))
			hack.Trigger(self.evilgame)
		
hacks = EvilHacks()
hacks = None;