import re
import string
def keepWindowInMainScreen(H,W,Y,X,Window):
	offscreenY = 0
	offscreenX = 0
	offscreen = False
	windowAltered = False

	# if actual window does not fit in main screen

	if standardscreen.getmaxyx()[0] <= Window.getmaxyx()[0] + Window.getbegyx()[0]:	# if screen size x does not fit the window x
		offscreen = True
		offscreenY = Window.getbegyx()[0]+Window.getmaxyx()[0]-standardscreen.getmaxyx()[0]
		if Window.getbegyx()[0]-offscreenY < 0:
			Window.resize(Window.getmaxyx()[0]+(Window.getbegyx()[0]-offscreenY),Window.getmaxyx()[1])
			windowAltered = True
			offscreenY = Window.getbegyx()[0]+Window.getmaxyx()[0]-standardscreen.getmaxyx()[0]
	if standardscreen.getmaxyx()[1] <= Window.getmaxyx()[1] + Window.getbegyx()[1]:
		offscreen = True
		offscreenX = Window.getbegyx()[1]+Window.getmaxyx()[1]-standardscreen.getmaxyx()[1]
		if Window.getbegyx()[1]-offscreenX < 0:
			Window.resize(Window.getmaxyx()[0],Window.getmaxyx()[1]+(Window.getbegyx()[1]-offscreenX))
			windowAltered = True
			offscreenX = Window.getbegyx()[1]+Window.getmaxyx()[1]-standardscreen.getmaxyx()[1]
	if offscreen:
		Window.mvwin(Window.getbegyx()[0]-offscreenY,Window.getbegyx()[1]-offscreenX)
		windowAltered = True
	if standardscreen.getmaxyx()[0] == Window.getmaxyx()[0]:
		if Window.getmaxyx()[0]-1 <= 0:
			Window.resize(1,Window.getmaxyx()[1])
		else:
			Window.resize(Window.getmaxyx()[0]-1,Window.getmaxyx()[1])
		windowAltered = True
	if standardscreen.getmaxyx()[1] == Window.getmaxyx()[1]:
		if Window.getmaxyx()[1]-1 <= 0:
			Window.resize(Window.getmaxyx()[0], 1)
		else:
			Window.resize(Window.getmaxyx()[0], Window.getmaxyx()[1]-1)
		windowAltered = True

	# if there is space available to resize window closer to intended dimensions

	if H > Window.getmaxyx()[0] and standardscreen.getmaxyx()[0] > Window.getmaxyx()[0]+Window.getbegyx()[0]:
		Window.resize(Window.getmaxyx()[0]+(standardscreen.getmaxyx()[0]-Window.getmaxyx()[0]),Window.getmaxyx()[1])
		windowAltered = True
	if Window.getmaxyx()[0] > H:
		if H <= 0:
			H = 1
		Window.resize(H,Window.getmaxyx()[1])
		windowAltered = True
	if W > Window.getmaxyx()[1] and standardscreen.getmaxyx()[1] > Window.getmaxyx()[1]+Window.getbegyx()[1]:
		Window.resize(Window.getmaxyx()[0],Window.getmaxyx()[1]+(standardscreen.getmaxyx()[1]-Window.getmaxyx()[1]))
		windowAltered = True
	if Window.getmaxyx()[1] > W:
		if W <= 0:
			W = 1
		Window.resize(Window.getmaxyx()[0],W)
		windowAltered = True

	# if window can be moved closer to intended position

	if Y > Window.getbegyx()[0] and standardscreen.getmaxyx()[0] > Window.getmaxyx()[0]:
		if standardscreen.getmaxyx()[0] > Y+Window.getmaxyx()[0]:
			Window.mvwin(Y,Window.getbegyx()[1])
			windowAltered = True
		elif Y+Window.getmaxyx()[0] > standardscreen.getmaxyx()[0]:
			Window.mvwin(standardscreen.getmaxyx()[0]-Window.getmaxyx()[0],Window.getbegyx()[1])
			windowAltered = True
	if X > Window.getbegyx()[1] and standardscreen.getmaxyx()[1] > Window.getmaxyx()[1]:
		if standardscreen.getmaxyx()[1] > X+Window.getmaxyx()[1]:
			Window.mvwin(Window.getbegyx()[0],X)
			windowAltered = True
			
		elif X+Window.getmaxyx()[1] > standardscreen.getmaxyx()[1]:
			Window.mvwin(Window.getbegyx()[0],standardscreen.getmaxyx()[1]-Window.getmaxyx()[1])
			windowAltered = True
	changeX = Window.getbegyx()[1]
	changeY = Window.getbegyx()[0]
	if X < Window.getbegyx()[1] and X > 0:
		changeX = X
	if Y < Window.getbegyx()[0] and Y > 0:
		changeY = Y
	if changeX != Window.getbegyx()[1] or changeY != Window.getbegyx()[0]:
		Window.mvwin(changeY, changeX)
		windowAltered = True

	if windowAltered:
		standardscreen.erase()

