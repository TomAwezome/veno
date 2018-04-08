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
		gotoLineCursorX = 0
		gotoLineString = ""
		use = ""
		patternMatches = None
		# standardscreen = self.manager.stdscr
		self.panel.top()
		self.panel.hide()

	def update(self):
		# global use, patternMatches, pattern, patternMatch, self.searchString, self.searchCursorX, gotoLineString, gotoLineCursorX, firstString, secondString
		self.cursor = self.manager.Windows["fileWindow"].filecursor
		#if use = search
		#elif use = gotoLine
		#elif use = searchNext
		#elif use = replace

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
		self.window.addnstr(0,0,self.searchString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
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
				searchStringLeft = self.searchString[:self.searchCursorX]+c
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
			self.window.addnstr(0,0,self.searchString, self.window.getmaxyx()[1]-1, self.manager.curses.A_REVERSE)
			if self.searchCursorX <= self.window.getmaxyx()[1]-2 and self.searchCursorX >= 0:
				self.window.chgat(0,self.searchCursorX, 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)
			self.manager.update()
		pattern = self.re.compile(self.searchString)
		patternMatches = pattern.finditer(self.manager.Windows["fileWindow"].file.contents)
		try:
			nextMatch = next(patternMatches)
			searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
			searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
		except StopIteration:
			pass
		try:
			while searchIndexY < self.cursor[1]:
				try:
					nextMatch = next(patternMatches)
					searchIndexY = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].count('\n')
					searchLines = self.manager.Windows["fileWindow"].file.contents[:nextMatch.start()].split('\n')
					if len(searchLines) > 0:
						searchIndexX = len(searchLines[len(searchLines)-1])
				except StopIteration:
					break

			while searchIndexY == self.cursor[1] and searchIndexX <= self.cursor[0]:
				try:
					nextMatch = next(patternMatches)
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

		# self.manager.Windows["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		# venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
		# venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

		# use = ""

# 	elif use == "searchNext":
# 		magicBarPanel.show()
# 		magicBarPanel.top()
# 		intendedX = 0
# 		intendedY = self.manager.stdscr.getmaxyx()[0]
# 		intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
# 		intendedHeight = 1
# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)

# #		if patternMatches == None:
# 	#		try:
# #		patternMatches = pattern.finditer(venicGlobals["venicFile"][patternMatch.end():])
# 		#	except: 
# 			#	return
# #		try:
# 		#if patternMatches != None:
# 		try:
# 			try:
# 				nextMatch = next(patternMatches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
# 			except TypeError:
# 				return
# 			searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 			searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 			if len(searchLines) > 0:
# 				searchIndexX = len(searchLines[len(searchLines)-1])
# #		except:
# #			exit()
# 			while cursor[1] > searchIndexY:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorUp()
# 			while cursor[1] < searchIndexY:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorDown()
# 			while cursor[0] > searchIndexX:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorLeft()
# 			while cursor[0] < searchIndexX:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorRight()
# 		except StopIteration:
# 			pass

# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 		venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
# 		venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
# 		venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

# 		use = ""

















# 	elif use == "replace":
# 		magicBarPanel.show()
# 		magicBarPanel.top()
# 		intendedX = 0
# 		intendedY = self.manager.stdscr.getmaxyx()[0]
# 		intendedWidth = self.manager.stdscr.getmaxyx()[1]-1
# 		intendedHeight = 1
# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
	
# #		magicBarWindow.box()
# #	magicBarWindow.addstr(0, 0, "222")

# 		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 		magicBarWindow.addnstr(0,0,self.searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
# 		if self.searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and self.searchCursorX >= 0:
# 			magicBarWindow.chgat(0,self.searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
# 		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)


# 	## search string
# 	# keypress loop: begin catching characters
# 		while True: # break out of this loop with enter key
# 			magicBarWindow.erase()
# 			try:
# 				c = venicGlobals["stdscr"].getch()
# 			except KeyboardInterrupt:
# 				break
# 			if c == -1:
# 				continue
# 			c = venicGlobals["curses"].keyname(c)
# 			c = c.decode("utf-8")
			
