# file window covers everything about a file and seeing it visually
# filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).
def start(venicGlobals):
	global filewin, viewport, fileLines, filecursor, standardscreen, filename
	standardscreen = venicGlobals["stdscr"]
	filename = venicGlobals["venicFileName"]
	viewport = [0,0]
	filecursor = [0,0]
	venicGlobals["viewport"] = viewport
	filewin = venicGlobals["curses"].newwin(venicGlobals["curses"].LINES, venicGlobals["curses"].COLS,0,0)
	filewin.erase()
	
	filepanel = venicGlobals["panel"].new_panel(filewin)
	venicGlobals["filepanel"] = filepanel
	filepanel.bottom()

	# create line array
	fileLines = venicGlobals["venicFile"].splitlines()
	# for loop to orient drawing each line to the window? :(
		# we are walking down the screen, we need to keep track of what line we're on
	windowY = 0
	for line in fileLines[viewport[1]:viewport[1]+standardscreen.getmaxyx()[0]]:
		filewin.addnstr(windowY,0,line.expandtabs(4)[viewport[0]:],standardscreen.getmaxyx()[1]-1)
		windowY += 1
			
def loop(venicGlobals):
	global tabDiff
	filewin.erase()
	windowY = 0
	for line in fileLines[viewport[1]:viewport[1]+standardscreen.getmaxyx()[0]]:
		filewin.addnstr(windowY,0,line.expandtabs(4)[viewport[0]:],standardscreen.getmaxyx()[1]-1)
		windowY += 1

	if filecursor[1] >= viewport[1] and filecursor[1] <= viewport[1]+standardscreen.getmaxyx()[0]-1:	
		tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
		if filecursor[0]-viewport[0]+tabDiff <= standardscreen.getmaxyx()[1]-2 and filecursor[0]-viewport[0]+tabDiff >= 0:
			filewin.chgat(filecursor[1]-viewport[1],filecursor[0]-viewport[0]+tabDiff,1,venicGlobals["curses"].color_pair(3) | venicGlobals["curses"].A_REVERSE)

def kill(venicGlobals):
	pass

### FUNCTIONS TO BE CALLED EXTERNALLY

def moveViewportDown():
	viewport[1] += 1
def moveViewportUp():
	if viewport[1] > 0:
		viewport[1] -= 1
def moveViewportRight():
	viewport[0] += 1
def moveViewportLeft():
	if viewport[0] > 0:
		viewport[0] -= 1

def moveFilecursorUp():
	if filecursor[1] > 0:
		filecursor[1] -= 1
		if filecursor[0] > len(fileLines[filecursor[1]]):
			if len(fileLines[filecursor[1]]) > 0:
				filecursor[0] = len(fileLines[filecursor[1]])
			elif len(fileLines[filecursor[1]]) == 0:
				filecursor[0] = 0
	while filecursor[1] < viewport[1]:
		moveViewportUp()
	while filecursor[1] > standardscreen.getmaxyx()[0]+viewport[1]-1:
		moveViewportDown()
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff > standardscreen.getmaxyx()[1]-2:
		moveViewportRight()
	while filecursor[0]-viewport[0]+tabDiff < 0:
		moveViewportLeft()


def moveFilecursorDown():
	if filecursor[1] < len(fileLines)-1:
		filecursor[1] += 1
		if filecursor[0] > len(fileLines[filecursor[1]]):
			if len(fileLines[filecursor[1]]) > 0:
				filecursor[0] = len(fileLines[filecursor[1]])
			elif len(fileLines[filecursor[1]]) == 0:
				filecursor[0] = 0
		while filecursor[1] > standardscreen.getmaxyx()[0]+viewport[1]-1:
			moveViewportDown()
		while filecursor[1] < viewport[1]:
			moveViewportUp()
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff > standardscreen.getmaxyx()[1]-2:
		moveViewportRight()
	while filecursor[0]-viewport[0]+tabDiff < 0:
		moveViewportLeft()


def moveFilecursorLeft():
	if filecursor[0] > 0:
		filecursor[0] -= 1
	elif filecursor[0] == 0 and filecursor[1] != 0:
		moveFilecursorUp()
		gotoEndOfLine()
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff > standardscreen.getmaxyx()[1]-2:
		moveViewportRight()
	while filecursor[0]-viewport[0]+tabDiff < 0:
		moveViewportLeft()

def moveFilecursorRight():
	if filecursor[0] < len(fileLines[filecursor[1]]):
		filecursor[0] += 1
	elif filecursor[0] == len(fileLines[filecursor[1]]) and filecursor[1] != len(fileLines)-1:
		moveFilecursorDown()
		gotoStartOfLine()
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff > standardscreen.getmaxyx()[1]-2:
		moveViewportRight()
	while filecursor[0]-viewport[0]+tabDiff < 0:
		moveViewportLeft()

def gotoStartOfLine():
	filecursor[0] = 0
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff < 0:
		moveViewportLeft()

def gotoEndOfLine():
	filecursor[0] = len(fileLines[filecursor[1]])
	tabDiff = len(fileLines[filecursor[1]][:filecursor[0]].expandtabs(4)) - len(fileLines[filecursor[1]][:filecursor[0]])
	while filecursor[0]-viewport[0]+tabDiff > standardscreen.getmaxyx()[1]-2:
		moveViewportRight()

def enterTextAtFilecursor(text):
	lineStringLeft = fileLines[filecursor[1]][:filecursor[0]]
	lineStringRight = fileLines[filecursor[1]][filecursor[0]:]
	lineStringLeft += text
	fileLines[filecursor[1]] = lineStringLeft + lineStringRight
	moveFilecursorRight()

def newLineAtFilecursor():
	lineStringLeft = fileLines[filecursor[1]][:filecursor[0]]
	lineStringRight = fileLines[filecursor[1]][filecursor[0]:]
	fileLines[filecursor[1]] = lineStringLeft
	fileLines.insert(filecursor[1]+1,"")
	moveFilecursorDown()
	fileLines[filecursor[1]] = lineStringRight

def backspaceTextAtFilecursor():
	if filecursor[0] == 0:
		if filecursor[1] > 0:
			lineString = fileLines[filecursor[1]]
			fileLines.pop(filecursor[1])
			moveFilecursorUp()
			gotoEndOfLine()
			fileLines[filecursor[1]] += lineString
	else:
		lineStringLeft = fileLines[filecursor[1]][:filecursor[0]-1]
		lineStringRight = fileLines[filecursor[1]][filecursor[0]:]
		fileLines[filecursor[1]] = lineStringLeft+lineStringRight
		moveFilecursorLeft()

def saveFile():
	file = open(filename,'w')
	fileString = ""
	linesRow = 0
	for line in fileLines:
		fileString += line+"\n"
#	fileString = fileString[:-1]
	file.write(fileString)
	file.close()
