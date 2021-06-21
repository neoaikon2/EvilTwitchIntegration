import twitch
import PySimpleGUI as sg
import time
import threading
from playsound import playsound
from random import sample, randint
from eviloverlay import EvilOverlay
from evilhacks import EvilHacks


class Pollster(object):
	chat = None;
	overlay = None;
	hacks = None;
	poll_running = False
	POLL_INTERVAL = 7.5 * 60 * 1000 # 12 minute poll intervals
	TIMEOUT = 90 * 1000 # 90 second timeout
	t = 0

	stingers = [ "snds\stinger.wav", "snds\stinger2.wav" ]
	sounds = [ "snds\yeah.wav", "snds\mad.wav", "snds\evilaugh.wav" ]
	
	# Objects to keep vote counts and also a list of people who've voted
	tally = [0, 0, 0]
	voted = []
	
	def __init__(self):
		self.overlay = EvilOverlay(self.TIMEOUT)
		self.hacks = EvilHacks()
		self.chat = twitch.Chat(channel='<Your Channel Name>', nickname='<Bot Nickname>', oauth='<Bot OAuth>')
		# Message handler
		self.chat.subscribe(lambda message: self.HandleMessages(message))
		return;
		
	def CastVote(self, vote, voter):		
		# Check to make sure this voter hasn't already cast a vote
		if voter in self.voted:
			self.chat.send("@" + voter + ", you may only vote once!")
			return
		
		# Get vote ID and make sure it's valid
		v = vote[5:6]	
		if not v.isnumeric():
			return
		vote_n = int(v)-1
		if vote_n < 0 | vote_n > 2:
			return
		
		# Cast vote and save the voters username
		self.tally[vote_n] = self.tally[vote_n] + 1
		self.voted.append(voter)
		
		total = self.tally[0] + self.tally[1] + self.tally[2]
		va = (self.tally[0]/total)*100
		vb = (self.tally[1]/total)*100
		vc = (self.tally[2]/total)*100
		self.overlay.setChoices(1, va)
		self.overlay.setChoices(2, vb)
		self.overlay.setChoices(3, vc)		
		
	# Handle recieving messages
	def HandleMessages(self, message):
		# Check for vote command
		if(message.text.startswith("!vote")):
			if len(message.text) >= 6:
				self.CastVote(message.text, message.sender)
		elif(message.text.startswith("!exit")):
			exit()
			
	# Resets the votes and voted lists
	def ResetVotes(self):		
		self.tally = [0, 0, 0]
		self.voted = []
		self.overlay.Reset()
		
	# Gets current time in MS
	def _ms(self):
		return round(time.time() * 1000)
	
	def GetRandomSample(self):
		s = sample(self.hacks.evil_hacks, 3)
		self.overlay.setText([ s[0]._name, s[1]._name, s[2]._name ])
		return s
		
	# Do a poll
	def DoPoll(self):		
		# Set the choices GUI stuff to visible, play a random stinger and get started	
		self.overlay.showChoices(True)
		playsound(sample(self.stingers, 1)[0], False)
		playsound(sample(self.sounds, 1)[0], False)
		self.poll_running = True
		
		while self.poll_running:		
			self.overlay.setTimer(self.TIMEOUT-(self._ms()-self.t)) # Update the timer progress bar
			# When the timer expires...
			if (self._ms() - self.t) > self.TIMEOUT:
				# Declare the winner
				self.poll_running = False;
				
				self.chat.send("Polls closed! The winner is: " + str(self.choices[self.tally.index(max(self.tally))]._name))
				self.overlay.setWinnerText(str(self.choices[self.tally.index(max(self.tally))]._name))
				# Show the winner text and hide the choice boxes
				self.overlay.showWinner()
				self.hacks.Trigger(self.choices[self.tally.index(max(self.tally))], self.tally.index(max(self.tally)))				
				break
			time.sleep(.100)
			
	choices = []
	def Run(self):
		# Preset t variable
		self.t = self._ms()-self.POLL_INTERVAL-self.TIMEOUT;

		# Main GUI Loop
		while True:
			events, values = self.overlay.Update()
			if events == sg.WIN_CLOSED or events == 'Exit':		
				break
			# If the poll isn't running
			if not self.poll_running:		
				# Check to see if the poll interval has lapsed				
				if (self._ms() - self.t) > self.TIMEOUT + self.POLL_INTERVAL:
					# Get a random sample of hacks, update t to the latest time value
					self.choices = self.GetRandomSample()
					self.t = self._ms()
					# Reset
					self.ResetVotes()
					self.poll_running = False
					# ... An start the pool thread
					p = threading.Thread(target=self.DoPoll)
					p.start()
					
					# Let chat know what's going on!
					self.chat.send("Polls are open! Choices should be on-screen! Vote with !vote1, !vote2, or !vote3. Polls close in "+str(self.TIMEOUT/1000)+" seconds!")
			# Slight delay
			time.sleep(.100)


pollster = Pollster()
pollster.Run();