# 			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
# 				searchStringLeft = self.searchString[:self.searchCursorX]+c
# 				searchStringRight = self.searchString[self.searchCursorX:]
# 				self.searchString = searchStringLeft + searchStringRight
# 				self.searchCursorX += 1
# 			elif c == "KEY_LEFT" and self.searchCursorX > 0:
# 				self.searchCursorX -= 1
# 			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
# 				self.searchCursorX += 1
# 			elif c == "KEY_BACKSPACE":
# 				if self.searchCursorX > 0:
# 					searchStringLeft = self.searchString[:self.searchCursorX-1]
# 					searchStringRight = self.searchString[self.searchCursorX:]
# 					self.searchString = searchStringLeft + searchStringRight
# 					self.searchCursorX -= 1
# 			elif c == "KEY_DC":
# 				if self.searchCursorX+1 <= len(self.searchString): # if there is text to the right of our cursor
# 					searchStringLeft = self.searchString[:self.searchCursorX]
# 					searchStringRight = self.searchString[self.searchCursorX+1:]
# 					self.searchString = searchStringLeft+searchStringRight
# 			elif c == "^J":
# 				break
			
# 			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 			magicBarWindow.addnstr(0,0,self.searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
# 			if self.searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and self.searchCursorX >= 0:
# 				magicBarWindow.chgat(0,self.searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
# 			venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
		
# 		firstString = self.searchString
		
# 	## replacement string
# 	# keypress loop: begin catching characters
# 		self.searchString = ""
# 		self.searchCursorX = 0
# 		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 		magicBarWindow.addnstr(0,0,self.searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
# 		if self.searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and self.searchCursorX >= 0:
# 			magicBarWindow.chgat(0,self.searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
# 		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)

# 		while True: # break out of this loop with enter key
# 			magicBarWindow.erase()
# 			try:
# 				c = venicGlobals["stdscr"].getch()
# 			except KeyboardInterrupt:
# 				break
# 			if c == -1:
# 				continue
# 			c = venicGlobals["curses"].keyname(c)
# 			c = c.decode("utf-8")
			
# 			if c in self.string.punctuation + self.string.digits + self.string.ascii_letters + self.string.whitespace:
# 				searchStringLeft = self.searchString[:self.searchCursorX]+c
# 				searchStringRight = self.searchString[self.searchCursorX:]
# 				self.searchString = searchStringLeft + searchStringRight
# 				self.searchCursorX += 1
# 			elif c == "KEY_LEFT" and self.searchCursorX > 0:
# 				self.searchCursorX -= 1
# 			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
# 				self.searchCursorX += 1
# 			elif c == "KEY_BACKSPACE":
# 				if self.searchCursorX > 0:
# 					searchStringLeft = self.searchString[:self.searchCursorX-1]
# 					searchStringRight = self.searchString[self.searchCursorX:]
# 					self.searchString = searchStringLeft + searchStringRight
# 					self.searchCursorX -= 1
# 			elif c == "KEY_DC":
# 				if self.searchCursorX+1 <= len(self.searchString): # if there is text to the right of our cursor
# 					searchStringLeft = self.searchString[:self.searchCursorX]
# 					searchStringRight = self.searchString[self.searchCursorX+1:]
# 					self.searchString = searchStringLeft+searchStringRight
# 			elif c == "^J":
# 				break
			
# 			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 			magicBarWindow.addnstr(0,0,self.searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
# 			if self.searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and self.searchCursorX >= 0:
# 				magicBarWindow.chgat(0,self.searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
# 			venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
			
# 		secondString = self.searchString

# 		fileLines = venicGlobals["modules"]["fileWindow"].fileLines
# 		fileString = '\n'.join(fileLines)


# 		# next we'll find the first occurence (relative to our cursor) of our to-be-replaced string, and move the file cursor there and have our current nexMatch be that occurence