global _globals
_globals = False

def start(venicGlobals):
	global _globals, standardscreen, intendedX, intendedY, intendedWidth, intendedHeight, magicBarWindow, magicBarPanel
	_globals = venicGlobals
	standardscreen = venicGlobals["stdscr"]
	intendedX = 0 # just some default values
	intendedY = 0
	intendedWidth = 1
	intendedHeight = 1
	magicBarWindow = venicGlobals["curses"].newwin(intendedHeight,intendedWidth,intendedY,intendedX) # sizeY sizeX posY posX
	magicBarWindow.erase()
	keepWindowInMainScreen(intendedHeight,intendedWidth,intendedY,intendedX,magicBarWindow)
	magicBarPanel = venicGlobals["panel"].new_panel(magicBarWindow)
	venicGlobals["magicBarPanel"] = magicBarPanel	# if panel not added to venicGlobals, garbage collector eats it
	magicBarPanel.top()
	magicBarPanel.hide()

def loop(venicGlobals):
	global _globals
	_globals = venicGlobals

# search mode
	# make visible, magicBarPanel.show()
	# perhaps change intended window info here for search configuration
	# set text to reverse text in draw operations...
	# catch keystrokes
		# each key, unless ^J aka enter key:
			# add to searchString
			# print searchString to bar
			# update window to show changes (mainWindow?)
		# if enter key:
			# searchString finished
	# catch all matches of searchString in file
		# if no matches, print 0 of 0 matches to bar
		# if matches:
			# print 1 of _ to bar
			# find first occurance, place filecursor at find index
			# upon further forward / backward operations:
				# move filecursor to next match index
				# update printed bar variable (e.g. 3 of 10)

# defaultString (callback): the initial string of the bar
# closeCallback (callback): callback run the the bar is closed
# openCallback (callback): callback run the the bar is open

