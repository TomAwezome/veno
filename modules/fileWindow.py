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

		self.modified = True ## i.e. Modified since last highlight. Variable used for speed optimization of syntax highlighting algorithm.
		self.selectPosition = []
		self.selectOn = False
		self.isRepeatingQuote = False
		self.copyLines = []

	def update(self):
		self.window.erase()
		self.intendedHeight = self.getStdscrMaxY() - self.intendedY - 1
		self.intendedWidth = self.getStdscrMaxX() - self.intendedX - 1

		self.keepWindowInMainScreen()

		windowY = 0
		tabExpandSize = self.config["TabExpandSize"]
		viewportY = self.getViewportY()
		windowMaxY = self.getWindowMaxY()
		viewportX = self.getViewportX()
		windowMaxX = self.getWindowMaxX()

		for line in self.fileLines[viewportY:viewportY + windowMaxY]:
			line = line.expandtabs(tabExpandSize)[viewportX:]

			self.window.addnstr(windowY, 0, line, windowMaxX - 1, self.manager.curses.color_pair(0))
			windowY += 1

		self.drawCursor()

	def drawCursor(self):
		tabExpandSize = self.config["TabExpandSize"]
		filecursorY = self.getFilecursorY()
		filecursorX = self.getFilecursorX()
		viewportY = self.getViewportY()
		viewportX = self.getViewportX()
		windowMaxY = self.getWindowMaxY()
		windowMaxX = self.getWindowMaxX()

		if filecursorY >= viewportY and filecursorY <= viewportY + windowMaxY - 1:
			if len(self.fileLines) == 0:
				self.fileLines.append("")

			line = self.fileLines[filecursorY][:filecursorX]
			expandedLine = line.expandtabs(tabExpandSize)
			tabDiff = len(expandedLine) - len(line)
			cursorX = filecursorX - viewportX + tabDiff
			cursorY = filecursorY - viewportY

			if cursorX <= windowMaxX - 2 and cursorX >= 0:
				self.window.chgat(cursorY, cursorX, 1, self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

# FUNCTIONS TO BE CALLED EXTERNALLY

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

	def setSelectX(self, x):
		if self.selectPosition != []:
			self.selectPosition[0] = x

	def setSelectY(self, y):
		if self.selectPosition != []:
			self.selectPosition[1] = y

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
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()
		selectX = self.getSelectX()
		selectY = self.getSelectY()

		if self.selectOn == True:
			self.copyLines = []
			# copy. so i need to store (RAM, variable :/ ) text between filecursor and select
			# store as list or string? well. selection<--filecursor<--fileLines<--list of strings. so list it is.
			# how to copy? work out start and end maybe mimic drawSelect logic. line by line or all at once?
			# tbh line by line likely better. easier to break down code to parse states of start line, middle lines, and end line.
			startY = min(filecursorY, selectY)
			endY = max(filecursorY, selectY)
			if startY == endY:
				startX = min(filecursorX, selectX)
				endX = max(filecursorX, selectX)
			elif startY == filecursorY:
				startX = filecursorX
				endX = selectX
			elif startY == selectY:
				startX = selectX
				endX = filecursorX

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
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()
		selectX = self.getSelectX()
		selectY = self.getSelectY()

		if self.selectOn == True:
			self.copySelect(False) # select text copied; toggle arg set to false so select attributes still populated

			startY = min(filecursorY, selectY)
			endY = max(filecursorY, selectY)
			if startY == endY:
				startX = min(filecursorX, selectX)
				endX = max(filecursorX, selectX)
			elif startY == filecursorY:
				startX = filecursorX
				endX = selectX
			elif startY == selectY:
				startX = selectX
				endX = filecursorX

			last = len(self.copyLines) - 1 # index of last line in copy lines.
			i = 0
			for line in self.copyLines: # now to delete lines and correct filecursor position
				filecursorX = self.getFilecursorX()
				filecursorY = self.getFilecursorY()

				if i == 0 and i == last: # if BOTH first and last cut line (copyLines length 1, startY & endY are ==), same line cut
					if startY != endY or len(self.copyLines) != 1:
						exit("Debug! Assumption Wrong!" + str(startY != endY) + str(len(self.copyLines) != 1))
					lineStringLeft = self.fileLines[startY][:startX]
					lineStringRight = self.fileLines[endY][endX:]

					self.fileLines[startY] = lineStringLeft + lineStringRight
					if filecursorX != startX or filecursorY != startY: # filecursor after select start, select dragged left->right
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
					if filecursorX != startX or filecursorY != startY:
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
				filecursorY = self.getFilecursorY()
				filecursorX = self.getFilecursorX()
				lineStringLeft = self.fileLines[filecursorY][:filecursorX]
				lineStringRight = self.fileLines[filecursorY][filecursorX:]
				lineStringLeft += line

				self.fileLines[filecursorY] = lineStringLeft + lineStringRight
				self.modified = True
				for ch in line:
					self.moveFilecursorRight()

				if i != last: #   ^ to not add unneeded newline
					self.newLineAtFilecursor(autoIndentOverride=False)

				i += 1
			
	def moveViewportDown(self):
		self.setViewportY(self.getViewportY() + 1)

	def moveViewportUp(self):
		viewportY = self.getViewportY()

		if viewportY > 0:
			self.setViewportY(viewportY - 1)

	def moveViewportRight(self):
		self.setViewportX(self.getViewportX() + 1)

	def moveViewportLeft(self):
		viewportX = self.getViewportX()

		if viewportX > 0:
			self.setViewportX(viewportX - 1)

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
		filecursorY = self.getFilecursorY()
		filecursorX = self.getFilecursorX()

		if filecursorX < 0:
			if filecursorY != 0: # if filecursor not at first line
				self.setFilecursorX(0)
				self.moveFilecursorUp()
				self.gotoEndOfLine()
			else: # filcursor on first line
				self.gotoStartOfLine()

		if filecursorX > len(self.fileLines[filecursorY]):
			if filecursorY != len(self.fileLines) - 1: # if filecursor not at last line
				self.moveFilecursorDown()
				self.gotoStartOfLine()

			else: # filecursor on last line
				self.gotoEndOfLine()

		self.moveViewportToCursor()

	def moveViewportToCursorX(self):
		tabExpandSize = self.config["TabExpandSize"]
		filecursorY = self.getFilecursorY()
		filecursorX = self.getFilecursorX()
		viewportX = self.getViewportX()
		tabDiff = len(self.fileLines[filecursorY][:filecursorX].expandtabs(tabExpandSize)) - len(self.fileLines[filecursorY][:filecursorX])
		tabcursorX = filecursorX + tabDiff
		viewportWidth = self.getWindowMaxX() - 2

		if viewportX > tabcursorX:
			self.setViewportX(tabcursorX)

		elif viewportX < tabcursorX - viewportWidth:
			self.setViewportX(tabcursorX - viewportWidth)

	def moveViewportToCursorY(self):
		filecursorY = self.getFilecursorY()
		viewportHeight = self.getWindowMaxY() - 1
		viewportY = self.getViewportY()

		if viewportY > filecursorY:
			self.setViewportY(filecursorY)

		elif viewportY < filecursorY - viewportHeight:
			self.setViewportY(filecursorY - viewportHeight)

	def moveViewportToCursor(self):
		self.moveViewportToCursorX()
		self.moveViewportToCursorY()

	def gotoLine(self, lineNum, preserveX = False):
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()

		if lineNum >= len(self.fileLines): # if linenumber is greater than last line,
			lineNum = len(self.fileLines) - 1 # goto last line

		if lineNum > -1:
			self.setFilecursorY(lineNum)
			if (preserveX):
				if filecursorX > len(self.fileLines[filecursorY]):
					if len(self.fileLines[filecursorY]) > 0:
						self.setFilecursorX(len(self.fileLines[filecursorY]))
					elif len(self.fileLines[filecursorY]) == 0:
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

	def unindentSelectedLines(self):
		filecursorY = self.getFilecursorY()
		filecursorX = self.getFilecursorX()

		indentText = "\t"
		if self.config["TabLength"] != "char":
			indentText = str(self.config["TabLength"])

		if self.selectOn:
			selectY = self.getSelectY()
			selectX = self.getSelectX()
			
			startY = min(filecursorY, selectY)
			endY = max(filecursorY, selectY)
			if startY == endY:
				startX = min(filecursorX, selectX)
				endX = max(filecursorX, selectX)

				line = self.fileLines[filecursorY]
				if line.find(indentText) == 0: # if we find indentText at line start, remove it, skips removal if not found or at wrong spot in line
					self.fileLines[filecursorY] = line.replace(indentText, "", 1) # 1 to only replace first occurence of indentText
					self.modified = True
					
					self.setSelectX(selectX - len(indentText))
					if filecursorX >= len(indentText): # if won't be pushed off line during moving, shift it back
						self.moveFilecursorLeft(len(indentText))

				return

			if startY == filecursorY:
				startX = filecursorX
				endX = selectX
			elif startY == selectY:
				startX = selectX
				endX = filecursorX

			for lineIndex in range(startY, endY + 1): # + 1 to end range on endY
				line = self.fileLines[lineIndex]
				
				if line.find(indentText) == 0: # if we find indentText at line start, remove it, skips removal if not found or at wrong spot in line
					if lineIndex == startY and startX == len(line): # don't indent start line if selection starts at end of line
						continue
					if lineIndex == endY and endX == 0: # don't indent end line if selection ends at beginning of a line
						continue
					self.fileLines[lineIndex] = line.replace(indentText, "", 1) # 1 to only replace first occurence of indentText
					
					# if current line is selection start, move either cursor or select
					if lineIndex == startY:
						if self.fileLines[lineIndex][startX - len(indentText):startX] == indentText: # if select still at indentText after replace, keep it there
							continue # since line was unindented and startX unchanged, subtracted indentText length to peek 

						if startY == filecursorY and startX == filecursorX: # if start is filecursor
							if filecursorX >= len(indentText): # if cursor won't be pushed off line during moving, shift it back
								self.moveFilecursorLeft(len(indentText))

						if startY == selectY and startX == selectX: # if start is selectPosition
							if selectX >= len(indentText): # if selectPosition won't be pushed off line, shift back
								self.setSelectX(selectX - len(indentText))

					# if current line is selection end, move either cursor or select
					elif lineIndex == endY:
						if self.fileLines[lineIndex][endX - len(indentText):endX] == indentText: # if select still at indentText after replace, keep it there
							continue # since line was unindented and endX unchanged, subtracted indentText length to peek 

						if endY == filecursorY and endX == filecursorX: # if end is filecursor
							if filecursorX >= len(indentText): # if cursor won't be pushed off line during moving, shift it back
								self.moveFilecursorLeft(len(indentText))

						if endY == selectY and endX == selectX: # if end is selectPosition
							if selectX >= len(indentText): # if selectPosition won't be pushed off line, shift back
								self.setSelectX(selectX - len(indentText))
		else:
			line = self.fileLines[filecursorY]
			if line.find(indentText) == 0: # if we find indentText at line start, remove it, skips removal if not found or at wrong spot in line
				self.fileLines[filecursorY] = line.replace(indentText, "", 1) # 1 to only replace first occurence of indentText
				if filecursorX >= len(indentText): # if won't be pushed off line during moving, shift it back
					self.moveFilecursorLeft(len(indentText))
		
		self.modified = True


	def indentSelectedLines(self, text):
		filecursorY = self.getFilecursorY()
		filecursorX = self.getFilecursorX()
		selectY = self.getSelectY()
		selectX = self.getSelectX()

		startY = min(filecursorY, selectY)
		endY = max(filecursorY, selectY)

		if startY == endY: # if selection is on one line
			startX = min(filecursorX, selectX)
			endX = max(filecursorX, selectX)

			lineStringLeft = self.fileLines[startY][:startX]
			lineStringRight = self.fileLines[startY][startX:]
			lineStringLeft += text

			self.fileLines[startY] = lineStringLeft + lineStringRight
			self.modified = True

			self.moveFilecursorRight(len(text))
			if startX == selectX: # if stored select value is start, set select to start + text length
				self.setSelectX(startX + len(text))
			elif startX == filecursorX: # if filecursor marks start, set select to end + text length
				self.setSelectX(endX + len(text))

			return

		# selection is on different lines 
		elif startY == filecursorY: # filecursor marks start
			startX = filecursorX
			endX = selectX
		elif startY == selectY: # selectPosition marks start
			startX = selectX
			endX = filecursorX

		for lineIndex in range(startY, endY + 1): # + 1 to end range on endY
			line = self.fileLines[lineIndex]
			if line == "": # don't tab empty lines 
				continue

			elif lineIndex == startY: # if current line is selection start
				if startX == len(line): # if startX is at the end of the line, don't indent it
					continue
				elif startX == filecursorX and startY == filecursorY: # if filecursor is start, indent line and move filecursor right, continue to next line
					line = text + line
					self.fileLines[lineIndex] = line
					if startX != 0: # don't move cursor if it's at the beginning of a line
						self.moveFilecursorRight(len(text))
					continue
				elif startX == selectX and startY == selectY: # if select position is end, shift it by text length
					if startX != 0: # don't move select if it's at beginning of a line
						self.setSelectX(startX + len(text))

			elif lineIndex == endY: # if current line is end
				if endX == 0: # if endX is at start of the line, don't indent 
					continue
				elif endX == filecursorX and endY == filecursorY: # if filecursor is end, indent line and move filecursor right, continue to next line
					line = text + line
					self.fileLines[lineIndex] = line
					self.moveFilecursorRight(len(text))
					continue
				elif endX == selectX and endY == selectY: # if select position is end, shift it by text length
					self.setSelectX(endX + len(text))
			
			line = text + line
			self.fileLines[lineIndex] = line

		self.modified = True

	def enterTextAtFilecursor(self, text):
		if text == "\t":
			if self.config["TabLength"] != "char":
				text = " " * self.config["TabLength"]
			if self.selectOn:
				self.indentSelectedLines(text)
				return

		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()
		lineStringLeft = self.fileLines[filecursorY][:filecursorX]
		lineStringRight = self.fileLines[filecursorY][filecursorX:]
		lineStringLeft += text

		self.fileLines[filecursorY] = lineStringLeft + lineStringRight
		self.moveFilecursorRight(len(text))
		self.modified = True
		
		if self.config["BracketMatching"]:
			braceMatches = {
					"[": "]",
					"(": ")",
					"{": "}",
					}
			if text in braceMatches:
				self.enterTextAtFilecursor(braceMatches[text])
				self.moveFilecursorLeft()

		if self.config["QuoteMatching"]:
			if text in ["\"", "'"] and not self.isRepeatingQuote:
				self.isRepeatingQuote = True
				self.enterTextAtFilecursor(text)
				self.moveFilecursorLeft()
				self.isRepeatingQuote = False

	def newLineAtFilecursor(self, autoIndentOverride=True):
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()
		lineStringLeft = self.fileLines[filecursorY][:filecursorX]
		lineStringRight = self.fileLines[filecursorY][filecursorX:]
		indentSize = 0
		if self.config["AutoIndent"] and autoIndentOverride:
			indentSize = len(lineStringLeft) - len(lineStringLeft.lstrip())
			lineStringRight = lineStringLeft[:indentSize] + lineStringRight

		self.fileLines[filecursorY] = lineStringLeft
		self.fileLines.insert(filecursorY + 1, "")
		self.moveFilecursorDown()
		self.fileLines[self.getFilecursorY()] = lineStringRight
		self.moveFilecursorRight(indentSize)
		self.modified = True

	def backspaceTextAtFilecursor(self):
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()

		if filecursorX == 0:
			if filecursorY > 0:
				lineString = self.fileLines[filecursorY]
				self.fileLines.pop(filecursorY)
				self.moveFilecursorUp()
				self.gotoEndOfLine()
				self.fileLines[self.getFilecursorY()] += lineString
		else:
			lineStringLeft = self.fileLines[filecursorY][:filecursorX - 1]
			lineStringRight = self.fileLines[filecursorY][filecursorX:]
			self.fileLines[filecursorY] = lineStringLeft + lineStringRight
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
		filecursorY = self.getFilecursorY()
		self.gotoLine(min(filecursorY + scrollAmount, len(self.fileLines) - 1))

	def scrollUp(self):
		scrollAmount = 20
		filecursorY = self.getFilecursorY()
		self.gotoLine(max(filecursorY - scrollAmount, 0))

	def deleteLineAtFilecursor(self):
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()

		if filecursorY != len(self.fileLines) - 1:
			self.fileLines.pop(filecursorY)
			if len(self.fileLines[filecursorY]) >= filecursorX:
				pass
			else:
				self.setFilecursorX(len(self.fileLines[filecursorY]))

		else:
			self.fileLines.pop(filecursorY)
			if len(self.fileLines) - 1 >= 0:
				self.moveFilecursorUp()
			else:
				self.setFilecursorX(0)

		self.modified = True

	def deleteTextAtFilecursor(self):
		filecursorX = self.getFilecursorX()
		filecursorY = self.getFilecursorY()

		if filecursorX + 1 <= len(self.fileLines[filecursorY]): # if there is text to the right of our self.filecursor
			lineStringLeft = self.fileLines[filecursorY][:filecursorX]
			lineStringRight = self.fileLines[filecursorY][filecursorX + 1:]
			self.fileLines[filecursorY] = lineStringLeft + lineStringRight

		elif filecursorY != len(self.fileLines) - 1: # else (no text to right of self.filecursor) if there is line below
			nextLine = self.fileLines[filecursorY + 1] # append line below to current line
			self.fileLines.pop(filecursorY + 1)
			self.fileLines[filecursorY] += nextLine

		self.modified = True
