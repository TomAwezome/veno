import re, string

from modules.window import Window
class SearchBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		
		## FileWindow instance SearchBar is attached to.
		self.file_window = self.manager.get("current_file_window")
		
		self.config = self.manager.get("config").options

		self.search_cursor_x = 0
		self.search_string = ""

		self.pattern_matches = None
		self.next_match = None

		self.search_bindings	= {}
		self.replace_bindings	= {}

		self.bind()

		self.panel.hide()

	def update(self):
		self.file_window = self.manager.get("current_file_window")

		self.cursor = self.file_window.filecursor

		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getStdscrMaxY() - 2
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		self.manager.update()

	def bind(self):
		self.search_bindings = {
			"KEY_LEFT":      self.moveSearchCursorLeft,
			"KEY_RIGHT":     self.moveSearchCursorRight,
			"KEY_BACKSPACE": self.backspaceAtSearchCursor,
			"^?":            self.backspaceAtSearchCursor,
			"^H":            self.backspaceAtSearchCursor,
			"KEY_DC":        self.deleteAtSearchCursor,
			"KEY_HOME":      self.moveSearchCursorToStart,
			"KEY_END":       self.moveSearchCursorToEnd,
			"^I":            self.enterTabAtSearchCursor,
			"^V":            self.pasteAtSearchCursor,

			"printable-character": self.enterTextAtSearchCursor
		}

		self.replace_bindings = {
			"y": self.replaceTextAtMatch,
			"a": self.replaceAllMatches
		}

	def moveSearchCursorLeft(self):
		if self.search_cursor_x > 0:
			self.search_cursor_x -= 1

	def moveSearchCursorRight(self):
		if self.search_cursor_x < len(self.search_string):
			self.search_cursor_x += 1

	def backspaceAtSearchCursor(self):
		if self.search_cursor_x > 0:
			search_string_left = self.search_string[:self.search_cursor_x - 1]
			search_string_right = self.search_string[self.search_cursor_x:]
			self.search_string = search_string_left + search_string_right
			self.search_cursor_x -= 1

	def deleteAtSearchCursor(self):
		if self.search_cursor_x + 1 <= len(self.search_string): # if there is text to the right of our cursor
			search_string_left = self.search_string[:self.search_cursor_x]
			search_string_right = self.search_string[self.search_cursor_x + 1:]
			self.search_string = search_string_left + search_string_right

	def moveSearchCursorToStart(self):
		if self.search_cursor_x > 0:
			self.search_cursor_x = 0

	def moveSearchCursorToEnd(self):
		if self.search_cursor_x < len(self.search_string):
			self.search_cursor_x = len(self.search_string)

	def enterTabAtSearchCursor(self):
		search_string_left = self.search_string[:self.search_cursor_x] + '\t'
		search_string_right = self.search_string[self.search_cursor_x:]
		self.search_string = search_string_left + search_string_right
		self.search_cursor_x += 1

	def enterTextAtSearchCursor(self, text):
		search_string_left = self.search_string[:self.search_cursor_x] + text
		search_string_right = self.search_string[self.search_cursor_x:]
		self.search_string = search_string_left + search_string_right
		self.search_cursor_x += 1

	def pasteAtSearchCursor(self):
		if self.file_window.copy_lines != []:
			paste_string = "\\n".join(self.file_window.copy_lines)

