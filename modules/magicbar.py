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
# 		global standardscreen, intendedX, intendedY, intendedWidth, intendedHeight, magicBarWindow, magicBarPanel, use, patternMatches, self.searchString, self.searchCursorX, gotoLineString, gotoLineCursorX
		self.searchCursorX = 0
		self.searchString = ""
		self.saveString = self.manager.Windows["fileWindow"].file.source
		gotoLineCursorX = 0
		gotoLineString = ""
		use = ""
		self.patternMatches = None
		# standardscreen = self.manager.stdscr
		self.panel.top()
		self.panel.hide()

	def update(self):
		self.cursor = self.manager.Windows["fileWindow"].filecursor

	def search(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0 
		self.intendedY = self.manager.stdscr.getmaxyx()[0]
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
		if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
			self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
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
				searchStringLeft = self.searchString[:self.searchCursorX]+c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX]+'\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1
			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1
			elif c == "KEY_BACKSPACE":
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX-1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1
			elif c == "KEY_DC":
				if self.searchCursorX+1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX+1:]
					self.searchString = searchStringLeft+searchStringRight
			elif c == "^J":
				break
			self.keepWindowInMainScreen()
			self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
			if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
				self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
		pattern = self.re.compile(self.searchString)
		self.patternMatches = pattern.finditer(self.manager.Windows["fileWindow"].file.contents)
		try:
			nextMatch = next(self.patternMatches)
			searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
			searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
		except StopIteration:
			pass
		try:
			while searchIndexY < self.cursor[1]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
					searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines)-1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
					searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines)-1])
				except StopIteration:
					break

			while self.cursor[1] > searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorRight()

			self.update()
			keepWindowInMainScreen()
		except NameError:
			pass

	def gotoLine(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.manager.stdscr.getmaxyx()[0]
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()

		self.manager.update()# 		keepWindowInMainScreen(self.intendedHeight, self.intendedWidth, self.intendedY, self.intendedX, self.window)
		gotoLineString = ""
		gotoLineCursorX = 0
		self.window.addnstr(0,0,gotoLineString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
		if gotoLineCursorX <= self.window.getmaxyx()[1]-2 and gotoLineCursorX >= 0:
			self.window.chgat(0,gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
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
				searchStringLeft = gotoLineString[:gotoLineCursorX]+c
				searchStringRight = gotoLineString[gotoLineCursorX:]
				gotoLineString = searchStringLeft + searchStringRight
				gotoLineCursorX += 1
			elif c == "KEY_LEFT" and gotoLineCursorX > 0:
				gotoLineCursorX -= 1
			elif c == "KEY_RIGHT" and gotoLineCursorX < len(gotoLineString): # later deal with offscreen typing
				gotoLineCursorX += 1
			elif c == "KEY_BACKSPACE":
				if gotoLineCursorX > 0:
					searchStringLeft = gotoLineString[:gotoLineCursorX-1]
					searchStringRight = gotoLineString[gotoLineCursorX:]
					gotoLineString = searchStringLeft + searchStringRight
					gotoLineCursorX -= 1
			elif c == "KEY_DC":
				if gotoLineCursorX+1 <= len(gotoLineString): # if there is text to the right of our cursor
					searchStringLeft = gotoLineString[:gotoLineCursorX]
					searchStringRight = gotoLineString[gotoLineCursorX+1:]
					gotoLineString = searchStringLeft+searchStringRight
			elif c == "^J":
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0,0,gotoLineString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			if gotoLineCursorX <= self.window.getmaxyx()[1]-2 and gotoLineCursorX >= 0:
				self.window.chgat(0,gotoLineCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
		try:
			lineNumber = int(gotoLineString)
			if lineNumber > 0:
				self.manager.Windows["fileWindow"].gotoLine(lineNumber - 1)
		except:
			pass

		self.keepWindowInMainScreen()

	def searchNext(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.manager.stdscr.getmaxyx()[0]
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		try:
			try:
				nextMatch = next(self.patternMatches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
			except TypeError:
				return
			searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
			searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
			while self.cursor[1] > searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorRight()
		except StopIteration:
			pass

	def replace(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.manager.stdscr.getmaxyx()[0]
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
	
#		self.window.box()
#	self.window.addstr(0, 0, "222")

		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
		if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
			self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
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
				searchStringLeft = self.searchString[:self.searchCursorX]+c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX]+'\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1
			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1
			elif c == "KEY_BACKSPACE":
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX-1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1
			elif c == "KEY_DC":
				if self.searchCursorX+1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX+1:]
					self.searchString = searchStringLeft+searchStringRight
			elif c == "^J":
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
			if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
				self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
		
		firstString = self.searchString
		
	## replacement string
	# keypress loop: begin catching characters
		self.searchString = ""
		self.searchCursorX = 0
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
		tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
		if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
			self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
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
				searchStringLeft = self.searchString[:self.searchCursorX]+c
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "^I":
				searchStringLeft = self.searchString[:self.searchCursorX]+'\t'
				searchStringRight = self.searchString[self.searchCursorX:]
				self.searchString = searchStringLeft + searchStringRight
				self.searchCursorX += 1
			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1
			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
				self.searchCursorX += 1
			elif c == "KEY_BACKSPACE":
				if self.searchCursorX > 0:
					searchStringLeft = self.searchString[:self.searchCursorX-1]
					searchStringRight = self.searchString[self.searchCursorX:]
					self.searchString = searchStringLeft + searchStringRight
					self.searchCursorX -= 1
			elif c == "KEY_DC":
				if self.searchCursorX+1 <= len(self.searchString): # if there is text to the right of our cursor
					searchStringLeft = self.searchString[:self.searchCursorX]
					searchStringRight = self.searchString[self.searchCursorX+1:]
					self.searchString = searchStringLeft+searchStringRight
			elif c == "^J":
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0,0,self.searchString.expandtabs(4), self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			tabDiff = len(self.searchString[:self.searchCursorX].expandtabs(4))-len(self.searchString[:self.searchCursorX])
			if self.searchCursorX+tabDiff <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
				self.window.chgat(0,self.searchCursorX+tabDiff, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
			
		secondString = self.searchString

		fileLines = self.manager.Windows["fileWindow"].fileLines
		fileString = '\n'.join(fileLines)


		# next we'll find the first occurence (relative to our cursor) of our to-be-replaced string, and move the file cursor there and have our current nexMatch be that occurence

		pattern = self.re.compile(firstString)
#		patternMatch = pattern.search(self.manager.Windows["fileWindow"].file.contents)
		self.patternMatches = pattern.finditer(self.manager.Windows["fileWindow"].file.contents)
		try:
			nextMatch = next(self.patternMatches)
#		if patternMatch is not None:
			searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
			searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
		except StopIteration:
			pass

		try:
			while searchIndexY < self.cursor[1]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
					searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines)-1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX < self.cursor[0]:
				try:
					nextMatch = next(self.patternMatches)
					searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
					searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines)-1])
				except StopIteration:
					break

			while self.cursor[1] > searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorUp()
			while self.cursor[1] < searchIndexY:
				self.manager.Windows["fileWindow"].moveFilecursorDown()
			while self.cursor[0] > searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorLeft()
			while self.cursor[0] < searchIndexX:
				self.manager.Windows["fileWindow"].moveFilecursorRight()


			self.keepWindowInMainScreen()
		except NameError:
			pass

		self.manager.Windows["fileWindow"].modified = True
		self.manager.Windows["fileWindow"].update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		self.manager.Objects["highlighter"].update()
		# venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)
		self.manager.update()


		# now we need to use .start() and .end() of match to chop and glue self.string. together, and self.re.sub the matching indices, and after replacing instance, repeat process again (using modified file, to adjust for differences in the indices after splicing replacement in)
		# while we do this, we need to factor in keypresses, so that users can enter 'y' or 'n' to replace match, and can use either ESC or ctrl-C to cancel this use of magicBar module

		# start while loop for keypresses (perhaps update window contents before this to show position at first instance)
			# if 'y':
				# replacedString = self.re.sub(firstString, secondString, fileString[start:end])
				# left = fileString[:start]
				# right = fileString[end:]
				# combined = left + replacedString + right
				# windowCodeLines = combined.splitlines()
				#? self.manager.Windows["fileWindow"].file.contents = combined
			# if 'n':
				# pass
			# if 'esc'
				# break

			# self.patternMatches = pattern.finditer(self.manager.Windows["fileWindow"].file.contents)
			# nextMatch = next(self.patternMatches) # break if except StopIteration:
			# adjust cursor

#		useSwapped = False
		while True: # break out of this loop with enter key
			try:
				nextMatch
			except NameError:
				break
			self.window.erase()
			self.window.addnstr(0, 0, "Replace? (y/n/a) ['a' = All]", self.window.getmaxyx()[1] - 1, self.manager.curses.A_REVERSE)
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
				fileLines = self.manager.Windows["fileWindow"].fileLines
				fileString = '\n'.join(fileLines)

				replacedString = self.re.sub(firstString, secondString, fileString[nextMatch.start():nextMatch.end()])
				replaceStringLeft = fileString[:nextMatch.start()]
				replaceStringRight = fileString[nextMatch.end():]
				replaceStringCombined = replaceStringLeft + replacedString + replaceStringRight
				self.manager.Windows["fileWindow"].fileLines = replaceStringCombined.splitlines()
				self.manager.Windows["fileWindow"].file.contents = replaceStringCombined
			elif c == "n":
				pass
			elif c == "a":
#				use = "replaceAll"
#				useSwapped = True
				fileLines = self.manager.Windows["fileWindow"].fileLines
				fileString = '\n'.join(fileLines)
				replacedString = self.re.sub(firstString, secondString, fileString)
				self.manager.Windows["fileWindow"].file.contents = replacedString
				self.manager.Windows["fileWindow"].fileLines = replacedString.splitlines()
				break

#				self.searchCursorX += 1
#			elif c == "KEY_LEFT" and self.searchCursorX > 0:
#				self.searchCursorX -= 1
#			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
#				self.searchCursorX += 1
#			elif c == "KEY_BACKSPACE":
#				if self.searchCursorX > 0:
#					searchStringLeft = self.searchString[:self.searchCursorX-1]
#					searchStringRight = self.searchString[self.searchCursorX:]
#					self.searchString = searchStringLeft + searchStringRight
#					self.searchCursorX -= 1
			elif c == "^J":
				break

			self.patternMatches = pattern.finditer(self.manager.Windows["fileWindow"].file.contents)
			try:
				nextMatch = next(self.patternMatches)
#			if patternMatch is not None:
				searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
				searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
				if len(searchLines) > 0:
					searchIndexX = len(searchLines[len(searchLines)-1])
			except StopIteration:
				break

			try:
				while searchIndexY < self.cursor[1]:
					try:
						nextMatch = next(self.patternMatches)
						searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
						searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines)-1])
					except StopIteration:
						break

				while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
					try:
						nextMatch = next(self.patternMatches)
						searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
						searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
						if len(searchLines) > 0:
							searchIndexX = len(searchLines[len(searchLines)-1])
					except StopIteration:
						break

				while self.cursor[1] > searchIndexY:
					self.manager.Windows["fileWindow"].moveFilecursorUp()
				while self.cursor[1] < searchIndexY:
					self.manager.Windows["fileWindow"].moveFilecursorDown()
				while self.cursor[0] > searchIndexX:
					self.manager.Windows["fileWindow"].moveFilecursorLeft()
				while self.cursor[0] < searchIndexX:
					self.manager.Windows["fileWindow"].moveFilecursorRight()


				self.keepWindowInMainScreen()
			except NameError:
				pass

			self.keepWindowInMainScreen()
