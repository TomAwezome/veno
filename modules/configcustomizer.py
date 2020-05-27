from modules.window import Window
class ConfigCustomizerWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intendedY = 0
		self.intendedWidth = self.getStdscrMaxX()
		self.intendedX = 0
		self.intendedHeight = self.getStdscrMaxY()
		self.isOpen = False
		self.window.erase()
		self.keepWindowInMainScreen()

		if self.isOpen == False:
			self.panel.hide()
		else:
			self.panel.top()

		self.currentOption = 0
		self.viewportY = 0
		
		## Config instance.
		self.config = self.manager.Objects["config"]

		## ConfigCustomizer keybindings dictionary stores functions
		self.bindings = {}
		self.bind()

	def update(self):
		self.window.erase()
		self.keepWindowInMainScreen()
		
		if self.isOpen == False:
			if self.panel.hidden == False:
				self.panel.hide()
		
		else:
			self.panel.top()
			self.editDict(self.config.options, "Config Customizer")

	def bind(self):
		self.bindings["^_"] = self.closeCurrentCustomizer
		self.bindings["KEY_LEFT"] = self.decrementConfigValue
		self.bindings["KEY_RIGHT"] = self.incrementConfigValue
		self.bindings["KEY_UP"] = self.moveCurrentOptionUp
		self.bindings["KEY_DOWN"] = self.moveCurrentOptionDown
		self.bindings["^J"] = self.descendIntoDict
		self.bindings[" "] = self.descendIntoDict


	def closeCurrentCustomizer(self, d, name): #d unused; passed to all customizer keybinding functions
		if name == "Config Customizer":
			self.toggle()
			self.panel.hide()
		elif name == "Color Customizer":
			self.intendedX = 0
			self.window.mvwin(0, 0) # for some reason, despite intendedX being 0, kWIMS() does not move it upon leaving a method...
			#self.keepWindowInMainScreen()

		self.currentOption = 0
		self.viewportY = 0

	def decrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		optionKeys = list(d.keys())
		datatype = str(type(d[optionKeys[self.currentOption]])).split("'")[1]

		if optionKeys[self.currentOption] == "TabLength":
			# custom TabLength config logic
			if datatype == "int": # if TabLength is currently already an integer
				if d[optionKeys[self.currentOption]] > 1:
					d[optionKeys[self.currentOption]] -= 1
				else: # no TabLength zero, char instead
					d[optionKeys[self.currentOption]] = "char"

		elif datatype == "bool":
			d[optionKeys[self.currentOption]] = not d[optionKeys[self.currentOption]]

		elif datatype == "int":
			if d[optionKeys[self.currentOption]] > 0:
				d[optionKeys[self.currentOption]] -= 1

	def incrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		optionKeys = list(d.keys())
		datatype = str(type(d[optionKeys[self.currentOption]])).split("'")[1]

		if optionKeys[self.currentOption] == "TabLength": # custom TabLength config logic
			if d[optionKeys[self.currentOption]] == "char":
				d[optionKeys[self.currentOption]] = 1
			elif datatype == "int": # if TabLength is currently already an integer
				d[optionKeys[self.currentOption]] += 1

		elif datatype == "bool":
			d[optionKeys[self.currentOption]] = not d[optionKeys[self.currentOption]]

		elif datatype == "int":
			d[optionKeys[self.currentOption]] += 1

	def moveCurrentOptionUp(self, d, name): #d, name unused; passed to all customizer keybinding functions
		if self.currentOption > 0:
			self.currentOption -= 1
			if self.currentOption < self.viewportY:
				#self.viewportY-=1
				self.viewportY -= self.viewportY - self.currentOption
			if self.currentOption > self.getWindowMaxY() + self.viewportY - 4:
				self.viewportY += self.currentOption - self.viewportY

	def moveCurrentOptionDown(self, d, name): #name unused; passed to all customizer keybinding functions
		optionKeys = list(d.keys())
		if self.currentOption < len(optionKeys) - 1: 
			self.currentOption += 1
			#if self.getWindowMaxY() == 6:
				#exit()
			if self.currentOption > self.getWindowMaxY() + self.viewportY - 4:
				self.viewportY += self.currentOption - self.viewportY

	def descendIntoDict(self, d, name): #name unused; passed to all customizer keybinding functions
		optionKeys = list(d.keys())
		datatype = str(type(d[optionKeys[self.currentOption]])).split("'")[1]

		if datatype == "dict":
			if optionKeys[self.currentOption] == "ColorMap": # custom ColorMap config logic, window resizes to see color changes realtime
				self.editDict(d[optionKeys[self.currentOption]], "Color Customizer")
			else:
				self.editDict(d[optionKeys[self.currentOption]])


	def toggle(self):
		if self.isOpen == True:
			self.isOpen = False
		else:
			self.isOpen = True

	def editDict(self, d, name="Dictionary Editor"):
		self.window.erase()
		self.currentOption = 0
		self.viewportY = 0 # self.getStdscrMaxX()
		self.intendedWidth = self.getStdscrMaxX()
		self.intendedHeight = self.getStdscrMaxY()
		self.intendedX = 0

		optionKeys = list(d.keys())

		if name == "Color Customizer":
			self.intendedHeight = len(optionKeys) + 3
			self.intendedWidth = max(len(str(len(optionKeys)) + "\t#"), len("Color Customizer") + 2)
			# intendedWidth explained: d.keys will return a number with as many digits..
			self.intendedX = int(self.getStdscrMaxX() / 2 - (self.intendedWidth / 2))
		
		self.keepWindowInMainScreen()
		self.window.box()
			
		# HAVE to consider screensize. self.window.getmaxyx() at this point should be happily computed.
		# if we wanna config on small displays, do we need scrolling?.....
		# yes. we can do that after we get it displaying based on maxyx.
		if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
			return # window is too small to print anything so quit while we're ahead.

		self.window.addnstr(1, 1, name, self.getWindowMaxX() - 2, self.manager.curses.A_STANDOUT)
			
		# Explaining some possibly hard to read code;
		# this for loop increments i over a range of 1...windowMaxY to do the following with i:
		# 1) ensure that i+viewportY (to be used in optionKeys index) won't exceed optionKeys max index
		# 2) check type of value at optionKeys[i+viewportY-1], if dict or list, show value as ...
		#    (... is to indicate that another config menu will come up and pressing Enter is needed.)
		# 3) add text to screen row i+1 for windowMaxX-2 characters
		#    (+1 since title takes up row 1, row 0 is box but accounted for since range begins at 1)
		#    (-2 since text is offset by 1 to not print over box, and to not print on the box 1 off from the right border)
		# 4) if current line in loop is one with currentOption on it, highlight the key text

		for i in range(1, self.getWindowMaxY() - 1): # for each line of window after title text
			tabExpandSize = self.config.options["TabExpandSize"]
			optionIndex = i + self.viewportY - 1
			if optionIndex >= len(optionKeys):
				break
			optionString = optionKeys[optionIndex]
			optionValue = d[optionString]
			optionValueString = str(optionValue)
			optionType = str(type(optionValue)).split("'")[1]
			lineString = str(optionString + "\t" + optionValueString).expandtabs(tabExpandSize)
			objectString = str(optionString + "\t...").expandtabs(tabExpandSize)
			colorHighlightIndex = len(str(optionString + "\t").expandtabs(tabExpandSize)) + 1

			if optionType != "dict" and optionType != "list":
				self.window.addnstr(i + 1, 1, lineString, self.getWindowMaxX() - 2)

				if name == "Color Customizer" and self.getWindowMaxX() > len(lineString) + 1:
					self.window.chgat(i + 1, colorHighlightIndex, len(optionValueString), self.manager.curses.color_pair(optionValue))

			else: # it is a dict or list
				self.window.addnstr(i + 1, 1, objectString, self.getWindowMaxX() - 2)

			if self.currentOption == optionIndex:
				self.window.chgat(i + 1, 1, min(self.getWindowMaxX() - 2, len(optionString)), self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

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
					self.window.mvwin(0, 0) # for some reason, despite intendedX being 0, kWIMS() does not move it upon leaving a method...
					#self.keepWindowInMainScreen()
				break
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
				#self.toggle() # window is too small to print anything so quit while we're ahead.
				#self.panel.hide()
				#break
				continue

			if c in self.bindings:
				self.bindings[c](d, name)
				if c == "^_":
					break

			self.intendedWidth = self.getStdscrMaxX()
			self.intendedHeight = self.getStdscrMaxY()
			self.intendedX = 0

			if name == "Color Customizer":
				self.intendedHeight = len(d.keys()) + 3
				self.intendedWidth = max(len(str(len(d.keys())) + "\t#"), len("Color Customizer") + 2)
				# intendedWidth explained: d.keys will return a number with as many digits..
				self.intendedX = int(self.getStdscrMaxX() / 2 - (self.intendedWidth / 2))

			self.keepWindowInMainScreen()
			self.window.clear()
			
			self.window.addnstr(1, 1, name, self.getWindowMaxX() - 2, self.manager.curses.A_STANDOUT)
			for i in range(1, self.getWindowMaxY() - 1): # for each line of window after title text				
				tabExpandSize = self.config.options["TabExpandSize"]
				optionIndex = i + self.viewportY - 1				
				if optionIndex >= len(optionKeys):
					break
				optionString = optionKeys[optionIndex]
				optionValue = d[optionString]
				optionValueString = str(optionValue)
				optionType = str(type(optionValue)).split("'")[1]
				lineString = str(optionString + "\t" + optionValueString).expandtabs(tabExpandSize)
				objectString = str(optionString + "\t...").expandtabs(tabExpandSize)
				colorHighlightIndex = len(str(optionString + "\t").expandtabs(tabExpandSize)) + 1

			
				if optionType != "dict" and optionType != "list":
					self.window.addnstr(i + 1, 1, lineString, self.getWindowMaxX() - 2)
					if name == "Color Customizer" and self.getWindowMaxX() > len(lineString) + 1:
						self.window.chgat(i + 1, colorHighlightIndex, len(optionValueString), self.manager.curses.color_pair(optionValue))

				else: # it is a dict or list
					self.window.addnstr(i + 1, 1, objectString, self.getWindowMaxX() - 2)

				if self.currentOption == optionIndex:
					self.window.chgat(i + 1, 1, min(self.getWindowMaxX() - 2, len(optionString)), self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

			self.window.box()
				
			for i in self.manager.Windows:
				if self.manager.Windows[i].name == "configCustomizer": # name given in engine init
					continue # to avoid recursive loop

				self.manager.Windows[i].update()

			self.manager.Objects["highlighter"].update()
			self.manager.update()

		self.config.save()
		self.manager.update()

	def terminate(self):
		pass
