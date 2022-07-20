import string

from modules.window import Window
class SaveBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		## FileWindow instance SaveBar is attached to.
		self.file_window = self.manager.get("current_file_window")

		self.config = self.manager.get("config").options

		self.save_cursor_x = 0
		self.save_string = self.file_window.file.source

		# Functions are stored in these dictionaries for SaveBar curses getch() loops.
		self.save_bindings		= {}
		self.bind()

		self.panel.hide()

	def update(self):
		self.file_window = self.manager.get("current_file_window")

		self.cursor = self.file_window.filecursor

		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		self.manager.update()

	def bind(self):

		self.save_bindings = {
			"KEY_LEFT":      self.moveSaveCursorLeft,
			"KEY_RIGHT":     self.moveSaveCursorRight,
			"KEY_BACKSPACE": self.backspaceAtSaveCursor,
			"^?":            self.backspaceAtSaveCursor,
			"^H":            self.backspaceAtSaveCursor,
			"KEY_DC":        self.deleteAtSaveCursor,
			"KEY_HOME":      self.moveSaveCursorToStart,
			"KEY_END":       self.moveSaveCursorToEnd,

			"printable-character": self.enterTextAtSaveCursor
		}


	def moveSaveCursorLeft(self):
		if self.save_cursor_x > 0:
			self.save_cursor_x -= 1

	def moveSaveCursorRight(self):
		if self.save_cursor_x < len(self.save_string):
			self.save_cursor_x += 1

	def backspaceAtSaveCursor(self):
		if self.save_cursor_x > 0:
			save_string_left = self.save_string[:self.save_cursor_x - 1]
			save_string_right = self.save_string[self.save_cursor_x:]
			self.save_string = save_string_left + save_string_right
			self.save_cursor_x -= 1

	def deleteAtSaveCursor(self):
		if self.save_cursor_x + 1 <= len(self.save_string): # if there is text to the right of our cursor
			save_string_left = self.save_string[:self.save_cursor_x]
			save_string_right = self.save_string[self.save_cursor_x + 1:]
			self.save_string = save_string_left + save_string_right

	def moveSaveCursorToStart(self):
		if self.save_cursor_x > 0:
			self.save_cursor_x = 0

	def moveSaveCursorToEnd(self):
		if self.save_cursor_x < len(self.save_string):
			self.save_cursor_x = len(self.save_string)

	def enterTextAtSaveCursor(self, text):
		save_string_left = self.save_string[:self.save_cursor_x] + text
		save_string_right = self.save_string[self.save_cursor_x:]
		self.save_string = save_string_left + save_string_right
		self.save_cursor_x += 1

	def confirmExitSave(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		result = False

		while True:
			self.keepWindowInMainScreen()

			self.window.erase()
			self.window.addnstr(0, 0, "Save before exit? (Y/N or Enter/Ctrl-C)", self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)

			self.manager.update()

			try:
				c = self.manager.screen.getch()
			except KeyboardInterrupt:
				result = True # (Ctrl-C to refuse exit save)
				break
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if c.lower() == 'n':
				result = True
				break
			if c == "^J" or c.lower() == "y":
				self.window.erase()
				if self.file_window.saveFile() == True: # successfully saved
					result = True
					break
				else: # Ctrl-C to exit confirmExitSave and return to file
					break

		return result

	def save(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1
		returnval = True

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		self.save_string = self.file_window.file.source

		# savefile string
		# keypress loop: begin catching characters
		self.window.erase()
		prompt = "Save Filename: "
		self.window.addnstr(0, 0, prompt + self.save_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)

		if self.save_cursor_x <= self.getWindowMaxX() - 2 and self.save_cursor_x >= 0:
			self.window.chgat(0, self.save_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.screen.getch()
			except KeyboardInterrupt:
				returnval = False
				self.panel.hide()
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.save_bindings:
				self.save_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.save_bindings["printable-character"](c)
			elif c == "^J": # enter key
				if self.save_string != "":
					break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.save_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)

			if self.save_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.save_cursor_x >= 0:
				self.window.chgat(0, self.save_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		self.file_window.file.source = self.save_string
		self.panel.hide()
		return returnval

	def terminate(self):
		pass