# TODO: make a config option or class member boolean for regex Find mode to fix this?
#	if the following lines are commented, Find breaks; uncommented, pasting LOC into Find field will work with regex,
#	but if pasting into Replace field, resulting text has garbage extra \ symbols ...

			paste_string = paste_string.replace("(", "\(").replace("[", "\[").replace("{", "\{") # replacements
			paste_string = paste_string.replace(")", "\)").replace("]", "\]").replace("}", "\}") # for regex: ()[]{}|?+*$^.
			paste_string = paste_string.replace("|", "\|").replace("?", "\?").replace("+", "\+").replace("\t", "\\t")
			paste_string = paste_string.replace("*", "\*").replace("$", "\$").replace("^", "\^").replace(".", "\.")

			search_string_left = self.search_string[:self.search_cursor_x] + paste_string
			search_string_right = self.search_string[self.search_cursor_x:]
			self.search_string = search_string_left + search_string_right
			self.search_cursor_x += len(paste_string)

	def replaceTextAtMatch(self, first_string, second_string):
		file_lines = self.file_window.file_lines
		file_string = '\n'.join(file_lines)

		replaced_string = re.sub(first_string, second_string, file_string[self.next_match.start():self.next_match.end()])
		replaced_string_left = file_string[:self.next_match.start()]
		replaced_string_right = file_string[self.next_match.end():]
		replaced_string_combined = replaced_string_left + replaced_string + replaced_string_right
		self.file_window.file_lines = replaced_string_combined.splitlines()
		self.file_window.file.contents = replaced_string_combined

	def replaceAllMatches(self, first_string, second_string):
		file_lines = self.file_window.file_lines
		file_string = '\n'.join(file_lines)
		replaced_string = re.sub(first_string, second_string, file_string)
		self.file_window.file.contents = replaced_string
		self.file_window.file_lines = replaced_string.splitlines()

	def search(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0 
		self.intended_y			= self.getStdscrMaxY() - 2
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		tab_expand_size = self.config["TabExpandSize"]
		prompt = "Search: "
		self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

		tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
		if self.search_cursor_x + tab_diff + len(prompt) <= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
			self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.panel.hide()
				return

			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.search_bindings:
				self.search_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.search_bindings["printable-character"](c)
			elif c == "^J": # enter key
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

			tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
			if self.search_cursor_x + tab_diff + len(prompt)<= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
				self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		try:
			pattern = re.compile(self.search_string)
		except:
			self.panel.hide()
			return

		self.pattern_matches = pattern.finditer(self.file_window.file.contents)
		try:
			self.next_match = next(self.pattern_matches)
			search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
			search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
			if len(search_lines) > 0:
				search_index_x = len(search_lines[len(search_lines) - 1])
		except StopIteration:
			self.next_match = None

		if self.next_match:
			while search_index_y < self.cursor[1]:
				try:
					self.next_match = next(self.pattern_matches)
					search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
					search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
					if len(search_lines) > 0:
						search_index_x = len(search_lines[len(search_lines) - 1])
				except StopIteration:
					break

			while search_index_y == self.cursor[1] and search_index_x <= self.cursor[0]:
				try:
					self.next_match = next(self.pattern_matches)
					search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
					search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
					if len(search_lines) > 0:
						search_index_x = len(search_lines[len(search_lines) - 1])
				except StopIteration:
					break

			self.file_window.jumpToLine(search_index_y)
			self.file_window.setFilecursorX(search_index_x)
			self.cursor = self.file_window.filecursor

			self.keepWindowInMainScreen()

		self.panel.hide()

	def searchNext(self):
		try:
			try:
				self.next_match = next(self.pattern_matches) # next operates to go down iterator, in this case if hitting first instance of given string, next() will start at that first index and continue through matches
			except TypeError: # if patternMatches is not iterator, next() raises TypeError. Catch and abort.
				return

			search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
			search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
			if len(search_lines) > 0:
				search_index_x = len(search_lines[len(search_lines) - 1])

			self.file_window.jumpToLine(search_index_y)
			self.file_window.setFilecursorX(search_index_x)

		except StopIteration:
			pass

	def replace(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getStdscrMaxY() - 2
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()	
		self.manager.update()
		self.keepWindowInMainScreen()

		tab_expand_size = self.config["TabExpandSize"]

		prompt = "Replace: "

		self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

		tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
		if self.search_cursor_x + tab_diff + len(prompt) <= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
			self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()

	# search string
	# keypress loop: begin catching characters
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.panel.hide()
				return
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.search_bindings:
				self.search_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.search_bindings["printable-character"](c)
			elif c == "^J": # enter key
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

			tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
			if self.search_cursor_x + tab_diff + len(prompt) <= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
				self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()
		
		first_string = self.search_string
		
	# replacement string
	# keypress loop: begin catching characters
		self.search_string = ""
		self.search_cursor_x = 0

		self.manager.update()
		self.keepWindowInMainScreen()

		prompt = "Replace with: "

		self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

		tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
		if self.search_cursor_x + tab_diff + len(prompt) <= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
			self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()

		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.panel.hide()
				return
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.search_bindings:
				self.search_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.search_bindings["printable-character"](c)
			elif c == "^J": # enter key
				break
			
			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.search_string.expandtabs(tab_expand_size), self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

			tab_diff = len(self.search_string[:self.search_cursor_x].expandtabs(tab_expand_size)) - len(self.search_string[:self.search_cursor_x])
			if self.search_cursor_x + tab_diff + len(prompt) <= self.getWindowMaxX() - 2 and self.search_cursor_x >= 0:
				self.window.chgat(0, self.search_cursor_x + tab_diff + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()
			
		second_string = self.search_string

		file_lines = self.file_window.file_lines
		file_string = '\n'.join(file_lines)

		# next we'll find the first occurence (relative to our cursor) of our to-be-replaced string, and move the file cursor there and have our current nexMatch be that occurence
		try:
			pattern = re.compile(first_string)
		except:
			self.panel.hide()
			return

		self.pattern_matches = pattern.finditer(self.file_window.file.contents)
		try:
			self.next_match = next(self.pattern_matches)
			search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
			search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
			if len(search_lines) > 0:
				search_index_x = len(search_lines[len(search_lines) - 1])
		except StopIteration:
			pass

		if self.next_match:
			while search_index_y < self.cursor[1]:
				try:
					self.next_match = next(self.pattern_matches)
					search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
					search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
					if len(search_lines) > 0:
						search_index_x = len(search_lines[len(search_lines) - 1])
				except StopIteration:
					break

			while search_index_y == self.cursor[1] and search_index_x < self.cursor[0]:
				try:
					self.next_match = next(self.pattern_matches)
					search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
					search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
					if len(search_lines) > 0:
						search_index_x = len(search_lines[len(search_lines) - 1])
				except StopIteration:
					break

			self.file_window.jumpToLine(search_index_y)
			self.file_window.moveFilecursorDown() # kludge to keep replace results onscreen since savebar draws overtop FileWindow bottom line
			self.file_window.moveFilecursorUp() # "" !! this doesn't work if match at last FileWindow line!!
			self.file_window.setFilecursorX(search_index_x)

			self.keepWindowInMainScreen()

		self.file_window.is_modified = True
		self.file_window.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement

		self.manager.get("highlighter").update()

		self.manager.update()

		while True: # break out of this loop with enter key
			if not self.next_match:
				break

			self.window.erase()
			self.window.addnstr(0, 0, "Replace? (y/n/a) ['a' = All]", self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

			self.manager.get("line_numbers").update()

			self.manager.update()

			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.replace_bindings:
				self.replace_bindings[c](first_string, second_string)
				if c == "a":
					break
			elif c == "n":
				pass
			elif c == "^J": # enter key
				break

			self.pattern_matches = pattern.finditer(self.file_window.file.contents)
			try:
				self.next_match = next(self.pattern_matches)
				search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
				search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
				if len(search_lines) > 0:
					search_index_x = len(search_lines[len(search_lines) - 1])
			except StopIteration:
				break

			if self.next_match:
				while search_index_y < self.cursor[1]:
					try:
						self.next_match = next(self.pattern_matches)
						search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
						search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
						if len(search_lines) > 0:
							search_index_x = len(search_lines[len(search_lines) - 1])
					except StopIteration:
						break

				while search_index_y == self.cursor[1] and search_index_x <= self.cursor[0]:
					try:
						self.next_match = next(self.pattern_matches)
						search_index_y = self.file_window.file.contents[:self.next_match.start()].count('\n')
						search_lines = self.file_window.file.contents[:self.next_match.start()].split('\n')
						if len(search_lines) > 0:
							search_index_x = len(search_lines[len(search_lines) - 1])
					except StopIteration:
						break

				self.file_window.jumpToLine(search_index_y)
				self.file_window.moveFilecursorDown() # kludge to keep replace results onscreen since savebar draws overtop FileWindow bottom line
				self.file_window.moveFilecursorUp() # ""  !! this doesn't work if match at last FileWindow line!!
				self.file_window.setFilecursorX(search_index_x)

				self.keepWindowInMainScreen()

			self.keepWindowInMainScreen()

			self.file_window.is_modified = True
			self.file_window.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement

			self.manager.get("highlighter").update()

			self.manager.update()

		self.window.erase()
		self.keepWindowInMainScreen()

		self.file_window.is_modified = True
		self.file_window.update() # this is broken, I need to take this to a module in loop stack order above these to not have to update every module upon movement

		self.manager.get("highlighter").update()

		self.manager.update()

		self.panel.hide()

	def terminate(self):
		pass
