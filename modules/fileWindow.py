# import time
# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class FileWindow(Window):
	def __init__(self, manager, name, file):
		Window.__init__(self, manager, name)
		self.viewport = [0,0]
		self.filecursor = [0,0]
		self.panel.bottom()
		self.file = file
		self.fileLines = self.file.contents.splitlines()
		windowY = 0
		for line in self.fileLines[self.viewport[1]:self.viewport[1]+self.window.getmaxyx()[0]]:
			self.window.addnstr(windowY,0,line.expandtabs(self.manager.Objects["config"].options["TabExpandSize"])[self.viewport[0]:],self.window.getmaxyx()[1]-1)
			windowY += 1
		self.modified = True ## i.e. Modified since last highlight. Variable used for speed optimization of syntax highlighting algorithm.
		self.selectPosition = []
		self.selectOn = False
		self.quoteOnce = True
	def update(self):
		self.window.erase()
		self.intendedHeight = self.manager.stdscr.getmaxyx()[0] - self.intendedY - 1
		self.intendedWidth = self.manager.stdscr.getmaxyx()[1] - self.intendedX - 1
		self.keepWindowInMainScreen()
		# self.window.box()
		windowY = 0
		for line in self.fileLines[self.viewport[1]:self.viewport[1]+self.window.getmaxyx()[0]]:
			self.window.addnstr(windowY,0,line.expandtabs(self.manager.Objects["config"].options["TabExpandSize"])[self.viewport[0]:],self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(0))
			windowY += 1
		# self.drawSelect()
		self.drawCursor()
	def drawCursor(self):
		if self.filecursor[1] >= self.viewport[1] and self.filecursor[1] <= self.viewport[1]+self.window.getmaxyx()[0]-1:
			if len(self.fileLines) == 0:
				self.fileLines.append("")
			tabDiff = len(self.fileLines[self.filecursor[1]][:self.filecursor[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) - len(self.fileLines[self.filecursor[1]][:self.filecursor[0]])
			if self.filecursor[0]-self.viewport[0]+tabDiff <= self.window.getmaxyx()[1]-2 and self.filecursor[0]-self.viewport[0]+tabDiff >= 0:
				self.window.chgat(self.filecursor[1]-self.viewport[1],self.filecursor[0]-self.viewport[0]+tabDiff,1,self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
# 	def drawSelect(self):
# 		if self.selectOn == True:
# 			if self.filecursor[1] > self.selectPosition[1]:	  # if cursor below selectStart. 
# 				start = [self.selectPosition[0],self.selectPosition[1]]
# 				end = [self.filecursor[0],self.filecursor[1]]
# #				tabDiff = len(self.fileLines[self.selectPosition[1]][:self.selectPosition[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) - len(self.fileLines[self.selectPosition[1]][:self.selectPosition[0]])
# 			elif self.filecursor[1] < self.selectPosition[1]: # if selectStart below cursor.
# 				start = [self.filecursor[0],self.filecursor[1]]
# 				end = [self.selectPosition[0],self.selectPosition[1]]
# #				tabDiff = len(self.fileLines[self.selectPosition[1]][:self.selectPosition[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) - len(self.fileLines[self.selectPosition[1]][:self.selectPosition[0]])
# 			elif self.filecursor[1] == self.selectPosition[1]: # if they're the same row.
# 				if self.filecursor[0] == self.selectPosition[0]:
# 					start = [self.selectPosition[0],self.selectPosition[1]] # if x index same on each
# 					end = start
# 				elif self.filecursor[0] < self.selectPosition[0]: # if cursor index before selection index. 
# 					start = [self.filecursor[0],self.filecursor[1]]
# 					end = [self.selectPosition[0],self.selectPosition[1]]
# 				elif self.filecursor[0] > self.selectPosition[0]: # if cursor index after selection index. 
# 					start = [self.selectPosition[0],self.selectPosition[1]]
# 					end = [self.filecursor[0],self.filecursor[1]]
					
# 			yOffset = 0
# 			# for each line of window contents
# 			for line in self.fileLines[self.viewport[1]:self.viewport[1]+self.window.getmaxyx()[0]]:
# 				# if selection on screen
# 				if self.viewport[1]+yOffset in range(start[1],end[1]+1):
# 					# if start and end on same line
# 					if start[1] == end[1]:
# 						# chgat blue from extendTabString[start[0]:end[0]]
# 						tabDiff = len(line[:start[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) - len(line[:start[0]])
# 						self.window.chgat(start[1]-self.viewport[1],start[0]-self.viewport[0]+tabDiff,len(line[start[0]:end[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])),self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
# 					# elif line is line that select starts on
# 						# chgat blue from start[0] to end of line
# 					# elif line is between start and end
# 						# chgat blue whole line
# 					# elif line is line that select ends on
# 						# chgat blue from start to end[0] of line
# 				yOffset += 1

##### FUNCTIONS TO BE CALLED EXTERNALLY

	def toggleSelect(self):
		if self.selectOn == False:
			self.selectOn = True
			self.selectPosition = [self.filecursor[0],self.filecursor[1]]
		else:
			self.selectOn = False
			self.selectPosition = []

	def moveViewportDown(self):
		self.viewport[1] += 1
	def moveViewportUp(self):
		if self.viewport[1] > 0:
			self.viewport[1] -= 1
	def moveViewportRight(self):
		self.viewport[0] += 1
	def moveViewportLeft(self):
		if self.viewport[0] > 0:
			self.viewport[0] -= 1
	def moveFilecursorUp(self):
		if self.filecursor[1] > 0:
			self.filecursor[1] -= 1
			if self.filecursor[0] > len(self.fileLines[self.filecursor[1]]):
				if len(self.fileLines[self.filecursor[1]]) > 0:
					self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
				elif len(self.fileLines[self.filecursor[1]]) == 0:
					self.filecursor[0] = 0
			self.moveViewportToCursor()
	def moveFilecursorDown(self):
		if self.filecursor[1] < len(self.fileLines)-1:
			self.filecursor[1] += 1
			if self.filecursor[0] > len(self.fileLines[self.filecursor[1]]):
				if len(self.fileLines[self.filecursor[1]]) > 0:
					self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
				elif len(self.fileLines[self.filecursor[1]]) == 0:
					self.filecursor[0] = 0
			self.moveViewportToCursor()
	def moveFilecursorLeft(self):
		if self.filecursor[0] > 0:
			self.filecursor[0] -= 1
			self.moveViewportToCursor()
		elif self.filecursor[0] == 0 and self.filecursor[1] != 0:
			self.moveFilecursorUp()
			self.gotoEndOfLine()
	def moveFilecursorRight(self):
		if self.filecursor[0] < len(self.fileLines[self.filecursor[1]]):
			self.filecursor[0] += 1
			self.moveViewportToCursor()
		elif self.filecursor[0] == len(self.fileLines[self.filecursor[1]]) and self.filecursor[1] != len(self.fileLines)-1:
			self.moveFilecursorDown()
			self.gotoStartOfLine()
	def moveViewportToCursorX(self):
		tabDiff = len(self.fileLines[self.filecursor[1]][:self.filecursor[0]].expandtabs(self.manager.Objects["config"].options["TabExpandSize"])) - len(self.fileLines[self.filecursor[1]][:self.filecursor[0]])
		cursorX = self.filecursor[0] + tabDiff
		viewportWidth = self.window.getmaxyx()[1] - 2
		if self.viewport[0] > cursorX:
			self.viewport[0] = cursorX
		elif self.viewport[0] < cursorX - viewportWidth:
			self.viewport[0] = cursorX - viewportWidth
	def moveViewportToCursorY(self):
		cursorY = self.filecursor[1]
		viewportHeight = self.window.getmaxyx()[0] - 1
		if self.viewport[1] > cursorY:
			self.viewport[1] = cursorY
		elif self.viewport[1] < cursorY - viewportHeight:
			self.viewport[1] = cursorY - viewportHeight
	def moveViewportToCursor(self):
		self.moveViewportToCursorX()
		self.moveViewportToCursorY()
	def gotoLine(self, lineNum, preserveX = False):
		if lineNum < len(self.fileLines) and lineNum > -1:
			self.filecursor[1] = lineNum
			if (preserveX):
				if self.filecursor[0] > len(self.fileLines[self.filecursor[1]]):
					if len(self.fileLines[self.filecursor[1]]) > 0:
						self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
					elif len(self.fileLines[self.filecursor[1]]) == 0:
						self.filecursor[0] = 0
			else:
				self.filecursor[0] = 0
	#	elif lineNum > len(self.fileLines) and lineNum > -1:
	#		self.filecursor[1] = len(self.fileLines) - 1
	#		if (preserveX):
	#			if self.filecursor[0] > len(self.fileLines[self.filecursor[1]]):
	#				if len(self.fileLines[self.filecursor[1]]) > 0:
	#					self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
	#				elif len(self.fileLines[self.filecursor[1]]) == 0:
	#					self.filecursor[0] = 0
			self.moveViewportToCursor()
	def gotoStartOfFile(self):
		self.gotoLine(0)
	def gotoEndOfFile(self):
		self.gotoLine(len(self.fileLines)-1)
	def gotoStartOfLine(self):
		self.filecursor[0] = 0
		self.moveViewportToCursorX()
	def gotoEndOfLine(self):
		self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
		self.moveViewportToCursorX()
	def enterTextAtFilecursor(self, text):
		lineStringLeft = self.fileLines[self.filecursor[1]][:self.filecursor[0]]
		lineStringRight = self.fileLines[self.filecursor[1]][self.filecursor[0]:]
		lineStringLeft += text
		self.fileLines[self.filecursor[1]] = lineStringLeft + lineStringRight
		self.moveFilecursorRight()
		self.modified = True
		if text == "[":
			self.enterTextAtFilecursor("]")
			self.moveFilecursorLeft()
		elif text == "(":
			self.enterTextAtFilecursor(")")
			self.moveFilecursorLeft()
		elif text == "{":
			self.enterTextAtFilecursor("}")
			self.moveFilecursorLeft()
		elif text == "\"" and self.quoteOnce == True:
			self.quoteOnce = False
			self.enterTextAtFilecursor("\"")
			self.moveFilecursorLeft()
			self.quoteOnce = True
	def newLineAtFilecursor(self):
		lineStringLeft = self.fileLines[self.filecursor[1]][:self.filecursor[0]]
		lineStringRight = self.fileLines[self.filecursor[1]][self.filecursor[0]:]
		self.fileLines[self.filecursor[1]] = lineStringLeft
		self.fileLines.insert(self.filecursor[1]+1,"")
		self.moveFilecursorDown()
		self.fileLines[self.filecursor[1]] = lineStringRight
		self.modified = True
	def backspaceTextAtFilecursor(self):
		if self.filecursor[0] == 0:
			if self.filecursor[1] > 0:
				lineString = self.fileLines[self.filecursor[1]]
				self.fileLines.pop(self.filecursor[1])
				self.moveFilecursorUp()
				self.gotoEndOfLine()
				self.fileLines[self.filecursor[1]] += lineString
		else:
			lineStringLeft = self.fileLines[self.filecursor[1]][:self.filecursor[0]-1]
			lineStringRight = self.fileLines[self.filecursor[1]][self.filecursor[0]:]
			self.fileLines[self.filecursor[1]] = lineStringLeft+lineStringRight
			self.moveFilecursorLeft()
		self.modified = True
		# self.window.mvwin(0,0)
	def saveFile(self):
		fileString = ""
		linesRow = 0
		for line in self.fileLines:
			fileString += line+"\n"
		self.manager.Windows["magicBar"].save()
		self.file.save(fileString)
	#	fileString = fileString[:-1]
		# file.write(fileString)
		# file.close()
	def searchForText(self):
		pass
	def scrollDown(self):
		scrollAmount = 20
		self.gotoLine(min(self.filecursor[1] + scrollAmount, len(self.fileLines)-1))
	def scrollUp(self):
		scrollAmount = 20
		self.gotoLine(max(self.filecursor[1] - scrollAmount, 0))
	def deleteLineAtFilecursor(self):
		if self.filecursor[1] != len(self.fileLines)-1:
			self.fileLines.pop(self.filecursor[1])
			if len(self.fileLines[self.filecursor[1]]) >= self.filecursor[0]:
				pass
			else:
				self.filecursor[0] = len(self.fileLines[self.filecursor[1]])
		else:
			self.fileLines.pop(self.filecursor[1])
			if len(self.fileLines)-1 >= 0:
				self.moveFilecursorUp()
			else:
				self.filecursor[0] = 0
		self.modified = True
	def deleteTextAtFilecursor(self):
		if self.filecursor[0]+1 <= len(self.fileLines[self.filecursor[1]]): # if there is text to the right of our self.filecursor
			lineStringLeft = self.fileLines[self.filecursor[1]][:self.filecursor[0]]
			lineStringRight = self.fileLines[self.filecursor[1]][self.filecursor[0]+1:]
			self.fileLines[self.filecursor[1]] = lineStringLeft+lineStringRight
		elif self.filecursor[1] != len(self.fileLines)-1: # else (no text to right of self.filecursor) if there is line below
			nextLine = self.fileLines[self.filecursor[1]+1] # append line below to current line
			self.fileLines.pop(self.filecursor[1]+1)
			self.fileLines[self.filecursor[1]] += nextLine
		self.modified = True

