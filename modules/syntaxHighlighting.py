import time
def start(venicGlobals):
#	import pygments
#	import pygments.lexers as lexers
	
	fileContents = venicGlobals["venicFile"]
	codeLexer = venicGlobals["lexer"]
#	codeLexer = lexers.python
#	venicGlobals["lexer"] = codeLexer
	from pygments.formatters import IRCFormatter
	global codeLexer, IRCFormatter

def loop(venicGlobals):
	fileViewport = venicGlobals["viewport"]
	windowSize = venicGlobals["filewin"].getmaxyx()
#	windowCodeLines = venicGlobals["modules"]["fileWindow"].fileLines[fileViewport[1]-1:fileViewport[1]+windowSize[0]]
	windowCodeLines = venicGlobals["modules"]["fileWindow"].fileLines[fileViewport[1]:fileViewport[1]+windowSize[0]]
	windowCodeString = '\n'.join(windowCodeLines)

	highlightedCodeString = venicGlobals["pygments"].highlight(windowCodeString,codeLexer,IRCFormatter())
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
			colorData = []	# [[color,start,num]]
			colorDataRowIndex = 0
			while colorInstances > 0:
				colorIndex = properLine.find('\x03',lineIndex)
				lineIndex = colorIndex+1
				
				# so what we want is this: start by checking for numbers (I THINK that pygments is working such that colors are simply one number, which uses two digits (none of that 3,5 crap))
				#			   if it's the number sequence we're expecting: that is now our point IN THE STRING DATA (NO TABS!) that our coloring begins
				#			   if there's no number sequence AFTER STARTING WITH A SEQUENCE: that is the point IN THE STRING DATA that our coloring stops
				# how to convert DATA index into TABBED index? after all, that's what's being tossed to the window we are changing the attributes of!
				# ... oh, do i need to subtract from the formatted string? given that its internal character indexes are technically being changed by the presence of ^C characters...


				if (colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex])) > windowSize[1]:
					colorData.pop()
					break

				if opener == False and closer == False:
					if str.isdigit(properLine[colorIndex+1:colorIndex+3]):
						opener = True
				
				if closer == True:
					colorData[colorDataRowIndex].append((colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))-colorData[colorDataRowIndex][1])
					colorDataRowIndex += 1
					
					closerCount += 1
					closer = False
					
					


#					(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))



				if opener == True:
					colorData.append([])
					colorData[colorDataRowIndex].append(properLine[colorIndex+1:colorIndex+3])
					colorData[colorDataRowIndex].append((colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex])))
					
					openerCount += 1
					opener = False
					closer = True
				

#				venicGlobals["filewin"].clear()
#				venicGlobals["filewin"].addstr(0,0,str(colorData))

#				venicGlobals["filewin"].addstr(0,0,"formatted line length: "+str(len(properLine)))
#				venicGlobals["filewin"].addstr(1,0,"original line length: "+str(len(windowCodeLines[windowY])))
#				venicGlobals["filewin"].addstr(1,0,str(colorIndex))
#				venicGlobals["filewin"].addstr(2,0,"original line: "+windowCodeLines[windowY])
#				venicGlobals["filewin"].addstr(3,0,"formatted line: "+str([properLine]))
#				venicGlobals["filewin"].addstr(2,0,str(lineIndex))
#				venicGlobals["filewin"].addstr(3,0,str(colorInstances))
#				venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
				colorInstances -= 1

#				time.sleep(.001)

#			venicGlobals["filewin"].chgat(windowY,0,venicGlobals["curses"].color_pair(3))
			for row in colorData:
				venicGlobals["filewin"].chgat(windowY,row[1],row[2],venicGlobals["curses"].color_pair(int(row[0])))
#				time.sleep(.1)
#				venicGlobals["modules"]["MainWindow"].loop(venicGlobals)
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
