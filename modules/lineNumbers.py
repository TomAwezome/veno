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
	global standardscreen, intendedX, intendedY, intendedWidth, intendedHeight, lineNumberWindow
	standardscreen = venicGlobals["stdscr"]

	intendedY = venicGlobals["filewin"].getbegyx()[0]
	intendedWidth = 5
	intendedX = venicGlobals["filewin"].getbegyx()[1] - intendedWidth
	intendedHeight = venicGlobals["filewin"].getmaxyx()[0]

	if intendedX < 0:
		intendedX = 0

	lineNumberWindow = venicGlobals["curses"].newwin(intendedHeight,intendedWidth,intendedY,intendedX) # sizeY sizeX posY posX
	lineNumberWindow.erase()

	keepWindowInMainScreen(intendedHeight,intendedWidth,intendedY,intendedX,lineNumberWindow)

	lineNumberPanel = venicGlobals["panel"].new_panel(lineNumberWindow)
	venicGlobals["lineNumberPanel"] = lineNumberPanel	# if panel not added to venicGlobals, garbage collector eats it
	# lineNumberPanel.top()
	venicGlobals["filepanel"].top()

def loop(venicGlobals):
	global totalLines
	lineNumberWindow.erase()

	totalLines = len(venicGlobals["modules"]["fileWindow"].fileLines)
	intendedWidth = len(str(totalLines))+2
	intendedX = venicGlobals["filewin"].getbegyx()[1] - intendedWidth+1
	intendedY = venicGlobals["filewin"].getbegyx()[0]
	intendedHeight = venicGlobals["filewin"].getmaxyx()[0]

	#venicGlobals["modules"]["fileWindow"].forceWindowCheck()

	# intendedX = venicGlobals["filewin"].getbegyx()[1]
	keepWindowInMainScreen(intendedHeight,intendedWidth,intendedY,intendedX,lineNumberWindow)
	if intendedX >= 0:
		lineNumberWindow.mvwin(intendedY,intendedX)
	else:
		lineNumberWindow.mvwin(intendedY,0)

	# lineNumberWindow.box()
	windowY = 0
	currentLine = venicGlobals["modules"]["fileWindow"].viewport[1]
	if intendedX >= 0:
		while windowY < lineNumberWindow.getmaxyx()[0] and windowY+currentLine < totalLines:
			# venicGlobals["debug"]["empty file LN"] = (windowY,0,str(currentLine+windowY)+(" "*(len(str(totalLines))-len(str(currentLine+windowY))))+"┃")
			lineNumberWindow.addstr(windowY,0,str(currentLine+windowY+1)+(" "*(len(str(totalLines))-len(str(currentLine+windowY+1))))+"┃")
			windowY += 1

	# lineNumberWindow.addstr(0,0,str(intendedY))

def kill(venicGlobals):
	pass
