
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

		## colorMap dictionary with format of {"highlighterColorCode":RenderedColorCode}
		self.colorMap = self.manager.Objects["config"].options["ColorMap"]
		
		## Lexer for filetype
		self.lexer = None
		
		## FileWindow highlighter is attached to.
		self.fileWindow = self.manager.Windows["fileWindow"]
		
		try:
			try:
				self.lexer = self.lexers.guess_lexer_for_filename(
						self.fileWindow.file.source,
						self.fileWindow.file.contents
					)
			except:
				self.lexer = self.lexers.guess_lexer(
						self.fileWindow.file.contents
					)
			if self.lexer.name == "PHP":
				self.lexer = self.lexers.PhpLexer(startinline=True)
		except:
			pass
		self.fileWindow.modified = True
	##
	## @brief      Update syntax highlighting on fileWindow
	##
	## @param      self  The object
	##
	def update(self):
		viewportX = self.fileWindow.getViewportX()
		viewportY = self.fileWindow.getViewportY()
		windowMaxY = self.fileWindow.getWindowMaxY()
		windowMaxX = self.fileWindow.getWindowMaxX()
		windowCodeLines = self.fileWindow.fileLines
		windowCodeString = '\n'.join(windowCodeLines)
		tabExpandSize = self.manager.Objects["config"].options["TabExpandSize"]

		if self.lexer != None and self.fileWindow.modified == True:
			highlightedCodeString = self.pygments.highlight(windowCodeString, self.lexer, self.irc())
			## **Highlighted** code lines from windowCodeLines (which is default defined as fileLines[viewportY:viewportY + windowMaxY])
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
				self.highlightedCodeLines.extend([''] * trailingNewlines)
			if leadingNewlines > 0:
				self.highlightedCodeLines.reverse()
				self.highlightedCodeLines.extend([''] * leadingNewlines)
				self.highlightedCodeLines.reverse()

			self.fileWindow.modified = False
		elif self.lexer == None:
			highlightedCodeString = windowCodeString
			self.highlightedCodeLines = highlightedCodeString.split('\n')
			
			
		windowY = viewportY
		for line in self.highlightedCodeLines[windowY:windowY + windowMaxY]:
			properLine = line
			properLine = properLine.replace('\x1d', '')
			lineIndex = 0
			# at this point, each line is a string which has been colored, irregardless of the window x size
			# tabs are a \t character, and ctrl-C is a \x03 character; not expanded for tabs
			if '\x03' in properLine:
				colorInstances = properLine.count('\x03')
				opener = False
				closer = False
				openerCount = 0
				closerCount = 0
				colorData = [[]] # [[color, start, num]]
				colorDataRowIndex = 0
				while colorInstances > 0:
					colorIndex = properLine.find('\x03', lineIndex)
					lineIndex = colorIndex + 1
					# so what we want is this: start by checking for numbers (I THINK that pygments is working such that colors are simply one number, which uses two digits (none of that 3,5 crap))
					#			   if it's the number sequence we're expecting: that is now our point IN THE STRING DATA (NO TABS!) that our coloring begins
					#			   if there's no number sequence AFTER STARTING WITH A SEQUENCE: that is the point IN THE STRING DATA that our coloring stops
					# how to convert DATA index into TABBED index? after all, that's what's being tossed to the window we are changing the attributes of!
					# ... oh, do i need to subtract from the formatted string? given that its internal character indexes are technically being changed by the presence of ^C characters...
					if (colorIndex - (openerCount * 3) - closerCount) + \
						(len(windowCodeLines[windowY][:colorIndex].expandtabs(tabExpandSize)) - \
						len(windowCodeLines[windowY][:colorIndex])) - viewportX > windowMaxX: # if color is offscreen right
						
						if closer == True and colorData[colorDataRowIndex][1] - viewportX < windowMaxX - 1:	# if closer and opener is on screen
							colorData[colorDataRowIndex][1] = max(colorData[colorDataRowIndex][1] - viewportX, 0)
							colorData[colorDataRowIndex].append(windowMaxX + viewportX - colorData[colorDataRowIndex][1])
							colorDataRowIndex += 1
							closerCount += 1
							closer = False
							colorData.append([])
						else:	# if opener is also offscreen right
							colorData.pop()
						break
					if opener == False and closer == False:
						if str.isdigit(properLine[colorIndex + 1:colorIndex + 3]):
							opener = True
					if closer == True:
						if colorData[colorDataRowIndex][1] - viewportX < 0:	# if opener is offscreen
							if (colorIndex - (openerCount * 3) - closerCount) + \
								(len(windowCodeLines[windowY][:colorIndex].expandtabs(tabExpandSize)) - \
								len(windowCodeLines[windowY][:colorIndex])) - viewportX > 0: # if closer is on screen
								
								colorData[colorDataRowIndex][1] = 0
								colorData[colorDataRowIndex].append((colorIndex - (openerCount * 3) - closerCount) + \
									(len(windowCodeLines[windowY][:colorIndex].expandtabs(tabExpandSize)) - \
									len(windowCodeLines[windowY][:colorIndex])) - viewportX)
							else: # if closer is not on screen
								colorData.pop()
								colorDataRowIndex -= 1
						else:
							colorData[colorDataRowIndex].append((colorIndex - (openerCount * 3) - closerCount) + \
								(len(windowCodeLines[windowY][:colorIndex].expandtabs(tabExpandSize)) - \
								len(windowCodeLines[windowY][:colorIndex]))-colorData[colorDataRowIndex][1])
							colorData[colorDataRowIndex][1] = colorData[colorDataRowIndex][1] - viewportX

						colorDataRowIndex += 1
						closerCount += 1
						closer = False
						colorData.append([])
					if opener == True:
						colorData[colorDataRowIndex].append(properLine[colorIndex + 1:colorIndex + 3])
						colorData[colorDataRowIndex].append((colorIndex - (openerCount * 3) - closerCount) + \
							(len(windowCodeLines[windowY][:colorIndex].expandtabs(tabExpandSize)) - \
							len(windowCodeLines[windowY][:colorIndex])))
						openerCount += 1
						opener = False
						closer = True
					colorInstances -= 1
				for row in colorData:
					if row != []:
						self.fileWindow.window.chgat(windowY - viewportY, row[1], row[2], self.manager.curses.color_pair(self.colorMap[str(int(row[0]))]))
			windowY += 1
			if windowY > viewportY + windowMaxY-1:
				break
		self.drawSelect()
		self.fileWindow.drawCursor()

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

	##
	## @brief      Highlight text between filecursor and selectPosition, this allows onscreen coloration to show what text is currently being selected.
	##
	## @param      self  The object
	##
	def drawSelect(self):
	#i see: filecursor, selectposition, viewport, fileWindowmaxyx, (start/end)
		filecursorX = self.fileWindow.getFilecursorX()
		filecursorY = self.fileWindow.getFilecursorY()
		selectX = self.fileWindow.getSelectX()
		selectY = self.fileWindow.getSelectY()
		viewportX = self.fileWindow.getViewportX()
		viewportY = self.fileWindow.getViewportY()
		windowMaxY = self.fileWindow.getWindowMaxY()
		tabExpandSize = self.manager.Objects["config"].options["TabExpandSize"]
		if self.fileWindow.selectOn == True:
			if filecursorY > selectY:	  # if cursor below selectStart. 
				startX = selectX
				startY = selectY
				endX = filecursorX
				endY = filecursorY
			elif filecursorY < selectY: # if selectStart below cursor.
				startX = filecursorX
				startY = filecursorY
				endX = selectX
				endY = selectY
			elif filecursorY == selectY: # if they're the same row.
				if filecursorX == selectX: # if x index same on each
					startX = selectX
					startY = selectY
					endX = startX
					endY = startY
				elif filecursorX < selectX: # if cursor index before selection index. 
					startX = filecursorX
					startY = filecursorY
					endX = selectX
					endY = selectY
				elif filecursorX > selectX: # if cursor index after selection index. 
					startX = selectX
					startY = selectY
					endX = filecursorX
					endY = filecursorY
					
			yOffset = 0
			for line in self.fileWindow.fileLines[viewportY:viewportY + windowMaxY]: # for each line of window contents
				if viewportY + yOffset in range(startY, endY + 1): # if selection on screen

					if startY == endY: # if start and end on same line
						# chgat blue from extendTabString[start[0]:end[0]]
						tabDiff = len(line[:startX].expandtabs(tabExpandSize)) - len(line[:startX])
						if startX - viewportX + tabDiff < 0: # if start is off screen
							chgx = 0 # start blue from left edge of window.
							chgl = endX - viewportX #this should work. but. end[0] doesn't care if tabs are before it, spacing bugged. need new/same tabdiff?
							tabDiffEnd = len(line[:endX].expandtabs(tabExpandSize)) - len(line[:endX]) # similar tab difference but based on sel ends
							chgl+= tabDiffEnd
							if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
								chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						else: # start is on screen
							chgx = startX - viewportX + tabDiff
							chgl = len(line[startX:endX].expandtabs(tabExpandSize))
						self.fileWindow.window.chgat(startY - viewportY, chgx, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)

					elif startY == viewportY + yOffset: # elif line is line that select starts on
						tabDiff = len(line[:startX].expandtabs(tabExpandSize)) - len(line[:startX])
						if startX - viewportX + tabDiff < 0: # if start is off screen
							chgx = 0
							chgl = len(line.expandtabs(tabExpandSize)) - viewportX
							if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
								chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						else: # start is on screen
							chgx = startX - viewportX + tabDiff
							chgl = len(line[startX:].expandtabs(tabExpandSize))
						self.fileWindow.window.chgat(yOffset, chgx, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue from start[0] to end of line

					elif endY == viewportY + yOffset: # elif line is line that select ends on
						chgl = len(line[:endX].expandtabs(tabExpandSize)) - viewportX
						if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
							chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						self.fileWindow.window.chgat(yOffset, 0, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue from start to end[0] of line

					else: # elif line is between start and end
						chgl = len(line.expandtabs(tabExpandSize)) - viewportX
						if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
							chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						self.fileWindow.window.chgat(yOffset, 0, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue whole line
				yOffset += 1
