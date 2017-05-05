import time
def start(venicGlobals):
#	import pygments
#	import pygments.lexers as lexers
	
	fileContents = venicGlobals["venicFile"]
	codeLexer = venicGlobals["lexer"]

	colorMap = {
	"0":0,
	"1":1,
	"2":5,
	"3":3,
	"4":2,
	"5":4,
	"6":6,
	"7":4,
	"8":4,
	"9":3,
	"10":7,
	"11":5,
	"12":5,
	"13":2,
	"14":8,
	"15":8
	}

#	codeLexer = lexers.python
#	venicGlobals["lexer"] = codeLexer
	from pygments.formatters import IRCFormatter
	global codeLexer, IRCFormatter, colorMap

def loop(venicGlobals):
	fileViewport = venicGlobals["viewport"]
	windowSize = venicGlobals["filewin"].getmaxyx()
#	windowCodeLines = venicGlobals["modules"]["fileWindow"].fileLines[fileViewport[1]-1:fileViewport[1]+windowSize[0]]
	windowCodeLines = venicGlobals["modules"]["fileWindow"].fileLines[fileViewport[1]:fileViewport[1]+windowSize[0]]
	windowCodeString = '\n'.join(windowCodeLines)

	if venicGlobals["lexer"] != None:
		highlightedCodeString = venicGlobals["pygments"].highlight(windowCodeString,codeLexer,IRCFormatter())
		highlightedCodeLines = highlightedCodeString.split('\n')
	else:
		highlightedCodeString = windowCodeString
		highlightedCodeLines = highlightedCodeString.split('\n')

	
	windowY = 0

#	if fileViewport[0] == 0:
#		exit()

	# problem is a bit different than originally thought... it snips both leading and trailing newlines. >:(
	# is there a way we could use the windowCodeLines, which will be more faithful to the actual window during iteration?
	# regular expressions could get into this I suppose... iteration until first non-newline character, but that's a computational waste...
	# for lack of a better method, I think I'll have to go with iteration... it would at most result in an extra iteration of the
		# file contents visible to the screen (assuming the WHOLE SCREEN is newlines...),

	leadingNewlines = 0
	for line in windowCodeLines:
		if line == '':
			leadingNewlines += 1
		else:
			break
	windowCodeLines.reverse()
	trailingNewlines = 0
	for line in windowCodeLines:
		if line == '':
			trailingNewlines += 1
		else:
			break
	windowCodeLines.reverse()

	if trailingNewlines > 0:
		highlightedCodeLines.extend(['']*trailingNewlines)
	if leadingNewlines > 0:
		highlightedCodeLines.reverse()
		highlightedCodeLines.extend(['']*leadingNewlines)
		highlightedCodeLines.reverse()


#	venicGlobals["filewin"].addstr(0,0,str(highlightedCodeLines))
	for line in highlightedCodeLines:
		properLine = line
		properLine = properLine.replace('\x1d','')
		lineIndex = 0
		# at this point, each line is a string which has been colored, irregardless of the window x size
		# tabs are a \t character, and ctrl-C is a \x03 character; not expanded for tabs
		if '\x03' in properLine:
			colorInstances = properLine.count('\x03')
			opener = False
			closer = False
			openerCount = 0
			closerCount = 0
			colorData = [[]]	# [[color,start,num]]
			colorDataRowIndex = 0
			while colorInstances > 0:
				colorIndex = properLine.find('\x03',lineIndex)
				lineIndex = colorIndex+1
				
				# so what we want is this: start by checking for numbers (I THINK that pygments is working such that colors are simply one number, which uses two digits (none of that 3,5 crap))
				#			   if it's the number sequence we're expecting: that is now our point IN THE STRING DATA (NO TABS!) that our coloring begins
				#			   if there's no number sequence AFTER STARTING WITH A SEQUENCE: that is the point IN THE STRING DATA that our coloring stops
				# how to convert DATA index into TABBED index? after all, that's what's being tossed to the window we are changing the attributes of!
				# ... oh, do i need to subtract from the formatted string? given that its internal character indexes are technically being changed by the presence of ^C characters...


				if (colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex])) > windowSize[1]: # if color is offscreen right
					#if colorData != []:
					if closer == True and colorData[colorDataRowIndex][1] < windowSize[1]-1:	# if closer and opener is on screen
						colorData[colorDataRowIndex][1] = max(colorData[colorDataRowIndex][1]-fileViewport[0],0)
						colorData[colorDataRowIndex].append(windowSize[1]-colorData[colorDataRowIndex][1])
						colorDataRowIndex += 1
						closerCount += 1
						closer = False
						colorData.append([])
					else:	# if opener is also offscreen right
						colorData.pop()
					break



				if opener == False and closer == False:
					if str.isdigit(properLine[colorIndex+1:colorIndex+3]):
						opener = True
				
				if closer == True:
					if colorData[colorDataRowIndex][1]-fileViewport[0] < 0:	# if opener is offscreen
						if (colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))-fileViewport[0] > 0: # if closer is on screen
							colorData[colorDataRowIndex][1] = 0
							colorData[colorDataRowIndex].append((colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))-fileViewport[0])
						else: # if closer is not on screen
							colorData.pop()
							colorDataRowIndex -= 1
					else:
						colorData[colorDataRowIndex].append((colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))-colorData[colorDataRowIndex][1])
						colorData[colorDataRowIndex][1] = colorData[colorDataRowIndex][1]-fileViewport[0]

					colorDataRowIndex += 1
					
					closerCount += 1
					closer = False
					colorData.append([])

				if opener == True:
					colorData[colorDataRowIndex].append(properLine[colorIndex+1:colorIndex+3])
					colorData[colorDataRowIndex].append((colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex])))
					openerCount += 1
					opener = False
					closer = True


				colorInstances -= 1

			for row in colorData:
				if row != []:
					venicGlobals["filewin"].chgat(windowY,row[1],row[2],venicGlobals["curses"].color_pair(colorMap[str(int(row[0]))]))
		windowY += 1
		if windowY > windowSize[0]-1:
			break
	venicGlobals["modules"]["fileWindow"].drawCursor(venicGlobals)
#	where are we getting the string from? the active string... but we would only want the part that the user sees.
#		we would need filewindow module variables: fileLines?, viewport, window size xy, 
#	before we get there... how to color the screen? does it have to be character by character?
#	no way!!!! that's insane. it can be done in chunks, searching for the next ^C character index each time.
def kill(venicGlobals):
	pass