# 		pattern = re.compile(firstString)
# #		patternMatch = pattern.search(venicGlobals["venicFile"])
# 		patternMatches = pattern.finditer(venicGlobals["venicFile"])
# 		try:
# 			nextMatch = next(patternMatches)
# #		if patternMatch is not None:
# 			searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 			searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 			if len(searchLines) > 0:
# 				searchIndexX = len(searchLines[len(searchLines)-1])
# 		except StopIteration:
# 			pass

# 		try:
# 			while searchIndexY < cursor[1]:
# 				try:
# 					nextMatch = next(patternMatches)
# 					searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 					searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 					if len(searchLines) > 0:
# 						searchIndexX = len(searchLines[len(searchLines)-1])
# 				except StopIteration:
# 					break

# 			while searchIndexY == cursor[1] and searchIndexX < cursor[0]:
# 				try:
# 					nextMatch = next(patternMatches)
# 					searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 					searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 					if len(searchLines) > 0:
# 						searchIndexX = len(searchLines[len(searchLines)-1])
# 				except StopIteration:
# 					break

# 			while cursor[1] > searchIndexY:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorUp()
# 			while cursor[1] < searchIndexY:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorDown()
# 			while cursor[0] > searchIndexX:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorLeft()
# 			while cursor[0] < searchIndexX:
# 				venicGlobals["modules"]["fileWindow"].moveFilecursorRight()


# 			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 		except NameError:
# 			pass

# 		venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
# 		venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
# 		venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)
# 		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)


# 		# now we need to use .start() and .end() of match to chop and glue self.string. together, and re.sub the matching indices, and after replacing instance, repeat process again (using modified file, to adjust for differences in the indices after splicing replacement in)
# 		# while we do this, we need to factor in keypresses, so that users can enter 'y' or 'n' to replace match, and can use either ESC or ctrl-C to cancel this use of magicBar module

# 		# start while loop for keypresses (perhaps update window contents before this to show position at first instance)
# 			# if 'y':
# 				# replacedString = re.sub(firstString, secondString, fileString[start:end])
# 				# left = fileString[:start]
# 				# right = fileString[end:]
# 				# combined = left + replacedString + right
# 				# windowCodeLines = combined.splitlines()
# 				#? venicGlobals["venicFile"] = combined
# 			# if 'n':
# 				# pass
# 			# if 'esc'
# 				# break

# 			# patternMatches = pattern.finditer(venicGlobals["venicFile"])
# 			# nextMatch = next(patternMatches) # break if except StopIteration:
# 			# adjust cursor

# #		useSwapped = False
# 		while True: # break out of this loop with enter key
# 			try:
# 				nextMatch
# 			except NameError:
# 				break
# 			magicBarWindow.erase()
# 			magicBarWindow.addnstr(0, 0, "Replace? (y/n/a) ['a' = All]", magicBarWindow.getmaxyx()[1] - 1, venicGlobals["curses"].A_REVERSE)	
# 			venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
# 			try:
# 				c = venicGlobals["stdscr"].getch()
# 			except KeyboardInterrupt:
# 				break
# 			if c == -1:
# 				continue
# 			c = venicGlobals["curses"].keyname(c)
# 			c = c.decode("utf-8")
			
# 			if c == "y":
# 				fileLines = venicGlobals["modules"]["fileWindow"].fileLines
# 				fileString = '\n'.join(fileLines)

# 				replacedString = re.sub(firstString, secondString, fileString[nextMatch.start():nextMatch.end()])
# 				replaceStringLeft = fileString[:nextMatch.start()]
# 				replaceStringRight = fileString[nextMatch.end():]
# 				replaceStringCombined = replaceStringLeft + replacedString + replaceStringRight
# 				venicGlobals["modules"]["fileWindow"].fileLines = replaceStringCombined.splitlines()
# 				venicGlobals["venicFile"] = replaceStringCombined
# 			elif c == "n":
# 				pass
# 			elif c == "a":
# #				use = "replaceAll"
# #				useSwapped = True
# 				fileLines = venicGlobals["modules"]["fileWindow"].fileLines
# 				fileString = '\n'.join(fileLines)
# 				replacedString = re.sub(firstString, secondString, fileString)
# 				venicGlobals["venicFile"] = replacedString
# 				venicGlobals["modules"]["fileWindow"].fileLines = replacedString.splitlines()
# 				break

