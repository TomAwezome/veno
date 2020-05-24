# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class FileWindow(Window):
	def __init__(self, manager, name, file):
		Window.__init__(self, manager, name)
		self.viewport = [0, 0] #   [X, Y]
		self.filecursor = [0, 0] # [X, Y]
		self.panel.bottom()
		self.file = file
		self.fileLines = self.file.contents.splitlines()
		self.config = self.manager.Objects["config"].options
		windowY = 0
		for line in self.fileLines[self.getViewportY():self.getViewportY() + self.getWindowMaxY()]:
			self.window.addnstr(windowY, 0, line.expandtabs(self.config["TabExpandSize"])[self.getViewportX():], self.getWindowMaxX() - 1)
			windowY += 1
		self.modified = True ## i.e. Modified since last highlight. Variable used for speed optimization of syntax highlighting algorithm.
		self.selectPosition = []
		self.selectOn = False
		self.quoteOnce = True
		self.copyLines = []
	def update(self):
		self.window.erase()
		self.intendedHeight = self.getStdscrMaxY() - self.intendedY - 1
		self.intendedWidth = self.getStdscrMaxX() - self.intendedX - 1
		self.keepWindowInMainScreen()
		windowY = 0
		for line in self.fileLines[self.getViewportY():self.getViewportY() + self.getWindowMaxY()]:
			self.window.addnstr(windowY, 0, line.expandtabs(self.config["TabExpandSize"])[self.getViewportX():], self.getWindowMaxX() - 1, self.manager.curses.color_pair(0))
			windowY += 1
		self.drawCursor()
	def drawCursor(self):
		if self.getFilecursorY() >= self.getViewportY() and self.getFilecursorY() <= self.getViewportY() + self.getWindowMaxY() - 1:
			if len(self.fileLines) == 0:
				self.fileLines.append("")
			tabDiff = len(self.fileLines[self.getFilecursorY()][:self.getFilecursorX()].expandtabs(self.config["TabExpandSize"])) - len(self.fileLines[self.getFilecursorY()][:self.getFilecursorX()])
			if self.getFilecursorX() - self.getViewportX() + tabDiff <= self.getWindowMaxX() - 2 and self.getFilecursorX() - self.getViewportX() + tabDiff >= 0:
				self.window.chgat(self.getFilecursorY() - self.getViewportY(), self.getFilecursorX() - self.getViewportX() + tabDiff, 1, self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

##### FUNCTIONS TO BE CALLED EXTERNALLY

	def getViewportX(self):
		return self.viewport[0]
	def getViewportY(self):
		return self.viewport[1]
	def getFilecursorX(self):
		return self.filecursor[0]
	def getFilecursorY(self):
		return self.filecursor[1]
	def getSelectX(self):
		if self.selectPosition != []:
			return self.selectPosition[0]
	def getSelectY(self):
		if self.selectPosition != []:
			return self.selectPosition[1]
	def setViewportX(self, x):
		self.viewport[0] = x
	def setViewportY(self, y):
		self.viewport[1] = y
	def setFilecursorX(self, x):
		self.filecursor[0] = x
	def setFilecursorY(self, y):
		self.filecursor[1] = y

	def toggleSelect(self):
		if self.selectOn == False:
			self.selectOn = True
			self.selectPosition = [self.getFilecursorX(), self.getFilecursorY()]
		else:
			self.selectOn = False
			self.selectPosition = []

	def copySelect(self, toggle=True):
		if self.selectOn == True:
			self.copyLines = []
			# copy. so i need to store (RAM, variable :/ ) text between filecursor and select
			# store as list or string? well. selection<--filecursor<--fileLines<--list of strings. so list it is.
			# how to copy? work out start and end maybe mimic drawSelect logic. line by line or all at once?
			# tbh line by line likely better. easier to break down code to parse states of start line, middle lines, and end line.
			if self.getFilecursorY() > self.getSelectY():	  # if cursor below selectStart. 
				startX = self.getSelectX()
				startY = self.getSelectY()				
				endX = self.getFilecursorX()
				endY = self.getFilecursorY()
			elif self.getFilecursorY() < self.getSelectY(): # if selectStart below cursor.
				startX = self.getFilecursorX()
				startY = self.getFilecursorY()
				endX = self.getSelectX()
				endY = self.getSelectY()
			elif self.getFilecursorY() == self.getSelectY(): # if they're the same row.
				if self.getFilecursorX() == self.getSelectX(): # if x index same on each
					startX = self.getSelectX()
					startY = self.getSelectY()
					endX = startX
					endY = startY
				elif self.getFilecursorX() < self.getSelectX(): # if cursor index before selection index. 
					startX = self.getFilecursorX()
					startY = self.getFilecursorY()
					endX = self.getSelectX()
					endY = self.getSelectY()
				elif self.getFilecursorX() > self.getSelectX(): # if cursor index after selection index. 
					startX = self.getSelectX()
					startY = self.getSelectY()
					endX = self.getFilecursorX()
					endY = self.getFilecursorY()
			index = 0
			yOffset = len(self.fileLines[:startY])
			# for each line of file, from startY to endY
			for line in self.fileLines[startY:endY + 1]: # +1 to grab line select ends on and not stop one before it
				if startY == endY: # if start and end on same line (means only one line to process.)
					self.copyLines = [self.fileLines[index + yOffset][startX:endX]]
					#self.toggleSelect()
					break
				elif startY == index + yOffset: # elif line is line that select starts on
					self.copyLines.append(self.fileLines[index + yOffset][startX:])
				elif endY == index + yOffset: # elif line is line that select ends on
					self.copyLines.append(self.fileLines[index + yOffset][:endX])
				else: # elif line is between start and end
					self.copyLines.append(self.fileLines[index + yOffset])

				index += 1
			if toggle:
				self.toggleSelect()

	def cutSelect(self):
		if self.selectOn == True:
			self.copySelect(False) # select text copied; toggle arg set to false so select attributes still populated
			if self.getFilecursorY() > self.getSelectY():	  # if cursor below selectStart. 
				startX = self.getSelectX()
				startY = self.getSelectY()
				endX = self.getFilecursorX()
				endY = self.getFilecursorY()
			elif self.getFilecursorY() < self.getSelectY(): # if selectStart below cursor.
				startX = self.getFilecursorX()
				startY = self.getFilecursorY()
				endX = self.getSelectX()
				endY = self.getSelectY()
			elif self.getFilecursorY() == self.getSelectY(): # if they're the same row.
				if self.getFilecursorX() == self.getSelectX(): # if x index same on each
					startX = self.getSelectX()
					startY = self.getSelectY()
					endX = startX
					endY = startY
				elif self.getFilecursorX() < self.getSelectX(): # if cursor index before selection index. 
					startX = self.getFilecursorX()
					startY = self.getFilecursorY()
					endX = self.getSelectX()
					endY = self.getSelectY()
				elif self.getFilecursorX() > self.getSelectX(): # if cursor index after selection index. 
					startX = self.getSelectX()
					startY = self.getSelectY()
					endX = self.getFilecursorX()
					endY = self.getFilecursorY()
			last = len(self.copyLines) - 1 # index of last line in copy lines.
			i = 0
			for line in self.copyLines: # now to delete lines and correct filecursor position
				if i == 0 and i == last: # if BOTH first and last cut line (copyLines length 1, startY & endY are ==), same line cut
					if startY != endY or len(self.copyLines) != 1:
						exit("Debug! Assumption Wrong!" + str(startY != endY) + str(len(self.copyLines) != 1))
					lineStringLeft = self.fileLines[startY][:startX]
					lineStringRight = self.fileLines[endY][endX:]
					self.fileLines[startY] = lineStringLeft + lineStringRight
					if self.getFilecursorX() != startX or self.getFilecursorY() != startY: # filecursor after select start, select dragged left->right
						# move filecursor back to select start
						self.setFilecursorX(startX)
						self.setFilecursorY(startY)
						self.moveViewportToCursor()
				elif i == 0: # if first cut line, retain text from beginning to start[]
					lineStringLeft = self.fileLines[startY][:startX]
					self.fileLines[startY] = lineStringLeft
				elif i == last: # if last cut line, retain text from end[] to end of string
					lineStringRight = self.fileLines[startY + 1][endX:] # +1 since reading line ahead of start at this point
					self.fileLines.pop(startY + 1) # delete line one ahead of start
					self.fileLines[startY] += lineStringRight
					if self.getFilecursorX() != startX or self.getFilecursorY() != startY:
						self.setFilecursorX(startX)
						self.setFilecursorY(startY)
						self.moveViewportToCursor()
				else:
					self.fileLines.pop(startY + 1) # delete line one ahead of start
				i += 1
			self.modified = True

			self.toggleSelect()

	def pasteAtFilecursor(self):
		if self.copyLines != []:
			last = len(self.copyLines) - 1 # index of last line in copy lines. this is to not add an unessecary newline at the end
			i = 0
			for line in self.copyLines:
				lineStringLeft = self.fileLines[self.getFilecursorY()][:self.getFilecursorX()]
				lineStringRight = self.fileLines[self.getFilecursorY()][self.getFilecursorX():]
				lineStringLeft += line
				self.fileLines[self.getFilecursorY()] = lineStringLeft + lineStringRight
				self.modified = True
				for ch in line:
					self.moveFilecursorRight()
				if i != last: #   ^ to not add unneeded newline
					self.newLineAtFilecursor(autoIndentOverride=False)
				i += 1
			
	def moveViewportDown(self):
		self.setViewportY(self.getViewportY() + 1)
	def moveViewportUp(self):
		if self.getViewportY() > 0:
			self.setViewportY(self.getViewportY() - 1)
	def moveViewportRight(self):
		self.setViewportX(self.getViewportX() + 1)
	def moveViewportLeft(self):
		if self.getViewportX() > 0:
			self.setViewportX(self.getViewportX() - 1)
	def moveFilecursorUp(self):
		if self.getFilecursorY() > 0:
			self.setFilecursorY(self.getFilecursorY() - 1)
			if self.getFilecursorX() > len(self.fileLines[self.getFilecursorY()]):
				if len(self.fileLines[self.getFilecursorY()]) > 0:
					self.setFilecursorX(len(self.fileLines[self.getFilecursorY()]))
				elif len(self.fileLines[self.getFilecursorY()]) == 0:
					self.setFilecursorX(0)
			self.moveViewportToCursor()
	def moveFilecursorDown(self):
		if self.getFilecursorY() < len(self.fileLines)-1:
			self.setFilecursorY(self.getFilecursorY() + 1)
			if self.getFilecursorX() > len(self.fileLines[self.getFilecursorY()]):
				if len(self.fileLines[self.getFilecursorY()]) > 0:
					self.setFilecursorX(len(self.fileLines[self.getFilecursorY()]))
				elif len(self.fileLines[self.getFilecursorY()]) == 0:
					self.setFilecursorX(0)
			self.moveViewportToCursor()
	def moveFilecursorLeft(self, dist=1):
		self.moveFilecursorRight(-dist)
	def moveFilecursorRight(self, dist=1):
		self.setFilecursorX(self.getFilecursorX() + dist)
		if self.getFilecursorX() < 0:
			self.setFilecursorX(0)
			self.moveFilecursorUp()
			self.gotoEndOfLine()
		if self.getFilecursorX() > len(self.fileLines[self.getFilecursorY()]):
			if self.getFilecursorY() != len(self.fileLines) - 1: # if filecursor not at last line
				self.moveFilecursorDown()
				self.gotoStartOfLine()
			else: # filecursor on last line
				self.gotoEndOfLine()
		self.moveViewportToCursor()
	def moveViewportToCursorX(self):
		tabDiff = len(self.fileLines[self.getFilecursorY()][:self.getFilecursorX()].expandtabs(self.config["TabExpandSize"])) - len(self.fileLines[self.getFilecursorY()][:self.getFilecursorX()])
		cursorX = self.getFilecursorX() + tabDiff
		viewportWidth = self.getWindowMaxX() - 2
		if self.getViewportX() > cursorX:
			self.setViewportX(cursorX)
		elif self.getViewportX() < cursorX - viewportWidth:
			self.setViewportX(cursorX - viewportWidth)
	def moveViewportToCursorY(self):
		cursorY = self.getFilecursorY()
		viewportHeight = self.getWindowMaxY() - 1
		if self.getViewportY() > cursorY:
			self.setViewportY(cursorY)
		elif self.getViewportY() < cursorY - viewportHeight:
			self.setViewportY(cursorY - viewportHeight)
	def moveViewportToCursor(self):
		self.moveViewportToCursorX()
		self.moveViewportToCursorY()
	def gotoLine(self, lineNum, preserveX = False):
		if lineNum < len(self.fileLines) and lineNum > -1:
			self.setFilecursorY(lineNum)
			if (preserveX):
				if self.getFilecursorX() > len(self.fileLines[self.getFilecursorY()]):
					if len(self.fileLines[self.getFilecursorY()]) > 0:
						self.setFilecursorX(len(self.fileLines[self.getFilecursorY()]))
					elif len(self.fileLines[self.getFilecursorY()]) == 0:
						self.setFilecursorX(0)
			else:
				self.setFilecursorX(0)
			self.moveViewportToCursor()
	def gotoStartOfFile(self):
		self.gotoLine(0)
	def gotoEndOfFile(self):
		self.gotoLine(len(self.fileLines) - 1)
	def gotoStartOfLine(self):
		self.setFilecursorX(0)
		self.moveViewportToCursorX()
	def gotoEndOfLine(self):
		self.setFilecursorX(len(self.fileLines[self.getFilecursorY()]))
		self.moveViewportToCursorX()
	def enterTextAtFilecursor(self, text):
		if text == "\t" and self.config["TabLength"] != "char":
			text = " " * self.config["TabLength"]
		lineStringLeft = self.fileLines[self.getFilecursorY()][:self.getFilecursorX()]
		lineStringRight = self.fileLines[self.getFilecursorY()][self.getFilecursorX():]
		lineStringLeft += text
		self.fileLines[self.getFilecursorY()] = lineStringLeft + lineStringRight
		self.moveFilecursorRight(len(text))
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
		elif text == "'" and self.quoteOnce == True:
			self.quoteOnce = False
			self.enterTextAtFilecursor("'")
			self.moveFilecursorLeft()
			self.quoteOnce = True
	def newLineAtFilecursor(self, autoIndentOverride=True):
		lineStringLeft = self.fileLines[self.getFilecursorY()][:self.getFilecursorX()]
		lineStringRight = self.fileLines[self.getFilecursorY()][self.getFilecursorX():]
		indentSize = 0
		if self.config["AutoIndent"] and autoIndentOverride:
			indentSize = len(lineStringLeft) - len(lineStringLeft.lstrip())
			lineStringRight = lineStringLeft[:indentSize] + lineStringRight
		self.fileLines[self.getFilecursorY()] = lineStringLeft
		self.fileLines.insert(self.getFilecursorY() + 1, "")
		self.moveFilecursorDown()
		self.fileLines[self.getFilecursorY()] = lineStringRight
		self.moveFilecursorRight(indentSize)
		self.modified = True
	def backspaceTextAtFilecursor(self):
		if self.getFilecursorX() == 0:
			if self.getFilecursorY() > 0:
				lineString = self.fileLines[self.getFilecursorY()]
				self.fileLines.pop(self.getFilecursorY())
				self.moveFilecursorUp()
				self.gotoEndOfLine()
				self.fileLines[self.getFilecursorY()] += lineString
		else:
			lineStringLeft = self.fileLines[self.getFilecursorY()][:self.getFilecursorX() - 1]
			lineStringRight = self.fileLines[self.getFilecursorY()][self.getFilecursorX():]
			self.fileLines[self.getFilecursorY()] = lineStringLeft + lineStringRight
			self.moveFilecursorLeft()
		self.modified = True
	def saveFile(self):
		fileString = ""
		linesRow = 0
		for line in self.fileLines:
			fileString += line + "\n"
		returnval = self.manager.Windows["magicBar"].save()
		self.file.save(fileString)
		return returnval
	def searchForText(self):
		pass
	def scrollDown(self):
		scrollAmount = 20
		self.gotoLine(min(self.getFilecursorY() + scrollAmount, len(self.fileLines) - 1))
	def scrollUp(self):
		scrollAmount = 20
		self.gotoLine(max(self.getFilecursorY() - scrollAmount, 0))
	def deleteLineAtFilecursor(self):
		if self.getFilecursorY() != len(self.fileLines) - 1:
			self.fileLines.pop(self.getFilecursorY())
			if len(self.fileLines[self.getFilecursorY()]) >= self.getFilecursorX():
				pass
			else:
				self.setFilecursorX(len(self.fileLines[self.getFilecursorY()]))
		else:
			self.fileLines.pop(self.getFilecursorY())
			if len(self.fileLines) - 1 >= 0:
				self.moveFilecursorUp()
			else:
				self.setFilecursorX(0)
		self.modified = True
	def deleteTextAtFilecursor(self):
		if self.getFilecursorX() + 1 <= len(self.fileLines[self.getFilecursorY()]): # if there is text to the right of our self.filecursor
			lineStringLeft = self.fileLines[self.getFilecursorY()][:self.getFilecursorX()]
			lineStringRight = self.fileLines[self.getFilecursorY()][self.getFilecursorX() + 1:]
			self.fileLines[self.getFilecursorY()] = lineStringLeft+lineStringRight
		elif self.getFilecursorY() != len(self.fileLines) - 1: # else (no text to right of self.filecursor) if there is line below
			nextLine = self.fileLines[self.getFilecursorY() + 1] # append line below to current line
			self.fileLines.pop(self.getFilecursorY() + 1)
			self.fileLines[self.getFilecursorY()] += nextLine
		self.modified = True
