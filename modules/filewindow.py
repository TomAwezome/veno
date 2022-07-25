from modules.window import Window
class FileWindow(Window):
	def __init__(self, engine, file):
		Window.__init__(self, engine)
		self.viewport	= [0, 0] # [X, Y]
		self.filecursor = [0, 0] # [X, Y]
		self.file		= file
		self.file_lines	= self.file.contents.splitlines()
		self.config		= self.engine.get("config").options

		self.is_modified		= True ## i.e. Modified since last highlight. Variable used for speed optimization of syntax highlighting algorithm.
		self.select_position	= []
		self.is_select_on = self.is_repeating_quote = False
		self.copy_lines			= []
		
		self.panel.bottom()

	def update(self):
		self.window.erase()
		self.intended_height = self.getScreenMaxY() - self.intended_y - 1
		self.intended_width  = self.getScreenMaxX() - self.intended_x - 1

		self.keepWindowInMainScreen()

		window_y = 0
		tab_expand_size = self.config["TabExpandSize"]
		viewport_y = self.getViewportY()
		viewport_x = self.getViewportX()
		window_max_y = self.getWindowMaxY()
		window_max_x = self.getWindowMaxX()

		for line in self.file_lines[viewport_y:viewport_y + window_max_y]:
			line = line.expandtabs(tab_expand_size)[viewport_x:]

			self.window.addnstr(window_y, 0, line, window_max_x - 1, self.engine.curses.color_pair(0))
			window_y += 1

		self.drawCursor()

	def drawCursor(self):
		tab_expand_size = self.config["TabExpandSize"]
		filecursor_y = self.getFilecursorY()
		filecursor_x = self.getFilecursorX()
		viewport_y = self.getViewportY()
		viewport_x = self.getViewportX()
		window_max_y = self.getWindowMaxY()
		window_max_x = self.getWindowMaxX()

		if filecursor_y >= viewport_y and filecursor_y <= viewport_y + window_max_y - 1:
			if len(self.file_lines) == 0:
				self.file_lines.append("")

			line = self.file_lines[filecursor_y][:filecursor_x]
			expanded_line = line.expandtabs(tab_expand_size)
			tab_diff = len(expanded_line) - len(line)
			cursorX = filecursor_x - viewport_x + tab_diff
			cursorY = filecursor_y - viewport_y

			if cursorX <= window_max_x - 2 and cursorX >= 0:
				self.window.chgat(cursorY, cursorX, 1, self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)

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
		if self.select_position != []:
			return self.select_position[0]

	def getSelectY(self):
		if self.select_position != []:
			return self.select_position[1]

	def setSelectX(self, x):
		if self.select_position != []:
			self.select_position[0] = x

	def setSelectY(self, y):
		if self.select_position != []:
			self.select_position[1] = y

	def setViewportX(self, x):
		self.viewport[0] = x

	def setViewportY(self, y):
		self.viewport[1] = y

	def setFilecursorX(self, x):
		self.filecursor[0] = x

	def setFilecursorY(self, y):
		self.filecursor[1] = y

	def toggleSelect(self):
		if not self.is_select_on:
			self.is_select_on = True
			self.select_position = [self.getFilecursorX(), self.getFilecursorY()]
		else:
			self.is_select_on = False
			self.select_position = []

	def selectAll(self):
		self.is_select_on = True
		self.select_position = [0, 0]
		self.gotoEndOfFile()
		self.gotoEndOfLine()		

	def copySelect(self, toggle=True):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()
		select_x = self.getSelectX()
		select_y = self.getSelectY()

		if self.is_select_on:
			self.copy_lines = []
			start_y = min(filecursor_y, select_y)
			end_y = max(filecursor_y, select_y)
			if start_y == end_y:
				start_x = min(filecursor_x, select_x)
				end_x = max(filecursor_x, select_x)
			elif start_y == filecursor_y:
				start_x = filecursor_x
				end_x = select_x
			elif start_y == select_y:
				start_x = select_x
				end_x = filecursor_x

			index = 0
			y_offset = len(self.file_lines[:start_y])
			# for each line of file, from start_y to end_y
			for line in self.file_lines[start_y:end_y + 1]: # +1 to grab line select ends on and not stop one before it
				if start_y == end_y: # if start and end on same line (means only one line to process.)
					self.copy_lines = [self.file_lines[index + y_offset][start_x:end_x]]
					#self.toggleSelect()
					break

				elif start_y == index + y_offset: # elif line is line that select starts on
					self.copy_lines.append(self.file_lines[index + y_offset][start_x:])

				elif end_y == index + y_offset: # elif line is line that select ends on
					self.copy_lines.append(self.file_lines[index + y_offset][:end_x])

				else: # elif line is between start and end
					self.copy_lines.append(self.file_lines[index + y_offset])

				index += 1

			if toggle:
				self.toggleSelect()

	def cutSelect(self):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()
		select_x = self.getSelectX()
		select_y = self.getSelectY()

		if self.is_select_on == True:
			self.copySelect(False) # select text copied; toggle arg set to false so select attributes still populated

			start_y = min(filecursor_y, select_y)
			end_y = max(filecursor_y, select_y)
			if start_y == end_y:
				start_x = min(filecursor_x, select_x)
				end_x = max(filecursor_x, select_x)
			elif start_y == filecursor_y:
				start_x = filecursor_x
				end_x = select_x
			elif start_y == select_y:
				start_x = select_x
				end_x = filecursor_x

			last = len(self.copy_lines) - 1 # index of last line in copy lines.
			i = 0
			for line in self.copy_lines: # now to delete lines and correct filecursor position
				filecursor_x = self.getFilecursorX()
				filecursor_y = self.getFilecursorY()

				if i == 0 and i == last: # if BOTH first and last cut line (copyLines length 1, start_y & end_y are ==), same line cut
					if start_y != end_y or len(self.copy_lines) != 1:
						exit("Debug! Assumption Wrong!" + str(start_y != end_y) + str(len(self.copy_lines) != 1))
					line_string_left = self.file_lines[start_y][:start_x]
					line_string_right = self.file_lines[end_y][end_x:]

					self.file_lines[start_y] = line_string_left + line_string_right
					if filecursor_x != start_x or filecursor_y != start_y: # filecursor after select start, select dragged left->right
						# move filecursor back to select start
						self.setFilecursorX(start_x)
						self.setFilecursorY(start_y)
						self.moveViewportToCursor()

				elif i == 0: # if first cut line, retain text from beginning to start[]
					line_string_left = self.file_lines[start_y][:start_x]
					self.file_lines[start_y] = line_string_left

				elif i == last: # if last cut line, retain text from end[] to end of string
					line_string_right = self.file_lines[start_y + 1][end_x:] # +1 since reading line ahead of start at this point

					self.file_lines.pop(start_y + 1) # delete line one ahead of start
					self.file_lines[start_y] += line_string_right
					if filecursor_x != start_x or filecursor_y != start_y:
						self.setFilecursorX(start_x)
						self.setFilecursorY(start_y)
						self.moveViewportToCursor()

				else:
					self.file_lines.pop(start_y + 1) # delete line one ahead of start

				i += 1

			self.is_modified = True

			self.toggleSelect()

	def pasteAtFilecursor(self):
		if self.copy_lines != []:
			last = len(self.copy_lines) - 1 # index of last line in copy lines. this is to not add an unessecary newline at the end
			i = 0
			for line in self.copy_lines:
				filecursor_y = self.getFilecursorY()
				filecursor_x = self.getFilecursorX()
				line_string_left = self.file_lines[filecursor_y][:filecursor_x]
				line_string_right = self.file_lines[filecursor_y][filecursor_x:]
				line_string_left += line

				self.file_lines[filecursor_y] = line_string_left + line_string_right
				self.is_modified = True
				for ch in line:
					self.moveFilecursorRight()

				if i != last: #   ^ to not add unneeded newline
					self.newLineAtFilecursor(auto_indent_override=False)

				i += 1
			
	def moveViewportDown(self):
		self.setViewportY(self.getViewportY() + 1)

	def moveViewportUp(self):
		viewport_y = self.getViewportY()

		if viewport_y > 0:
			self.setViewportY(viewport_y - 1)

	def moveViewportRight(self):
		self.setViewportX(self.getViewportX() + 1)

	def moveViewportLeft(self):
		viewport_x = self.getViewportX()

		if viewport_x > 0:
			self.setViewportX(viewport_x - 1)

	def moveFilecursorUp(self):
		if self.getFilecursorY() > 0:
			self.setFilecursorY(self.getFilecursorY() - 1)
			if self.getFilecursorX() > len(self.file_lines[self.getFilecursorY()]):
				if len(self.file_lines[self.getFilecursorY()]) > 0:
					self.setFilecursorX(len(self.file_lines[self.getFilecursorY()]))
				elif len(self.file_lines[self.getFilecursorY()]) == 0:
					self.setFilecursorX(0)
			self.moveViewportToCursor()

	def moveFilecursorDown(self):
		if self.getFilecursorY() < len(self.file_lines)-1:
			self.setFilecursorY(self.getFilecursorY() + 1)
			if self.getFilecursorX() > len(self.file_lines[self.getFilecursorY()]):
				if len(self.file_lines[self.getFilecursorY()]) > 0:
					self.setFilecursorX(len(self.file_lines[self.getFilecursorY()]))
				elif len(self.file_lines[self.getFilecursorY()]) == 0:
					self.setFilecursorX(0)
			self.moveViewportToCursor()

	def moveFilecursorLeft(self, dist=1):
		self.moveFilecursorRight(-dist)

	def moveFilecursorRight(self, dist=1):
		self.setFilecursorX(self.getFilecursorX() + dist)
		filecursor_y = self.getFilecursorY()
		filecursor_x = self.getFilecursorX()

		if filecursor_x < 0:
			if filecursor_y != 0: # if filecursor not at first line
				self.setFilecursorX(0)
				self.moveFilecursorUp()
				self.gotoEndOfLine()
			else: # filcursor on first line
				self.gotoStartOfLine()

		if filecursor_x > len(self.file_lines[filecursor_y]):
			if filecursor_y != len(self.file_lines) - 1: # if filecursor not at last line
				self.moveFilecursorDown()
				self.gotoStartOfLine()

			else: # filecursor on last line
				self.gotoEndOfLine()

		self.moveViewportToCursor()

	def moveViewportToCursorX(self):
		tab_expand_size = self.config["TabExpandSize"]
		filecursor_y = self.getFilecursorY()
		filecursor_x = self.getFilecursorX()
		viewport_x = self.getViewportX()
		tab_diff = len(self.file_lines[filecursor_y][:filecursor_x].expandtabs(tab_expand_size)) - len(self.file_lines[filecursor_y][:filecursor_x])
		tabcursorX = filecursor_x + tab_diff
		viewportWidth = self.getWindowMaxX() - 2

		if viewport_x > tabcursorX:
			self.setViewportX(tabcursorX)

		elif viewport_x < tabcursorX - viewportWidth:
			self.setViewportX(tabcursorX - viewportWidth)

	def moveViewportToCursorY(self):
		filecursor_y = self.getFilecursorY()
		viewportHeight = self.getWindowMaxY() - 1
		viewport_y = self.getViewportY()

		if viewport_y > filecursor_y:
			self.setViewportY(filecursor_y)

		elif viewport_y < filecursor_y - viewportHeight:
			self.setViewportY(filecursor_y - viewportHeight)

	def moveViewportToCursor(self):
		self.moveViewportToCursorX()
		self.moveViewportToCursorY()

	def jumpToLine(self, line_num, preserve_x = False):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()

		if line_num >= len(self.file_lines): # if linenumber is greater than last line,
			line_num = len(self.file_lines) - 1 # goto last line

		if line_num > -1:
			self.setFilecursorY(line_num)
			if preserve_x:
				if filecursor_x > len(self.file_lines[filecursor_y]):
					if len(self.file_lines[filecursor_y]) > 0:
						self.setFilecursorX(len(self.file_lines[filecursor_y]))
					elif len(self.file_lines[filecursor_y]) == 0:
						self.setFilecursorX(0)
			else:
				self.setFilecursorX(0)

			self.moveViewportToCursor()

	def gotoStartOfFile(self):
		self.jumpToLine(0)

	def gotoEndOfFile(self):
		self.jumpToLine(len(self.file_lines) - 1)

	def gotoStartOfLine(self):
		self.setFilecursorX(0)
		self.moveViewportToCursorX()

	def gotoEndOfLine(self):
		self.setFilecursorX(len(self.file_lines[self.getFilecursorY()]))
		self.moveViewportToCursorX()

	def unindentSelectedLines(self):
		filecursor_y = self.getFilecursorY()
		filecursor_x = self.getFilecursorX()

		indent_text = "\t"
		if self.config["TabLength"] != "char":
			indent_text = str(self.config["TabLength"])

		if self.is_select_on:
			select_y = self.getSelectY()
			select_x = self.getSelectX()
			
			start_y = min(filecursor_y, select_y)
			end_y = max(filecursor_y, select_y)
			if start_y == end_y:
				start_x = min(filecursor_x, select_x)
				end_x = max(filecursor_x, select_x)

				line = self.file_lines[filecursor_y]
				if line.find(indent_text) == 0: # if we find indent_text at line start, remove it, skips removal if not found or at wrong spot in line
					self.file_lines[filecursor_y] = line.replace(indent_text, "", 1) # 1 to only replace first occurence of indent_text
					self.is_modified = True
					
					self.setSelectX(select_x - len(indent_text))
					if filecursor_x >= len(indent_text): # if won't be pushed off line during moving, shift it back
						self.moveFilecursorLeft(len(indent_text))

				return

			if start_y == filecursor_y:
				start_x = filecursor_x
				end_x = select_x
			elif start_y == select_y:
				start_x = select_x
				end_x = filecursor_x

			for line_index in range(start_y, end_y + 1): # + 1 to end range on end_y
				line = self.file_lines[line_index]
				
				if line.find(indent_text) == 0: # if we find indent_text at line start, remove it, skips removal if not found or at wrong spot in line
					if line_index == start_y and start_x == len(line): # don't indent start line if selection starts at end of line
						continue
					if line_index == end_y and end_x == 0: # don't indent end line if selection ends at beginning of a line
						continue
					self.file_lines[line_index] = line.replace(indent_text, "", 1) # 1 to only replace first occurence of indent_text
					
					# if current line is selection start, move either cursor or select
					if line_index == start_y:
						if self.file_lines[line_index][start_x - len(indent_text):start_x] == indent_text: # if select still at indent_text after replace, keep it there
							continue # since line was unindented and start_x unchanged, subtracted indent_text length to peek 

						if start_y == filecursor_y and start_x == filecursor_x: # if start is filecursor
							if filecursor_x >= len(indent_text): # if cursor won't be pushed off line during moving, shift it back
								self.moveFilecursorLeft(len(indent_text))

						if start_y == select_y and start_x == select_x: # if start is selectPosition
							if select_x >= len(indent_text): # if selectPosition won't be pushed off line, shift back
								self.setSelectX(select_x - len(indent_text))

					# if current line is selection end, move either cursor or select
					elif line_index == end_y:
						if self.file_lines[line_index][end_x - len(indent_text):end_x] == indent_text: # if select still at indent_text after replace, keep it there
							continue # since line was unindented and end_x unchanged, subtracted indent_text length to peek 

						if end_y == filecursor_y and end_x == filecursor_x: # if end is filecursor
							if filecursor_x >= len(indent_text): # if cursor won't be pushed off line during moving, shift it back
								self.moveFilecursorLeft(len(indent_text))

						if end_y == select_y and end_x == select_x: # if end is selectPosition
							if select_x >= len(indent_text): # if selectPosition won't be pushed off line, shift back
								self.setSelectX(select_x - len(indent_text))
		else:
			line = self.file_lines[filecursor_y]
			if line.find(indent_text) == 0: # if we find indent_text at line start, remove it, skips removal if not found or at wrong spot in line
				self.file_lines[filecursor_y] = line.replace(indent_text, "", 1) # 1 to only replace first occurence of indent_text
				if filecursor_x >= len(indent_text): # if won't be pushed off line during moving, shift it back
					self.moveFilecursorLeft(len(indent_text))
		
		self.is_modified = True


	def indentSelectedLines(self, text):
		filecursor_y = self.getFilecursorY()
		filecursor_x = self.getFilecursorX()
		select_y = self.getSelectY()
		select_x = self.getSelectX()

		start_y = min(filecursor_y, select_y)
		end_y = max(filecursor_y, select_y)

		if start_y == end_y: # if selection is on one line
			start_x = min(filecursor_x, select_x)
			end_x = max(filecursor_x, select_x)

			line_string_left = self.file_lines[start_y][:start_x]
			line_string_right = self.file_lines[start_y][start_x:]
			line_string_left += text

			self.file_lines[start_y] = line_string_left + line_string_right
			self.is_modified = True

			self.moveFilecursorRight(len(text))
			if start_x == select_x: # if stored select value is start, set select to start + text length
				self.setSelectX(start_x + len(text))
			elif start_x == filecursor_x: # if filecursor marks start, set select to end + text length
				self.setSelectX(end_x + len(text))

			return

		# selection is on different lines 
		elif start_y == filecursor_y: # filecursor marks start
			start_x = filecursor_x
			end_x = select_x
		elif start_y == select_y: # selectPosition marks start
			start_x = select_x
			end_x = filecursor_x

		for line_index in range(start_y, end_y + 1): # + 1 to end range on end_y
			line = self.file_lines[line_index]
			if line == "": # don't tab empty lines 
				continue

			elif line_index == start_y: # if current line is selection start
				if start_x == len(line): # if start_x is at the end of the line, don't indent it
					continue
				elif start_x == filecursor_x and start_y == filecursor_y: # if filecursor is start, indent line and move filecursor right, continue to next line
					line = text + line
					self.file_lines[line_index] = line
					if start_x != 0: # don't move cursor if it's at the beginning of a line
						self.moveFilecursorRight(len(text))
					continue
				elif start_x == select_x and start_y == select_y: # if select position is end, shift it by text length
					if start_x != 0: # don't move select if it's at beginning of a line
						self.setSelectX(start_x + len(text))

			elif line_index == end_y: # if current line is end
				if end_x == 0: # if end_x is at start of the line, don't indent 
					continue
				elif end_x == filecursor_x and end_y == filecursor_y: # if filecursor is end, indent line and move filecursor right, continue to next line
					line = text + line
					self.file_lines[line_index] = line
					self.moveFilecursorRight(len(text))
					continue
				elif end_x == select_x and end_y == select_y: # if select position is end, shift it by text length
					self.setSelectX(end_x + len(text))
			
			line = text + line
			self.file_lines[line_index] = line

		self.is_modified = True

	def enterTextAtFilecursor(self, text):
		if text == "\t":
			if self.config["TabLength"] != "char":
				text = " " * self.config["TabLength"]
			if self.is_select_on:
				self.indentSelectedLines(text)
				return

		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()
		line_string_left = self.file_lines[filecursor_y][:filecursor_x]
		line_string_right = self.file_lines[filecursor_y][filecursor_x:]
		line_string_left += text

		self.file_lines[filecursor_y] = line_string_left + line_string_right
		self.moveFilecursorRight(len(text))
		self.is_modified = True
		
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
			if text in ["\"", "'"] and not self.is_repeating_quote:
				self.is_repeating_quote = True
				self.enterTextAtFilecursor(text)
				self.moveFilecursorLeft()
				self.is_repeating_quote = False

	def newLineAtFilecursor(self, auto_indent_override=True):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()
		line_string_left = self.file_lines[filecursor_y][:filecursor_x]
		line_string_right = self.file_lines[filecursor_y][filecursor_x:]
		indent_size = 0
		if self.config["AutoIndent"] and auto_indent_override:
			indent_size = len(line_string_left) - len(line_string_left.lstrip())
			line_string_right = line_string_left[:indent_size] + line_string_right

		self.file_lines[filecursor_y] = line_string_left
		self.file_lines.insert(filecursor_y + 1, "")
		self.moveFilecursorDown()
		self.file_lines[self.getFilecursorY()] = line_string_right
		self.moveFilecursorRight(indent_size)
		self.is_modified = True

	def backspaceTextAtFilecursor(self):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()

		if filecursor_x == 0:
			if filecursor_y > 0:
				line_string = self.file_lines[filecursor_y]
				self.file_lines.pop(filecursor_y)
				self.moveFilecursorUp()
				self.gotoEndOfLine()
				self.file_lines[self.getFilecursorY()] += line_string
		else:
			line_string_left = self.file_lines[filecursor_y][:filecursor_x - 1]
			line_string_right = self.file_lines[filecursor_y][filecursor_x:]
			self.file_lines[filecursor_y] = line_string_left + line_string_right
			self.moveFilecursorLeft()

		self.is_modified = True

	def saveFile(self):
		file_string = ""
		for line in self.file_lines:
			file_string += line + "\n"

		returnval = self.engine.get("savebar").save()
		if returnval == True: # saveBar save filename get success, save file
			self.file.save(file_string)

		return returnval

	def searchForText(self):
		pass

	def scrollDown(self):
		scroll_amount = self.config["ScrollAmount"]
		filecursor_y = self.getFilecursorY()
		self.jumpToLine(min(filecursor_y + scroll_amount, len(self.file_lines) - 1))

	def scrollUp(self):
		scroll_amount = self.config["ScrollAmount"]
		filecursor_y = self.getFilecursorY()
		self.jumpToLine(max(filecursor_y - scroll_amount, 0))

	def deleteLineAtFilecursor(self):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()

		if filecursor_y != len(self.file_lines) - 1:
			self.file_lines.pop(filecursor_y)
			if len(self.file_lines[filecursor_y]) >= filecursor_x:
				pass
			else:
				self.setFilecursorX(len(self.file_lines[filecursor_y]))

		else:
			self.file_lines.pop(filecursor_y)
			if len(self.file_lines) - 1 >= 0:
				self.moveFilecursorUp()
			else:
				self.setFilecursorX(0)

		self.is_modified = True

	def deleteTextAtFilecursor(self):
		filecursor_x = self.getFilecursorX()
		filecursor_y = self.getFilecursorY()

		if filecursor_x + 1 <= len(self.file_lines[filecursor_y]): # if there is text to the right of our self.filecursor
			line_string_left = self.file_lines[filecursor_y][:filecursor_x]
			line_string_right = self.file_lines[filecursor_y][filecursor_x + 1:]
			self.file_lines[filecursor_y] = line_string_left + line_string_right

		elif filecursor_y != len(self.file_lines) - 1: # else (no text to right of self.filecursor) if there is line below
			nextLine = self.file_lines[filecursor_y + 1] # append line below to current line
			self.file_lines.pop(filecursor_y + 1)
			self.file_lines[filecursor_y] += nextLine

		self.is_modified = True
