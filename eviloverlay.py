import PySimpleGUI as sg
import time
import threading

class EvilOverlay(object):
	window = None
	TIMEOUT = 30 * 1000 # 90 second timeout
	WINNER_TIMEOUT = 3	
	
	def __init__(self, TIMEOUT):				
		self.TIMEOUT = TIMEOUT
		
		tmpCol = [[sg.Column([[sg.ProgressBar(TIMEOUT, bar_color=("#FF6C11", "#6441A4"), size=(60,15), pad=(10,6), key=0)]], justification="center", background_color="#00DD00")],
		[sg.Column([
			[sg.ProgressBar(100, bar_color=("#FF6C11", "#6441A4"), size=(20,15), pad=(10,6), key=1)],
			[sg.Text("Choice 1", justification="center", size=(20,1), pad=(10,6), key='c1')]
		], background_color="#2E2157"), sg.Column([
			[sg.ProgressBar(100, bar_color=("#FF6C11", "#6441A4"), size=(20,15), pad=(10,6), key=2)],
			[sg.Text("Choice 2", justification="center", size=(20,1), pad=(10,6), key='c2')]
		], background_color="#2E2157"), sg.Column([
			[sg.ProgressBar(100, bar_color=("#FF6C11", "#6441A4"), size=(20,15), pad=(10,6), key=3)],
			[sg.Text("Choice 3", justification="center", size=(20,1), pad=(10,6), key='c3')]
		], background_color="#2E2157")]]
		tmpLayout = [[sg.Column(tmpCol, justification="center", background_color="#00DD00",key='Choices')]
		, [sg.Column([[sg.Text("", size=(1,15), background_color="#00DD00")], [sg.Text("WINNER!", font=("Cyberpunk Is Not Dead", 36), size=(32,1), background_color="#6441A4", key='Winner', justification="center")]], background_color="#00DD00")
		]]
		# Create our window, use a Window Capture to grab this for a OBS stream;
		self.window = sg.Window(title="Evil Genius Twitch Integration", layout=tmpLayout, background_color="#00DD00", size=(1200,720))
		self.window.Read(timeout=100)
		self.window['Choices'].Update(visible=False)
		self.window['Winner'].Update(visible=False)		
		
	def Update(self):
		events, values = self.window.Read(timeout=100)
		return events, values
		
	def showChoices(self, state):
		self.window['Choices'].Update(visible=state)
		
	def setChoices(self, idx, val):
		self.window[idx].UpdateBar(val)
		
	def setText(self, tuple_val):
		self.window['c1'].update(tuple_val[0])
		self.window['c2'].update(tuple_val[1])
		self.window['c3'].update(tuple_val[2])	
		
	def setTimer(self, val):
		self.setChoices(0, val)
		
	def hideWinner(self):
		time.sleep(self.WINNER_TIMEOUT)
		self.window['Winner'].Update(visible=False)	
	
	def setWinnerText(self, val):
		self.window['Winner'].update(val)
	
	def Reset(self):
		for i in range(1, 4):
			self.setChoices(i, 0);
	
	def showWinner(self):
		self.window['Choices'].Update(visible=False)
		self.window['Winner'].Update(visible=True)
		p = threading.Thread(target=self.hideWinner)
		p.start()