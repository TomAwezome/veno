# import re
# import string

from modules.window import Window
class MagicBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		import string
		import re
		self.re = re
		self.string = string
		self.searchCursorX = 0
		self.searchString = ""

		## FileWindow instance MagicBar is attached to.
		self.fileWindow = self.manager.Windows["fileWindow"]

		self.saveString = self.fileWindow.file.source
		self.config = self.manager.Objects["config"].options
		
#		gotoLineCursorX = 0
#		gotoLineString = ""
#		use = ""
#?
		self.patternMatches = None
		self.panel.top()
		self.panel.hide()

	def update(self):
		self.cursor = self.fileWindow.filecursor

	def search(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0 
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()
		
		tabExpandSize = tabExpandSize = self.config["TabExpandSize"]
		self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
		if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
			self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break

			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				searchStringLeft = self.searchString[:self.searchCursorX] + c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX] + '\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1

			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1

			elif c == "KEY_BACKSPACE" or c == "^?": # ^? reported on some macOS / other terms
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX - 1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1

			elif c == "KEY_DC":
				if self.searchCursorX + 1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX + 1:]
					self.searchString = searchStringLeft + searchStringRight

			elif c == "KEY_HOME" and self.searchCursorX > 0:
				self.searchCursorX = 0

			elif c == "KEY_END" and self.searchCursorX < len(self.searchString):
				self.searchCursorX = len(self.searchString)

			elif c == "^J":
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
			if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
				self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		pattern = self.re.compile(self.searchString)
		self.patternMatches = pattern.finditer(self.fileWindow.file.contents)
		try:
			nextMatch = next(self.patternMatches)
			searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])
		except StopIteration:
			pass

		try:
			while searchIndexY < self.cursor[1]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while self.cursor[1] > searchIndexY:
				self.fileWindow.moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.fileWindow.moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.fileWindow.moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.fileWindow.moveFilecursorRight()

			self.update()
			keepWindowInMainScreen()
		except NameError:
			pass

	def gotoLine(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()

		self.manager.update()# 		keepWindowInMainScreen(self.intendedHeight, self.intendedWidth, self.intendedY, self.intendedX, self.window)

		gotoLineString = ""
		gotoLineCursorX = 0
		self.window.addnstr(0, 0, gotoLineString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		if gotoLineCursorX <= self.getWindowMaxX() - 2 and gotoLineCursorX >= 0:
			self.window.chgat(0, gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				searchStringLeft = gotoLineString[:gotoLineCursorX] + c
				searchStringRight = gotoLineString[gotoLineCursorX:]
				gotoLineString = searchStringLeft + searchStringRight
				gotoLineCursorX += 1

			elif c == "KEY_LEFT" and gotoLineCursorX > 0:
				gotoLineCursorX -= 1

			elif c == "KEY_RIGHT" and gotoLineCursorX < len(gotoLineString): # later deal with offscreen typing
				gotoLineCursorX += 1

			elif c == "KEY_BACKSPACE" or c == "^?": # ^? reported on some macOS / other terms
				if gotoLineCursorX > 0:
					searchStringLeft = gotoLineString[:gotoLineCursorX - 1]
					searchStringRight = gotoLineString[gotoLineCursorX:]
					gotoLineString = searchStringLeft + searchStringRight
					gotoLineCursorX -= 1

			elif c == "KEY_DC":
				if gotoLineCursorX + 1 <= len(gotoLineString): # if there is text to the right of our cursor
					searchStringLeft = gotoLineString[:gotoLineCursorX]
					searchStringRight = gotoLineString[gotoLineCursorX + 1:]
					gotoLineString = searchStringLeft + searchStringRight

			elif c == "KEY_HOME" and gotoLineCursorX > 0:
				gotoLineCursorX = 0

			elif c == "KEY_END" and gotoLineCursorX < len(gotoLineString):
				gotoLineCursorX = len(gotoLineString)

			elif c == "^J":
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, gotoLineString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			if gotoLineCursorX <= self.getWindowMaxX() - 2 and gotoLineCursorX >= 0:
				self.window.chgat(0, gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		try:
			lineNumber = int(gotoLineString)
			if lineNumber > 0:
				self.fileWindow.gotoLine(lineNumber - 1)
		except:
			pass

		self.keepWindowInMainScreen()

	def searchNext(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		
		try:
			try:
				nextMatch = next(self.patternMatches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
			except TypeError:
				return

			searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])

			while self.cursor[1] > searchIndexY:
				self.fileWindow.moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.fileWindow.moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.fileWindow.moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.fileWindow.moveFilecursorRight()
		except StopIteration:
			pass

	def replace(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1

		self.keepWindowInMainScreen()	
		self.manager.update()
		self.keepWindowInMainScreen()

		tabExpandSize = tabExpandSize = self.config["TabExpandSize"]
		self.window.addnstr(0,0,self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
		if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
			self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
		self.manager.update()


	## search string
	# keypress loop: begin catching characters
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			
			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				searchStringLeft = self.searchString[:self.searchCursorX] + c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX] + '\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1

			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1

			elif c == "KEY_BACKSPACE" or c == "^?": # ^? reported on some macOS / other terms
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX - 1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1

			elif c == "KEY_DC":
				if self.searchCursorX + 1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX + 1:]
					self.searchString = searchStringLeft + searchStringRight

			elif c == "KEY_HOME" and self.searchCursorX > 0:
				self.searchCursorX = 0

			elif c == "KEY_END" and self.searchCursorX < len(self.searchString):
				self.searchCursorX = len(self.searchString)

			elif c == "^J":
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
			if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
				self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()
		
		firstString = self.searchString
		
	## replacement string
	# keypress loop: begin catching characters
		self.searchString = ""
		self.searchCursorX = 0
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
		if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
			self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
		self.manager.update()

		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			
			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				searchStringLeft = self.searchString[:self.searchCursorX] + c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX] + '\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1

			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1

			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1

			elif c == "KEY_BACKSPACE" or c == "^?": # ^? reported on some macOS / other terms
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX - 1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1

			elif c == "KEY_DC":
				if self.searchCursorX + 1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX + 1:]
					self.searchString = searchStringLeft + searchStringRight

			elif c == "KEY_HOME" and self.searchCursorX > 0:
				self.searchCursorX = 0

			elif c == "KEY_END" and self.searchCursorX < len(self.searchString):
				self.searchCursorX = len(self.searchString)

			elif c == "^J":
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
			if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
				self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()
			
		secondString = self.searchString

		fileLines = self.fileWindow.fileLines
		fileString = '\n'.join(fileLines)


		# next we'll find the first occurence (relative to our cursor) of our to-be-replaced string, and move the file cursor there and have our current nexMatch be that occurence

		pattern = self.re.compile(firstString)
		self.patternMatches = pattern.finditer(self.fileWindow.file.contents)
		try:
			nextMatch = next(self.patternMatches)
			searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])
		except StopIteration:
			pass

		try:
			while searchIndexY < self.cursor[1]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX < self.cursor[0]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while self.cursor[1] > searchIndexY:
				self.fileWindow.moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.fileWindow.moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.fileWindow.moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.fileWindow.moveFilecursorRight()


			self.keepWindowInMainScreen()
		except NameError:
			pass

		self.fileWindow.modified = True
		self.fileWindow.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		self.manager.Objects["highlighter"].update()
		self.manager.update()

		while True: # break out of this loop with enter key
			try:
				nextMatch
			except NameError:
				break
			self.window.erase()
			self.window.addnstr(0, 0, "Replace? (y/n/a) ['a' = All]", self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
			self.manager.Windows["lineNumbers"].update()
			self.manager.update()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			
			if c == "y":
				fileLines = self.fileWindow.fileLines
				fileString = '\n'.join(fileLines)

				replacedString = self.re.sub(firstString, secondString, fileString[nextMatch.start():nextMatch.end()])
				replaceStringLeft = fileString[:nextMatch.start()]
				replaceStringRight = fileString[nextMatch.end():]
				replaceStringCombined = replaceStringLeft + replacedString + replaceStringRight
				self.fileWindow.fileLines = replaceStringCombined.splitlines()
				self.fileWindow.file.contents = replaceStringCombined

			elif c == "n":
				pass

			elif c == "a":
				fileLines = self.fileWindow.fileLines
				fileString = '\n'.join(fileLines)
				replacedString = self.re.sub(firstString, secondString, fileString)
				self.fileWindow.file.contents = replacedString
				self.fileWindow.fileLines = replacedString.splitlines()
				break
			elif c == "^J":
				break

			self.patternMatches = pattern.finditer(self.fileWindow.file.contents)
			try:
				nextMatch = next(self.patternMatches)
#			if patternMatch is not None:
				searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
				searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
				if len(searchLines) > 0:
					searchIndexX = len(searchLines[len(searchLines) - 1])
			except StopIteration:
				break

			try:
				while searchIndexY < self.cursor[1]:
					try:
						nextMatch = next(self.patternMatches)
						searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
						searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines) - 1])
					except StopIteration:
						break

				while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
					try:
						nextMatch = next(self.patternMatches)
						searchIndexY = self.fileWindow.file.contents[:nextMatch.start()].count('\n')
						searchLines = self.fileWindow.file.contents[:nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines) - 1])
					except StopIteration:
						break

				while self.cursor[1] > searchIndexY:
					self.fileWindow.moveFilecursorUp()
				while self.cursor[1] < searchIndexY:
					self.fileWindow.moveFilecursorDown()
				while self.cursor[0] > searchIndexX:
					self.fileWindow.moveFilecursorLeft()
				while self.cursor[0] < searchIndexX:
					self.fileWindow.moveFilecursorRight()


				self.keepWindowInMainScreen()
			except NameError:
				pass

			self.keepWindowInMainScreen()
			self.fileWindow.modified = True
			self.fileWindow.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
			self.manager.Objects["highlighter"].update()
			self.manager.update()

		self.window.erase()
		self.keepWindowInMainScreen()
		self.fileWindow.modified = True
		self.fileWindow.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		self.manager.Objects["highlighter"].update()
		self.manager.update()

	def confirmExitSave(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0, 0, "Save before exit?", self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
		
		while True:
			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.addnstr(0, 0, "Save before exit?", self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
			self.manager.update()

			c = self.manager.stdscr.getch() # (Ctrl-C to refuse exit save)
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if c == "^J":
				self.window.erase()
				if self.fileWindow.saveFile() == 0: # successfully saved
					exit("File saved, safe to exit")
				else: # Ctrl-C to exit confirmExitSave and return to file
					break

	def save(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1
		returnval = 0

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0, 0, "Filename?", self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
		self.manager.update()

		while True:
			kill = False
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				kill = True
				break

			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if c == "^J":
				break

		if kill == True:
			self.window.erase()
			returnval = 1
			return returnval
		## savefile string
		# keypress loop: begin catching characters
		self.window.erase()
		self.window.addnstr(0, 0, self.saveString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		if self.searchCursorX <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
			self.window.chgat(0, self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				returnval = 1
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			
			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				saveStringLeft = self.saveString[:self.searchCursorX] + c
				saveStringRight = self.saveString[self.searchCursorX:]
				self.saveString = saveStringLeft + saveStringRight
				self.searchCursorX += 1

			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1

			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.saveString): # later deal with offscreen typing
				self.searchCursorX += 1

			elif c == "KEY_BACKSPACE" or c == "^?": # ^? reported on some macOS / other terms
				if self.searchCursorX > 0:
					saveStringLeft = self.saveString[:self.searchCursorX - 1]
					saveStringRight = self.saveString[self.searchCursorX:]
					self.saveString = saveStringLeft + saveStringRight
					self.searchCursorX -= 1

			elif c == "KEY_DC":
				if self.searchCursorX + 1 <= len(self.saveString): # if there is text to the right of our cursor
					saveStringLeft = self.saveString[:self.searchCursorX]
					saveStringRight = self.saveString[self.searchCursorX + 1:]
					self.saveString = saveStringLeft + saveStringRight

			elif c == "KEY_HOME" and self.searchCursorX > 0:
				self.searchCursorX = 0

			elif c == "KEY_END" and self.searchCursorX < len(self.saveString):
				self.searchCursorX = len(self.saveString)

			elif c == "^J":
				if self.saveString != "":
					break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.saveString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			if self.searchCursorX <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
				self.window.chgat(0, self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		self.fileWindow.file.source = self.saveString
		return returnval

	def terminate(self):
		pass