# #				self.searchCursorX += 1
# #			elif c == "KEY_LEFT" and self.searchCursorX > 0:
# #				self.searchCursorX -= 1
# #			elif c == "KEY_RIGHT" and self.searchCursorX < len(self.searchString): # later deal with offscreen typing
# #				self.searchCursorX += 1
# #			elif c == "KEY_BACKSPACE":
# #				if self.searchCursorX > 0:
# #					searchStringLeft = self.searchString[:self.searchCursorX-1]
# #					searchStringRight = self.searchString[self.searchCursorX:]
# #					self.searchString = searchStringLeft + searchStringRight
# #					self.searchCursorX -= 1
# 			elif c == "^J":
# 				break

# 			patternMatches = pattern.finditer(venicGlobals["venicFile"])
# 			try:
# 				nextMatch = next(patternMatches)
# #			if patternMatch is not None:
# 				searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 				searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 				if len(searchLines) > 0:
# 					searchIndexX = len(searchLines[len(searchLines)-1])
# 			except StopIteration:
# 				break

# 			try:
# 				while searchIndexY < cursor[1]:
# 					try:
# 						nextMatch = next(patternMatches)
# 						searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 						searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 						if len(searchLines) > 0:
# 							searchIndexX = len(searchLines[len(searchLines)-1])
# 					except StopIteration:
# 						break

# 				while searchIndexY == cursor[1] and searchIndexX < cursor[0]:
# 					try:
# 						nextMatch = next(patternMatches)
# 						searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
# 						searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
# 						if len(searchLines) > 0:
# 							searchIndexX = len(searchLines[len(searchLines)-1])
# 					except StopIteration:
# 						break

# 				while cursor[1] > searchIndexY:
# 					venicGlobals["modules"]["fileWindow"].moveFilecursorUp()
# 				while cursor[1] < searchIndexY:
# 					venicGlobals["modules"]["fileWindow"].moveFilecursorDown()
# 				while cursor[0] > searchIndexX:
# 					venicGlobals["modules"]["fileWindow"].moveFilecursorLeft()
# 				while cursor[0] < searchIndexX:
# 					venicGlobals["modules"]["fileWindow"].moveFilecursorRight()


# 				keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 			except NameError:
# 				pass

# 			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# #			magicBarWindow.addnstr(0,0,self.searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
# #			if self.searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and self.searchCursorX >= 0:
# #				magicBarWindow.chgat(0,self.searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
# 			venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
# 			venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
# 			venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)
# 			venicGlobals["modules"]["MainWindow"].loop(venicGlobals)



# #		fileLines = venicGlobals["modules"]["fileWindow"].fileLines
# #		fileString = '\n'.join(fileLines)
# #		replacedString = re.sub(firstString, secondString, fileString)
# #		venicGlobals["venicFile"] = replacedString
# #		venicGlobals["modules"]["fileWindow"].fileLines = replacedString.splitlines()		

# 		magicBarWindow.erase()
# 		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
# 		venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
# 		venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
# 		venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

# #		if useSwapped == False:
# 		use = ""



# 	# search mode
# 		# make visible, magicBarPanel.show()
# 		# perhaps change intended window info here for search configuration
# 		# set text to reverse text in draw operations...
# 		# catch keystrokes
# 			# each key, unless ^J aka enter key:
# 				# add to self.searchString
# 				# print self.searchString to bar
# 				# update window to show changes (mainWindow?)
# 			# if enter key:
# 				# self.searchString finished
# 		# catch all matches of self.searchString in file
# 			# if no matches, print 0 of 0 matches to bar
# 			# if matches:
# 				# print 1 of _ to bar
# 				# find first occurance, place filecursor at find index
# 				# upon further forward / backward operations:
# 					# move filecursor to next match index
# 					# update printed bar variable (e.g. 3 of 10)


# def kill(venicGlobals):
# 	pass
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