#			self.window.addnstr(0,0,self.searchString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
#			if self.searchCursorX <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
#				self.window.chgat(0,self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.Windows["fileWindow"].modified = True
			self.manager.Windows["fileWindow"].update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
			self.manager.Objects["highlighter"].update()

			# venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)
			self.manager.update()



#		fileLines = venicGlobals["modules"]["fileWindow"].fileLines
#		fileString = '\n'.join(fileLines)
#		replacedString = self.re.sub(firstString, secondString, fileString)
#		self.manager.Windows["fileWindow"].file.contents = replacedString
#		venicGlobals["modules"]["fileWindow"].fileLines = replacedString.splitlines()		

		self.window.erase()
		self.keepWindowInMainScreen()
		self.manager.Windows["fileWindow"].modified = True
		self.manager.Windows["fileWindow"].update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		self.manager.Objects["highlighter"].update()
		self.manager.update()

		# venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

#		if useSwapped == False:
		# use = ""


	def save(self):
		self.panel.show()
		self.panel.top()
		self.intendedX = 0
		self.intendedY = self.manager.stdscr.getmaxyx()[0]
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
		self.intendedHeight = 1
		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()
		self.window.addnstr(0,0,"Filename?", self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
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
			return
	## savefile string
	# keypress loop: begin catching characters
		self.window.erase()
		self.window.addnstr(0,0,self.saveString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
		if self.searchCursorX <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
			self.window.chgat(0,self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
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
				saveStringLeft = self.saveString[:self.searchCursorX]+c
				saveStringRight = self.saveString[self.searchCursorX:]
				self.saveString = saveStringLeft + saveStringRight
				self.searchCursorX += 1
			elif c == "KEY_LEFT" and self.searchCursorX > 0:
				self.searchCursorX -= 1
			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.saveString): # later deal with offscreen typing
				self.searchCursorX += 1
			elif c == "KEY_BACKSPACE":
				if self.searchCursorX > 0:
					saveStringLeft = self.saveString[:self.searchCursorX-1]
					saveStringRight = self.saveString[self.searchCursorX:]
					self.saveString = saveStringLeft + saveStringRight
					self.searchCursorX -= 1
			elif c == "KEY_DC":
				if self.searchCursorX+1 <= len(self.saveString): # if there is text to the right of our cursor
					saveStringLeft = self.saveString[:self.searchCursorX]
					saveStringRight = self.saveString[self.searchCursorX+1:]
					self.saveString = saveStringLeft+saveStringRight
			elif c == "^J":
				if self.saveString != "":
					break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0,0,self.saveString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			if self.searchCursorX <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
				self.window.chgat(0,self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
		self.manager.Windows["fileWindow"].file.source = self.saveString

	def terminate(self):
		pass

# # search functions, ctrl-F, ctrl-G

# def search():
# 	global use
# 	use = "search"

# def searchNext():
# 	global use
# 	use = "searchNext"

# def replace():
# 	global use
# 	use = "replace"

# def gotoLine():
# 	global use
# 	use = "gotoLine"
