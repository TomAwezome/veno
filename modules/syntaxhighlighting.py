# import time

##
## @brief      Class for highlighter.
##
class Highlighter:
	##
	## @brief      Constructs the object.
	##
	## @param      self     The object
	## @param      manager  The manager to allow access to drawing on window object in FileWindow
	##
	def __init__(self, manager):
		## The manager to allow access to drawing on window object in FileWindow. TODO: replace manager with Window variable to further scale Highlighter
		self.manager = manager
		import pygments
		## Pygments module
		self.pygments = pygments
		import pygments.lexers as lexers
		## Pygments lexer module
		self.lexers = lexers
		from pygments.formatters import IRCFormatter
		## Pygments formatter IRCFormatter
		self.irc = IRCFormatter
# def start(venicGlobals):
# #	import pygments
# #	import pygments.lexers as lexers
# 	fileContents = venicGlobals["venicFile"]
# 	lexer = self.lexer
		# self.colorMap = {
		# "0":0,
		# "1":1,
		# "2":5,
		# "3":3,
		# "4":2,
		# "5":4,
		# "6":6,
		# "7":4,
		# "8":4,
		# "9":3,
		# "10":7,
		# "11":5,
		# "12":5,
		# "13":2,
		# "14":8,
		# "15":9 # Comments. This color.
		# }

		## colorMap dictionary with format of {"highlighterColorCode":RenderedColorCode}
		self.colorMap = {
		"0":9,
		"1":9,
		"2":10,#class,def,try,if,break,while,for,ints,pass
		"3":9,
		"4":9,
		"5":11,#quotes
		"6":10,#in,and,or
		"7":11,#class/function name, 
		"8":9,
		"9":9,
		"10":4,#self,modules,literals
		"11":9,
		"12":9,
		"13":9,
		"14":9,
		"15":9 # Comments. This color.
		}
		
		## Lexer for filetype
		self.lexer = None
		try:
			try:
				self.lexer = self.lexers.guess_lexer_for_filename(
						self.manager.Windows["fileWindow"].file.source,
						self.manager.Windows["fileWindow"].file.contents
					)
			except:
				self.lexer = self.lexers.guess_lexer(
						self.manager.Windows["fileWindow"].file.contents
					)
			if self.lexer.name == "PHP":
				self.lexer = self.lexers.PhpLexer(startinline=True)
		except:
			pass
		self.manager.Windows["fileWindow"].modified = True
	##
	## @brief      Update syntax highlighting on fileWindow
	##
	## @param      self  The object
	##
	def update(self):
		fileViewport = self.manager.Windows["fileWindow"].viewport
		windowSize = self.manager.Windows["fileWindow"].window.getmaxyx()
		# windowCodeLines = self.manager.Windows["fileWindow"].fileLines[fileViewport[1]:fileViewport[1]+windowSize[0]]
		windowCodeLines = self.manager.Windows["fileWindow"].fileLines
		windowCodeString = '\n'.join(windowCodeLines)
		if self.lexer != None and self.manager.Windows["fileWindow"].modified == True:
			highlightedCodeString = self.pygments.highlight(windowCodeString,self.lexer,self.irc())
			## **Highlighted** code lines from windowCodeLines (which is default defined as fileLines[viewport[1]:viewport[1]+windowSize[0]])
			self.highlightedCodeLines = highlightedCodeString.split('\n')
			self.manager.Windows["fileWindow"].modified = False
		elif self.lexer == None:
			highlightedCodeString = windowCodeString
			self.highlightedCodeLines = highlightedCodeString.split('\n')
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
			self.highlightedCodeLines.extend(['']*trailingNewlines)
		if leadingNewlines > 0:
			self.highlightedCodeLines.reverse()
			self.highlightedCodeLines.extend(['']*leadingNewlines)
			self.highlightedCodeLines.reverse()
		windowY = fileViewport[1]
		for line in self.highlightedCodeLines[windowY:windowY+windowSize[0]]:
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
					if (colorIndex-(openerCount*3)-(closerCount*1))+(len(windowCodeLines[windowY][:colorIndex].expandtabs(4))-len(windowCodeLines[windowY][:colorIndex]))-fileViewport[0] > windowSize[1]: # if color is offscreen right
						#if colorData != []:
						if closer == True and colorData[colorDataRowIndex][1]-fileViewport[0] < windowSize[1]-1:	# if closer and opener is on screen
							colorData[colorDataRowIndex][1] = max(colorData[colorDataRowIndex][1]-fileViewport[0],0)
							colorData[colorDataRowIndex].append(windowSize[1]+fileViewport[0]-colorData[colorDataRowIndex][1])
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
						self.manager.Windows["fileWindow"].window.chgat(windowY-fileViewport[1],row[1],row[2],self.manager.curses.color_pair(self.colorMap[str(int(row[0]))]))
			windowY += 1
			if windowY > fileViewport[1] + windowSize[0]-1:
				break
		self.manager.Windows["fileWindow"].drawCursor()
# #	where are we getting the string from? the active string... but we would only want the part that the user sees.
# #		we would need filewindow module variables: fileLines?, viewport, window size xy, 
# #	before we get there... how to color the screen? does it have to be character by character?
# #	no way!!!! that's insane. it can be done in chunks, searching for the next ^C character index each time.
	
	##
	## @brief      Terminates Highlighter
	##
	## @param      self  The object
	##
	def terminate(self):
		pass
# def kill(venicGlobals):
# 	pass








# get file viewport
# get window size
# get file lines corresponding to viewport
# make code string
# if there's a lexer
# 	HIGHLIGHT code string
# 	make highlightcode lines
# else
# 	code string->pretend highlight
# leading/trailing lines shit?
# WINDOWY=0
# for each LINE in HIGHLIGHTED code 	# refer line 6
# 	opener closer parser bullshit...
# 	for each ROW of COLORDATA made PER LINE via HIGHLIGHTEDCODELINES:
# 		change attribute at WINDOWY, indexX,length, color
# 	WINDOWY ++
# 	if WINDOWY > windowSize
# 		break



# ___Way I *should* do it____
# get file viewport
# get window size
# get file lines of entire window
# make code string
# if there's a lexer
# 	if we need to highlight all of the text again (if modified, if first run..)
# 	HIGHLIGHT code string
# 	make highlightcode lines
# else
# 	code string => pretend highlight
# leading trailing lines shit?
# WINDOWY=