class MagicBar:
	def __init__(self,
				 defaultString,
				 closeCallback,
				 defaultCursorX = -1,
				 changeCallback = (lambda x: True),
				 colors = False,
				 showCursor = True,
				 openCallback = (lambda x,y: True)):
		self.str = self.defaultString = defaultString
		self.closeCallback = closeCallback
		self.cursorX = defaultCursorX
		if (self.cursorX < 0):
			self.cursorX = 0
		self.changeCallback = changeCallback
		self.colors = colors
		if not self.colors:
			self.colors = _globals["curses"].A_REVERSE
		self.openCallback = openCallback
		self.closed = False
		self.showCursor = showCursor

	def open(self):
		global _globals
		magicBarPanel.show()
		magicBarPanel.top()

		intendedX = 0
		intendedY = standardscreen.getmaxyx()[0]
		intendedWidth = standardscreen.getmaxyx()[1]-1
		intendedHeight = 1
		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)

		_globals["modules"]["MainWindow"].loop(_globals)

		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
		magicBarWindow.addnstr(0,0,self.str, magicBarWindow.getmaxyx()[1]-1, self.colors)
		if self.showCursor and self.cursorX <= magicBarWindow.getmaxyx()[1]-2 and self.cursorX >= 0:
			magicBarWindow.chgat(0,self.cursorX, 1, _globals["curses"].color_pair(2) | self.colors)
		_globals["modules"]["MainWindow"].loop(_globals)

		self.openCallback(self.str, self.cursorX)

		enterPressed = False
		while not self.closed: # break out of this loop with enter key
			magicBarWindow.erase()
			try:
				c = _globals["stdscr"].getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = _globals["curses"].keyname(c)
			c = c.decode("utf-8")

			if c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.insertCharacter(self.cursorX, c)
			elif c == "KEY_LEFT" and self.cursorX > 0:
				self.cursorX -= 1
			elif c == "KEY_RIGHT" and self.cursorX < len(self.str): # later deal with offscreen typing
				self.cursorX += 1
			elif c == "KEY_BACKSPACE":
				if self.deleteCharacter(self.cursorX-1):
					self.cursorX -= 1
			elif c == "KEY_DC":
				if self.cursorX < len(self.str):
					self.deleteCharacter(self.cursorX)
			elif c == "^J":
				enterPressed = True
				break

			self.changeCallback(self)
			if self.closed:
				break
			self.render()
			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
			_globals["modules"]["MainWindow"].loop(_globals)

		self.close(enterPressed)

	def insertCharacter(self, cursorX, char):
		self.str = self.str[:cursorX] + char + self.str[cursorX:]
		self.cursorX += 1

	def deleteCharacter(self, cursorX):
		if cursorX > -1 and cursorX < len(self.str):
			self.str = self.str[:cursorX] + self.str[cursorX+1:]
			return True

	def render(self):
		global _globals
		magicBarWindow.addnstr(0,0,self.str, magicBarWindow.getmaxyx()[1]-1, self.colors)
		if self.showCursor and  self.cursorX <= magicBarWindow.getmaxyx()[1]-2 and self.cursorX >= 0:
			magicBarWindow.chgat(0,self.cursorX, 1, _globals["curses"].color_pair(2) | self.colors)

	def close(self, enterPressed=False):
		if self.closed:
			return
		self.closed = True
		global _globals
		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
		self.closeCallback(enterPressed, self.str)
		_globals["modules"]["fileWindow"].loop(_globals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		_globals["modules"]["syntaxHighlighting"].loop(_globals)
		_globals["modules"]["lineNumbers"].loop(_globals)

def kill(venicGlobals):
	pass

currentMagicBar = False
def closeExistingMagicBar():
	global currentMagicBar
	if currentMagicBar:
		currentMagicBar.close()
		currentMagicBar = False

def getSearchLines(searchString):
	pattern = re.compile(searchString)
	return pattern.finditer(_globals["venicFile"])

def getMatchY(match):
	if not match:
		return -1
	global _globals
	return _globals["venicFile"][:match.start()].count('\n')

def getMatchX(match):
	global _globals
	lines = _globals["venicFile"][:match.start()].split('\n')
	return len(lines[len(lines)-1])

def getSearchPosition(searchString, cursor, allowCurrent=False):
	patternMatches = getSearchLines(searchString)
	match = False
	minY = cursor[1]
	minX = cursor[0]+1
	if allowCurrent:
		minX = cursor[0]
	while (not match) or (getMatchY(match) < minY) or (getMatchY(match) == minY and getMatchX(match) < minX):
		try:
			match = next(patternMatches)
		except StopIteration:
			if match and ((getMatchY(match) < minY) or (getMatchY(match) == minY and getMatchX(match) < minX)):
				patternMatches = getSearchLines(searchString)
				match = next(patternMatches)
				cursor = [-1, -1]
			else:
				break
	return match


searchString = ""
def search(callback=False, allowCurrent=False):
	global currentMagicBar
	closeExistingMagicBar()
	global searchString, _globals

	def closeCallback(enterPressed, newSearchString):
		global searchString
		searchString = newSearchString
		if enterPressed:
			searchNext(True, allowCurrent)
			if callback:
				callback(searchString)
			return True

	currentMagicBar = _globals["modules"]["magicBar"].MagicBar(searchString, closeCallback, len(searchString))
	currentMagicBar.open()
	return currentMagicBar

def replace():
	def replaceCallback(searchString):
		closeExistingMagicBar()
		def closeCallback(enterPressed, replaceString):
			if enterPressed:
				replaceYN(searchString, replaceString)
			return True
		initialString = ""
		currentMagicBar = _globals["modules"]["magicBar"].MagicBar(initialString, closeCallback, len(initialString))
		currentMagicBar.open()
	return search(replaceCallback, True)

def replaceYN(searchStr, replaceString):
	closeExistingMagicBar()
	global _globals, searchString, searchMatch
	searchString = searchStr

	if not searchMatch:
		searchNext(True, True)

	infoStr = "Replace? (y/n/a) ['a' = All]"
	def charCallback(inst, char):
		fileLines = _globals["modules"]["fileWindow"].fileLines
		fileString = '\n'.join(fileLines)

		if char == "y":
			replacedString = re.sub(searchString, replaceString, fileString[searchMatch.start():searchMatch.end()])
			replaceStringLeft = fileString[:searchMatch.start()]
			replaceStringRight = fileString[searchMatch.end():]
			replaceStringCombined = replaceStringLeft + replacedString + replaceStringRight
			_globals["modules"]["fileWindow"].fileLines = replaceStringCombined.splitlines()
			_globals["venicFile"] = replaceStringCombined
			searchNext(True)
			if not searchMatch:
				inst.close()
		elif char == "n":
			searchNext(True)
		elif char == "a":
			replacedString = re.sub(searchString, replaceString, fileString)
			_globals["venicFile"] = replacedString
			_globals["modules"]["fileWindow"].fileLines = replacedString.splitlines()
			inst.close()

	return infoBar(infoStr, charCallback)

searchMatch = False
def searchNext(rerenderWindow=False, allowCurrent=False):
	global searchString, _globals, searchMatch
	cursor = _globals["modules"]["fileWindow"].filecursor
	searchMatch = getSearchPosition(searchString, cursor)
	if searchMatch:
		searchMatchX = getMatchX(searchMatch)
		searchMatchY = getMatchY(searchMatch)
		_globals["modules"]["fileWindow"].gotoXY(searchMatchX, searchMatchY)
		if rerenderWindow:
			_globals["modules"]["fileWindow"].loop(_globals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
			_globals["modules"]["syntaxHighlighting"].loop(_globals)
			_globals["modules"]["lineNumbers"].loop(_globals)

def gotoLine():
	global _globals
	closeExistingMagicBar()
	def closeCallback(enterPressed, lineNumberString):
		if enterPressed:
			_globals["modules"]["fileWindow"].gotoLine(int(lineNumberString) - 1)
		return True
	initialString = ""
	currentMagicBar = _globals["modules"]["magicBar"].MagicBar(initialString, closeCallback, len(initialString))
	currentMagicBar.open()
	return currentMagicBar

def infoBar(text, charCallback=False):
	global _globals
	closeExistingMagicBar()

	def changeCallback(inst):
		if len(inst.str) > len(text):
			if charCallback:
				char = inst.str[len(inst.str)-1]
				charCallback(inst, char)
			else:
				inst.close()
		inst.str = text
		inst.cursorX = len(text)
	def closeCallback(enterPressed, text):
		if enterPressed and charCallback:
			infoBar(text, charCallback)

	currentMagicBar = _globals["modules"]["magicBar"].MagicBar(text, closeCallback, len(text), changeCallback, _globals["curses"].A_REVERSE, showCursor=False)
	currentMagicBar.open()
	return currentMagicBar