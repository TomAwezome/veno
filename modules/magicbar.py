import re
import string

from modules.window import Window
class MagicBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.re = re
		self.string = string
		
		## FileWindow instance MagicBar is attached to.
		self.fileWindow = self.manager.Windows["fileWindow"]
		
		self.config = self.manager.Objects["config"].options

		self.searchCursorX = 0
		self.searchString = ""

		self.gotoLineCursorX = 0
		self.gotoLineString = ""

		self.saveCursorX = 0
		self.saveString = self.fileWindow.file.source

		self.patternMatches = None
		self.nextMatch = None

		# Functions are stored in these dictionaries for magicBar curses getch() loops.
		self.searchBindings = {}
		self.gotoLineBindings = {}
		self.saveBindings = {}
		self.replaceBindings = {}
		self.bind()

		self.panel.top()
		self.panel.hide()

	def update(self):
		self.cursor = self.fileWindow.filecursor

	def bind(self):
		self.searchBindings["KEY_LEFT"] = self.moveSearchCursorLeft
		self.searchBindings["KEY_RIGHT"] = self.moveSearchCursorRight
		self.searchBindings["KEY_BACKSPACE"] = self.backspaceAtSearchCursor
		self.searchBindings["^?"] = self.backspaceAtSearchCursor
		self.searchBindings["^H"] = self.backspaceAtSearchCursor
		self.searchBindings["KEY_DC"] = self.deleteAtSearchCursor
		self.searchBindings["KEY_HOME"] = self.moveSearchCursorToStart
		self.searchBindings["KEY_END"] = self.moveSearchCursorToEnd
		self.searchBindings["^I"] = self.enterTabAtSearchCursor
		self.searchBindings["printable-character"] = self.enterTextAtSearchCursor

		self.gotoLineBindings["KEY_LEFT"] = self.moveGotoLineCursorLeft
		self.gotoLineBindings["KEY_RIGHT"] = self.moveGotoLineCursorRight
		self.gotoLineBindings["KEY_BACKSPACE"] = self.backspaceAtGotoLineCursor
		self.gotoLineBindings["^?"] = self.backspaceAtGotoLineCursor
		self.gotoLineBindings["^H"] = self.backspaceAtGotoLineCursor
		self.gotoLineBindings["KEY_DC"] = self.deleteAtGotoLineCursor
		self.gotoLineBindings["KEY_HOME"] = self.moveGotoLineCursorToStart
		self.gotoLineBindings["KEY_END"] = self.moveGotoLineCursorToEnd
		self.gotoLineBindings["digit"] = self.enterDigitAtGotoLineCursor
		
		self.saveBindings["KEY_LEFT"] = self.moveSaveCursorLeft
		self.saveBindings["KEY_RIGHT"] = self.moveSaveCursorRight
		self.saveBindings["KEY_BACKSPACE"] = self.backspaceAtSaveCursor
		self.saveBindings["^?"] = self.backspaceAtSaveCursor
		self.saveBindings["^H"] = self.backspaceAtSaveCursor
		self.saveBindings["KEY_DC"] = self.deleteAtSaveCursor
		self.saveBindings["KEY_HOME"] = self.moveSaveCursorToStart
		self.saveBindings["KEY_END"] = self.moveSaveCursorToEnd
		self.saveBindings["printable-character"] = self.enterTextAtSaveCursor

		self.replaceBindings["y"] = self.replaceTextAtMatch
		self.replaceBindings["a"] = self.replaceAllMatches


	def moveSearchCursorLeft(self):
		if self.searchCursorX > 0:
			self.searchCursorX -= 1

	def moveSearchCursorRight(self):
		if self.searchCursorX < len(self.searchString):
			self.searchCursorX += 1

	def backspaceAtSearchCursor(self):
		if self.searchCursorX > 0:
			searchStringLeft = self.searchString[:self.searchCursorX - 1]
			searchStringRight = self.searchString[self.searchCursorX:]
			self.searchString = searchStringLeft + searchStringRight
			self.searchCursorX -= 1

	def deleteAtSearchCursor(self):
		if self.searchCursorX + 1 <= len(self.searchString): # if there is text to the right of our cursor
			searchStringLeft = self.searchString[:self.searchCursorX]
			searchStringRight = self.searchString[self.searchCursorX + 1:]
			self.searchString = searchStringLeft + searchStringRight

	def moveSearchCursorToStart(self):
		if self.searchCursorX > 0:
			self.searchCursorX = 0

	def moveSearchCursorToEnd(self):
		if self.searchCursorX < len(self.searchString):
			self.searchCursorX = len(self.searchString)

	def enterTabAtSearchCursor(self):
		searchStringLeft = self.searchString[:self.searchCursorX] + '\t'
		searchStringRight = self.searchString[self.searchCursorX:]
		self.searchString = searchStringLeft + searchStringRight
		self.searchCursorX += 1

	def enterTextAtSearchCursor(self, text):
		searchStringLeft = self.searchString[:self.searchCursorX] + text
		searchStringRight = self.searchString[self.searchCursorX:]
		self.searchString = searchStringLeft + searchStringRight
		self.searchCursorX += 1

	def moveGotoLineCursorLeft(self):
		if self.gotoLineCursorX > 0:
			self.gotoLineCursorX -= 1

	def moveGotoLineCursorRight(self):
		if self.gotoLineCursorX < len(self.gotoLineString):
			self.gotoLineCursorX += 1

	def backspaceAtGotoLineCursor(self):
		if self.gotoLineCursorX > 0:
			searchStringLeft = self.gotoLineString[:self.gotoLineCursorX - 1]
			searchStringRight = self.gotoLineString[self.gotoLineCursorX:]
			self.gotoLineString = searchStringLeft + searchStringRight
			self.gotoLineCursorX -= 1

	def deleteAtGotoLineCursor(self):
		if self.gotoLineCursorX + 1 <= len(self.gotoLineString): # if there is text to the right of our cursor
			searchStringLeft = self.gotoLineString[:self.gotoLineCursorX]
			searchStringRight = self.gotoLineString[self.gotoLineCursorX + 1:]
			self.gotoLineString = searchStringLeft + searchStringRight

	def moveGotoLineCursorToStart(self):
		if self.gotoLineCursorX > 0:
			self.gotoLineCursorX = 0

	def moveGotoLineCursorToEnd(self):
		if self.gotoLineCursorX < len(self.gotoLineString):
			self.gotoLineCursorX = len(self.gotoLineString)

	def enterDigitAtGotoLineCursor(self, digit):
		searchStringLeft = self.gotoLineString[:self.gotoLineCursorX] + digit
		searchStringRight = self.gotoLineString[self.gotoLineCursorX:]
		self.gotoLineString = searchStringLeft + searchStringRight
		self.gotoLineCursorX += 1

	def moveSaveCursorLeft(self):
		if self.saveCursorX > 0:
			self.saveCursorX -= 1

	def moveSaveCursorRight(self):
		if self.saveCursorX < len(self.saveString):
			self.saveCursorX += 1

	def backspaceAtSaveCursor(self):
		if self.saveCursorX > 0:
			saveStringLeft = self.saveString[:self.saveCursorX - 1]
			saveStringRight = self.saveString[self.saveCursorX:]
			self.saveString = saveStringLeft + saveStringRight
			self.saveCursorX -= 1

	def deleteAtSaveCursor(self):
		if self.saveCursorX + 1 <= len(self.saveString): # if there is text to the right of our cursor
			saveStringLeft = self.saveString[:self.saveCursorX]
			saveStringRight = self.saveString[self.saveCursorX + 1:]
			self.saveString = saveStringLeft + saveStringRight

	def moveSaveCursorToStart(self):
		if self.saveCursorX > 0:
			self.saveCursorX = 0

	def moveSaveCursorToEnd(self):
		if self.saveCursorX < len(self.saveString):
			self.saveCursorX = len(self.saveString)

	def enterTextAtSaveCursor(self, text):
		saveStringLeft = self.saveString[:self.saveCursorX] + text
		saveStringRight = self.saveString[self.saveCursorX:]
		self.saveString = saveStringLeft + saveStringRight
		self.saveCursorX += 1

	def replaceTextAtMatch(self, firstString, secondString):
		fileLines = self.fileWindow.fileLines
		fileString = '\n'.join(fileLines)

		replacedString = self.re.sub(firstString, secondString, fileString[self.nextMatch.start():self.nextMatch.end()])
		replaceStringLeft = fileString[:self.nextMatch.start()]
		replaceStringRight = fileString[self.nextMatch.end():]
		replaceStringCombined = replaceStringLeft + replacedString + replaceStringRight
		self.fileWindow.fileLines = replaceStringCombined.splitlines()
		self.fileWindow.file.contents = replaceStringCombined

	def replaceAllMatches(self, firstString, secondString):
		fileLines = self.fileWindow.fileLines
		fileString = '\n'.join(fileLines)
		replacedString = self.re.sub(firstString, secondString, fileString)
		self.fileWindow.file.contents = replacedString
		self.fileWindow.fileLines = replacedString.splitlines()


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

			if c in self.searchBindings:
				self.searchBindings[c]()
			elif c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				self.searchBindings["printable-character"](c)
			elif c == "^J": # enter key
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
			self.nextMatch = next(self.patternMatches)
			searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])
		except StopIteration:
			pass

		if self.nextMatch != None:
			while searchIndexY < self.cursor[1]:
				try:
					self.nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
				try:
					self.nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			self.fileWindow.gotoLine(searchIndexY)
			self.fileWindow.setFilecursorX(searchIndexX)
			self.update()

			self.keepWindowInMainScreen()

	def gotoLine(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.getStdscrMaxY()
		self.intendedWidth = self.getStdscrMaxX() - 1
		self.intendedHeight = 1

		self.keepWindowInMainScreen()
		self.manager.update()
		
		self.window.addnstr(0, 0, self.gotoLineString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		if self.gotoLineCursorX <= self.getWindowMaxX() - 2 and self.gotoLineCursorX >= 0:
			self.window.chgat(0, self.gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		
		wasInterrupted = False
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				wasInterrupted = True
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.gotoLineBindings:
				self.gotoLineBindings[c]()
			elif c in self.string.digits:
				self.gotoLineBindings["digit"](c)
			elif c == "^J": # enter key
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.gotoLineString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			if self.gotoLineCursorX <= self.getWindowMaxX() - 2 and self.gotoLineCursorX >= 0:
				self.window.chgat(0, self.gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		if not wasInterrupted:
			if self.gotoLineString != "":
				lineNumber = int(self.gotoLineString)
				if lineNumber > 0:
					self.fileWindow.gotoLine(lineNumber - 1)

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
				self.nextMatch = next(self.patternMatches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
			except TypeError: # if patternMatches is not iterator, next() raises TypeError. Catch and abort.
				return

			searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])

			self.fileWindow.gotoLine(searchIndexY)
			self.fileWindow.setFilecursorX(searchIndexX)

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
		self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
		if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
			self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()

	# search string
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

			if c in self.searchBindings:
				self.searchBindings[c]()
			elif c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				self.searchBindings["printable-character"](c)
			elif c == "^J": # enter key
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.searchString.expandtabs(tabExpandSize), self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(tabExpandSize)) - len(self.searchString[:self.searchCursorX])
			if self.searchCursorX + tabDiff <= self.getWindowMaxX() - 2 and self.searchCursorX >= 0:
				self.window.chgat(0, self.searchCursorX + tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()
		
		firstString = self.searchString
		
	# replacement string
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

			if c in self.searchBindings:
				self.searchBindings[c]()
			elif c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				self.searchBindings["printable-character"](c)
			elif c == "^J": # enter key
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
			self.nextMatch = next(self.patternMatches)
			searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
			searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines) - 1])
		except StopIteration:
			pass

		if self.nextMatch != None:
			while searchIndexY < self.cursor[1]:
				try:
					self.nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX < self.cursor[0]:
				try:
					self.nextMatch = next(self.patternMatches)
					searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
					searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines) - 1])
				except StopIteration:
					break

			self.fileWindow.gotoLine(searchIndexY)
			self.fileWindow.setFilecursorX(searchIndexX)

			self.keepWindowInMainScreen()

		self.fileWindow.modified = True
		self.fileWindow.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement

		self.manager.Objects["highlighter"].update()

		self.manager.update()

		while True: # break out of this loop with enter key
			if self.nextMatch == None:
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

			if c in self.replaceBindings:
				self.replaceBindings[c](firstString, secondString)
				if c == "a":
					break
			elif c == "n":
				pass
			elif c == "^J": # enter key
				break

			self.patternMatches = pattern.finditer(self.fileWindow.file.contents)
			try:
				self.nextMatch = next(self.patternMatches)
				searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
				searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
				if len(searchLines) > 0:
					searchIndexX = len(searchLines[len(searchLines) - 1])
			except StopIteration:
				break

			if self.nextMatch != None:
				while searchIndexY < self.cursor[1]:
					try:
						self.nextMatch = next(self.patternMatches)
						searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
						searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines) - 1])
					except StopIteration:
						break

				while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
					try:
						self.nextMatch = next(self.patternMatches)
						searchIndexY = self.fileWindow.file.contents[:self.nextMatch.start()].count('\n')
						searchLines = self.fileWindow.file.contents[:self.nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines) - 1])
					except StopIteration:
						break

				self.fileWindow.gotoLine(searchIndexY)
				self.fileWindow.setFilecursorX(searchIndexX)

				self.keepWindowInMainScreen()

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

		# savefile string
		# keypress loop: begin catching characters
		self.window.erase()
		self.window.addnstr(0, 0, self.saveString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

		if self.saveCursorX <= self.getWindowMaxX() - 2 and self.saveCursorX >= 0:
			self.window.chgat(0, self.saveCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

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

			if c in self.saveBindings:
				self.saveBindings[c]()
			elif c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
				self.saveBindings["printable-character"](c)
			elif c == "^J": # enter key
				if self.saveString != "":
					break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, self.saveString, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)

			if self.saveCursorX <= self.getWindowMaxX() - 2 and self.saveCursorX >= 0:
				self.window.chgat(0, self.saveCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		self.fileWindow.file.source = self.saveString
		return returnval

	def terminate(self):
		pass
