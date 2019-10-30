# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class ConfigCustomizerWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intendedY = 0
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]
		self.intendedX = 0
		self.intendedHeight = self.manager.stdscr.getmaxyx()[0]
		self.isOpen = False
		self.window.erase()
		self.keepWindowInMainScreen()
		if self.isOpen == False:
			self.panel.hide()
		else:
			self.panel.top()
		self.currentOption = 0
		self.viewportY = 0
	def update(self):
		self.window.erase()
		"""
		self.intendedWidth = len("Customize Highlight Colors")+2
		self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
		self.intendedHeight = 19
		"""
		self.keepWindowInMainScreen()
		
		if self.isOpen == False:
			if self.panel.hidden == False:
				self.panel.hide()
		
		else:
			self.panel.top()
			"""
			self.window.addnstr(1,1,"Customize Highlight Colors", self.window.getmaxyx()[1]-1, self.manager.curses.color_pair(0))
			for color in self.manager.Objects["config"].options["ColorMap"]:
				self.window.addnstr(2+int(color),6,str(self.manager.Objects["config"].options["ColorMap"][color]),self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(int(self.manager.Objects["config"].options["ColorMap"][color])))
				self.window.addnstr(2+int(color),1,color,self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(0))
				if self.currentOption == int(color):
					self.window.chgat(2+int(color),1,1,self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
			"""
			self.editDict(self.manager.Objects["config"].options,"Config Customizer")

	def toggle(self):
		if self.isOpen == True:
			self.isOpen = False
		else:
			self.isOpen = True

	def editDict(self,d,name="Dictionary Editor"):
		self.window.erase()
		self.currentOption = 0
		self.viewportY = 0
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]
		self.intendedHeight = self.manager.stdscr.getmaxyx()[0]
		self.intendedX = 0
		if name == "Color Customizer":
			self.intendedHeight = len(d.keys())+3
			self.intendedWidth = max(len(str(len(d.keys()))+"\t#"),len("Color Customizer")+2)
			# intendedWidth explained: d.keys will return a number with as many digits..
			self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
		
		self.keepWindowInMainScreen()
		self.window.box()
			
		# HAVE to consider screensize. self.window.getmaxyx() at this point should be happily computed.
		# if we wanna config on small displays, do we need scrolling?.....
		# yes. we can do that after we get it displaying based on maxyx.
		if self.window.getmaxyx()[0] <= 2 or self.window.getmaxyx()[1] <= 2:
			return # window is too small to print anything so quit while we're ahead.
		self.window.addnstr(1,1,name,self.window.getmaxyx()[1]-2,self.manager.curses.A_STANDOUT)
		optionKeys = []
		for key in d:
			optionKeys.append(key) # append each config dictionary key to a list. # turns out this was redundant, {}.keys exists woops
			
		# Explaining some possibly hard to read code;
		# this for loop increments i over a range of 1...windowMaxY to do the following with i:
		# 1) ensure that i+viewportY (to be used in optionKeys index) won't exceed optionKeys max index
		# 2) check type of value at optionKeys[i+viewportY-1], if dict or list, show value as ...
		#    (... is to indicate that another config menu will come up and pressing Enter is needed.)
		# 3) add text to screen row i+1 for windowMaxX-2 characters
		#    (+1 since title takes up row 1, row 0 is box but accounted for since range begins at 1)
		#    (-2 since text is offset by 1 to not print over box, and to not print on the box 1 off from the right border)
		# 4) if current line in loop is one with currentOption on it, highlight the key text
		for i in range(1,self.window.getmaxyx()[0]-1): # for each line of window after title text				
			if i+self.viewportY-1 >= len(optionKeys):
				break
			if str(type(d[optionKeys[i+self.viewportY-1]])).split("'")[1] != "dict" and str(type(d[optionKeys[i+self.viewportY-1]])).split("'")[1] != "list":
				self.window.addnstr(i+1,1,str(optionKeys[i+self.viewportY-1]+"\t"+str(d[optionKeys[i+self.viewportY-1]])).expandtabs(self.manager.Objects["config"].options["TabExpandSize"]),self.window.getmaxyx()[1]-2)
				if name == "Color Customizer" and self.window.getmaxyx()[1] > len(str(optionKeys[i+self.viewportY-1]+"\t"+str(d[optionKeys[i+self.viewportY-1]])).expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) + 1:
					self.window.chgat(i+1,1+len(str(optionKeys[i+self.viewportY-1]+"\t").expandtabs(self.manager.Objects["config"].options["TabExpandSize"])),len(str(d[optionKeys[i+self.viewportY-1]])),self.manager.curses.color_pair(d[optionKeys[i+self.viewportY-1]]))
			else: # it is a dict or list
				self.window.addnstr(i+1,1,str(optionKeys[i+self.viewportY-1]+"\t...").expandtabs(self.manager.Objects["config"].options["TabExpandSize"]),self.window.getmaxyx()[1]-2)
			if self.currentOption == i+self.viewportY-1:
				self.window.chgat(i+1,1,min(self.window.getmaxyx()[1]-2,len(optionKeys[i+self.viewportY-1])),self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
		self.window.box()
		self.manager.update()
		
		while True:
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.currentOption = 0
				self.viewportY = 0
				if name == "Config Customizer":
					self.toggle()
					self.panel.hide()
				elif name == "Color Customizer":
					self.intendedX = 0
					self.window.mvwin(0,0) # for some reason, despite intendedX being 0, kWIMS() does not move it upon leaving a method...
#					self.keepWindowInMainScreen()
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if self.window.getmaxyx()[0] <= 2 or self.window.getmaxyx()[1] <= 2:
#				self.toggle() # window is too small to print anything so quit while we're ahead.
#				self.panel.hide()
#				break
				continue
			if c == "^_":
				if name == "Config Customizer":
					self.toggle()
					self.panel.hide()
				elif name == "Color Customizer":
					self.intendedX = 0
					self.window.mvwin(0,0) # for some reason, despite intendedX being 0, kWIMS() does not move it upon leaving a method...
#					self.keepWindowInMainScreen()
				self.currentOption = 0
				self.viewportY = 0
				break
#				"""
#				if c == "KEY_LEFT":
#					if self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] > 0:
#						self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] -= 1
#				if c == "KEY_RIGHT":
#					self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] += 1
#				"""
			elif c == "KEY_LEFT":
				datatype = str(type(d[optionKeys[self.currentOption]])).split("'")[1]
				if optionKeys[self.currentOption] == "TabLength":
					# custom TabLength config logic
					if datatype == "int": # if TabLength is currently already an integer
						if d[optionKeys[self.currentOption]] > 1:
							d[optionKeys[self.currentOption]]-=1
						else: # no TabLength zero, char instead
							d[optionKeys[self.currentOption]] = "char"
				elif datatype == "dict":
					if name != "Config Customizer":
#						self.editDict(d[optionKeys[self.currentOption]]) # unintuitive, easier to press left to go back
						break
				elif datatype == "bool":
					d[optionKeys[self.currentOption]] = not d[optionKeys[self.currentOption]]
				elif datatype == "int":
					if d[optionKeys[self.currentOption]] > 0:
						d[optionKeys[self.currentOption]]-=1

			elif c == "KEY_RIGHT":
				datatype = str(type(d[optionKeys[self.currentOption]])).split("'")[1]
				if optionKeys[self.currentOption] == "TabLength": # custom TabLength config logic
					if d[optionKeys[self.currentOption]] == "char":
						d[optionKeys[self.currentOption]] = 1
					elif datatype == "int": # if TabLength is currently already an integer
						d[optionKeys[self.currentOption]]+=1
				elif datatype == "dict":
					if optionKeys[self.currentOption] == "ColorMap": # custom ColorMap config logic, window resizes to see color changes realtime
						self.editDict(d[optionKeys[self.currentOption]],"Color Customizer")
					else:
						self.editDict(d[optionKeys[self.currentOption]])
				elif datatype == "bool":
					d[optionKeys[self.currentOption]] = not d[optionKeys[self.currentOption]]
				elif datatype == "int":
					d[optionKeys[self.currentOption]]+=1
					
			elif c == "KEY_UP":
				if self.currentOption > 0:
					self.currentOption -= 1
					if self.currentOption < self.viewportY:
#						self.viewportY-=1
						self.viewportY-=self.viewportY-self.currentOption
					if self.currentOption > self.window.getmaxyx()[0]+self.viewportY-4:
						self.viewportY+=self.currentOption-self.viewportY
						
			elif c == "KEY_DOWN":
				if self.currentOption < len(optionKeys)-1: 
					self.currentOption += 1
#					if self.window.getmaxyx()[0] == 6:
#						exit()
					if self.currentOption > self.window.getmaxyx()[0]+self.viewportY-4:
						self.viewportY+=self.currentOption-self.viewportY

			self.intendedWidth = self.manager.stdscr.getmaxyx()[1]
			self.intendedHeight = self.manager.stdscr.getmaxyx()[0]
			self.intendedX = 0
			if name == "Color Customizer":
				self.intendedHeight = len(d.keys())+3
				self.intendedWidth = max(len(str(len(d.keys()))+"\t#"),len("Color Customizer")+2)
				# intendedWidth explained: d.keys will return a number with as many digits..
				self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
			self.keepWindowInMainScreen()

			self.window.clear()
			self.window.addnstr(1,1,name,self.window.getmaxyx()[1]-2,self.manager.curses.A_STANDOUT)
			for i in range(1,self.window.getmaxyx()[0]-1): # for each line of window after title text				
				if i+self.viewportY-1 >= len(optionKeys):
					break
				if str(type(d[optionKeys[i+self.viewportY-1]])).split("'")[1] != "dict" and str(type(d[optionKeys[i+self.viewportY-1]])).split("'")[1] != "list":
					self.window.addnstr(i+1,1,str(optionKeys[i+self.viewportY-1]+"\t"+str(d[optionKeys[i+self.viewportY-1]])).expandtabs(self.manager.Objects["config"].options["TabExpandSize"]),self.window.getmaxyx()[1]-2)
					if name == "Color Customizer" and self.window.getmaxyx()[1] > len(str(optionKeys[i+self.viewportY-1]+"\t"+str(d[optionKeys[i+self.viewportY-1]])).expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) + 1:
						self.window.chgat(i+1,1+len(str(optionKeys[i+self.viewportY-1]+"\t").expandtabs(self.manager.Objects["config"].options["TabExpandSize"])),len(str(d[optionKeys[i+self.viewportY-1]])),self.manager.curses.color_pair(d[optionKeys[i+self.viewportY-1]]))
				else: # it is a dict or list
					self.window.addnstr(i+1,1,str(optionKeys[i+self.viewportY-1]+"\t...").expandtabs(self.manager.Objects["config"].options["TabExpandSize"]),self.window.getmaxyx()[1]-2)
				if self.currentOption == i+self.viewportY-1:
					self.window.chgat(i+1,1,min(self.window.getmaxyx()[1]-2,len(optionKeys[i+self.viewportY-1])),self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
			"""
			for color in self.manager.Objects["config"].options["ColorMap"]:
				self.window.addnstr(2+int(color),6,str(self.manager.Objects["config"].options["ColorMap"][color]),self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(int(self.manager.Objects["config"].options["ColorMap"][color])))
				self.window.addnstr(2+int(color),1,color,self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(0))
				if self.currentOption == int(color):
					self.window.chgat(2+int(color),1,1,self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
			self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
			"""
			self.window.box()
				
			for i in self.manager.Windows:
				if self.manager.Windows[i].name == "configCustomizer": # name given in engine init
					continue # to avoid recursive loop
				self.manager.Windows[i].update()
			self.manager.Objects["highlighter"].update()
			self.manager.update()
#			"""
		self.manager.Objects["config"].save()
#		"""
		self.manager.update()

	def terminate(self):
		pass
