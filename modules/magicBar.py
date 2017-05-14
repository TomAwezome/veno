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
def start(venicGlobals):
	global standardscreen, intendedX, intendedY, intendedWidth, intendedHeight, magicBarWindow, magicBarPanel, use, patternMatches
	use = ""
	patternMatches = None
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
	global use, patternMatches, pattern, patternMatch
	cursor = venicGlobals["modules"]["fileWindow"].filecursor
#	magicBarWindow.erase()
	# change intended window info here

#	keepWindowInMainScreen(intendedHeight,intendedWidth,intendedY,intendedX,magicBarWindow)

	if use == "search":
		magicBarPanel.show()
		magicBarPanel.top()
		intendedX = 0
		intendedY = standardscreen.getmaxyx()[0]
		intendedWidth = standardscreen.getmaxyx()[1]-1
		intendedHeight = 1
		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
	
		magicBarWindow.box()
#	magicBarWindow.addstr(0, 0, "222")
		searchCursorX = 0 
		searchString = ""
		venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
	# keypress loop: begin catching characters
		while True: # break out of this loop with enter key
			magicBarWindow.erase()
			c = venicGlobals["stdscr"].getch()
			if c == -1:
				continue
			c = venicGlobals["curses"].keyname(c)
			c = c.decode("utf-8")
			
			if c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				searchStringLeft = searchString[:searchCursorX]+c
				searchStringRight = searchString[searchCursorX:]
				searchString = searchStringLeft + searchStringRight
				searchCursorX += 1
			elif c == "KEY_LEFT" and searchCursorX > 0:
				searchCursorX -= 1
			elif c == "KEY_RIGHT" and searchCursorX < len(searchString): # later deal with offscreen typing
				searchCursorX += 1
			elif c == "KEY_BACKSPACE":
				if searchCursorX > 0:
					searchStringLeft = searchString[:searchCursorX-1]
					searchStringRight = searchString[searchCursorX:]
					searchString = searchStringLeft + searchStringRight
					searchCursorX -= 1
			elif c == "^J":
				break
			
			keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
			magicBarWindow.addnstr(0,0,searchString, magicBarWindow.getmaxyx()[1]-1, venicGlobals["curses"].A_REVERSE)
			if searchCursorX <= magicBarWindow.getmaxyx()[1]-2 and searchCursorX >= 0:
				magicBarWindow.chgat(0,searchCursorX, 1, venicGlobals["curses"].color_pair(2) | venicGlobals["curses"].A_REVERSE)
			venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
		
		pattern = re.compile(searchString)
#		patternMatch = pattern.search(venicGlobals["venicFile"])
		patternMatches = pattern.finditer(venicGlobals["venicFile"])
		try:
			nextMatch = next(patternMatches)
#		if patternMatch is not None:
			searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
			searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')

			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
		
			while cursor[1] > searchIndexY:
				venicGlobals["modules"]["fileWindow"].moveFilecursorUp()
			while cursor[1] < searchIndexY:
				venicGlobals["modules"]["fileWindow"].moveFilecursorDown()
			while cursor[0] > searchIndexX:
				venicGlobals["modules"]["fileWindow"].moveFilecursorLeft()
			while cursor[0] < searchIndexX:
				venicGlobals["modules"]["fileWindow"].moveFilecursorRight()
		except StopIteration:
			pass


		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
		venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
		venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

		use = ""
	
	elif use == "searchNext":
		magicBarPanel.show()
		magicBarPanel.top()
		intendedX = 0
		intendedY = standardscreen.getmaxyx()[0]
		intendedWidth = standardscreen.getmaxyx()[1]-1
		intendedHeight = 1
		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)

#		if patternMatches == None:
	#		try:
#		patternMatches = pattern.finditer(venicGlobals["venicFile"][patternMatch.end():])
		#	except: 
			#	return
#		try:
		#if patternMatches != None:
		try:
			nextMatch = next(patternMatches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
			searchIndexY = venicGlobals["venicFile"][:nextMatch.start()].count('\n')
			searchLines = venicGlobals["venicFile"][:nextMatch.start()].split('\n')
			if len(searchLines) > 0:
				searchIndexX = len(searchLines[len(searchLines)-1])
#		except:
#			exit()
			while cursor[1] > searchIndexY:
				venicGlobals["modules"]["fileWindow"].moveFilecursorUp()
			while cursor[1] < searchIndexY:
				venicGlobals["modules"]["fileWindow"].moveFilecursorDown()
			while cursor[0] > searchIndexX:
				venicGlobals["modules"]["fileWindow"].moveFilecursorLeft()
			while cursor[0] < searchIndexX:
				venicGlobals["modules"]["fileWindow"].moveFilecursorRight()
		except StopIteration:
			pass

		keepWindowInMainScreen(intendedHeight, intendedWidth, intendedY, intendedX, magicBarWindow)
		venicGlobals["modules"]["fileWindow"].loop(venicGlobals) # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement
		venicGlobals["modules"]["syntaxHighlighting"].loop(venicGlobals)
		venicGlobals["modules"]["lineNumbers"].loop(venicGlobals)

		use = ""

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


def kill(venicGlobals):
	pass

# search functions, ctrl-F, ctrl-G

def search():
	global use
	use = "search"

def searchNext():
	global use
	use = "searchNext"
