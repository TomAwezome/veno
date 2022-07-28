import string

from modules.window import Window
class SaveBar(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		## FileWindow instance SaveBar is attached to.
		self.file_window = self.engine.get("current_file_window")

		self.diff_window = self.engine.get("diffwindow")

		self.window_bar = self.engine.get("windowbar")

		self.config = self.engine.get("config").options

		self.save_cursor_x = 0
		self.save_string = self.file_window.file.source

		# Functions are stored in these dictionaries for SaveBar curses getch() loops.
		self.save_bindings		= {}
		self.bind()

		self.panel.hide()

	def update(self):
		self.file_window = self.engine.get("current_file_window")

		self.cursor = self.file_window.filecursor

		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.engine.update()
		self.keepWindowInMainScreen()

		self.engine.update()

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

	def confirmCloseSave(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.engine.update()
		self.keepWindowInMainScreen()

		result = False

		file_window_list = self.engine.get("file_window_list")
		while True and len(file_window_list) == 1:
			self.keepWindowInMainScreen()

			self.window.erase()
			self.window.addnstr(0, 0, "Are you sure you want to exit? (Y/N)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				result = True
				return result
			if c == -1:
				continue
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")
			if c.lower() == 'n':
				result = False
				self.panel.hide()
				return result
			if c == "^J" or c.lower() == "y":
				break
			if c == "^[": # ESC
				result = True
				return result

		while True:
			self.keepWindowInMainScreen()

			self.window.erase()
			self.window.addnstr(0, 0, "Sync file before closing FileWindow? (Y/N or Enter/Ctrl-C)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				result = True # (Ctrl-C to refuse exit save)
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")
			if c == "^[": # ESC
				result = True
				break
			if c.lower() == 'n':
				result = True
				break
			if c == "^J" or c.lower() == "y":
				self.window.erase()
				self.file_window = self.engine.get("current_file_window")
				self.diff_window.view_y = 0
				self.diff_window.is_open = True
				self.diff_window.panel.show()
				self.diff_window.update()
				self.diff_window.toggle()

				while True: # ask if want to save
					self.panel.top()
					self.keepWindowInMainScreen()
					self.window.erase()
					self.window_bar.update()
					self.window.addnstr(0, 0, "Save file? (Y/N or Enter/Ctrl-C)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)
					self.engine.update()

					try:
						c = self.engine.screen.getch()
					except KeyboardInterrupt:
						break
					if c == -1:
						continue

					c = self.engine.curses.keyname(c)
					c = c.decode("utf-8")
					if c.lower() == 'n':
						break
					if c == "^J" or c.lower() == "y":
						self.window.erase()
						self.file_window.saveFile()
						break
					if c == "^[": # ESC
						break

				self.diff_window.toggle()
				result = True
				break

		self.panel.hide()

		return result

	def confirmExitSave(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.engine.update()
		self.keepWindowInMainScreen()

		result = False

		while True:
			self.keepWindowInMainScreen()

			self.window.erase()
			self.window.addnstr(0, 0, "Are you sure you want to exit? (Y/N)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				result = True
				return result
			if c == -1:
				continue
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")
			if c.lower() == 'n':
				result = False
				self.panel.hide()
				return result
			if c == "^J" or c.lower() == "y":
				break
			if c == "^[": # ESC
				result = True
				return result

		while True:
			self.keepWindowInMainScreen()

			self.window.erase()

			self.window.addnstr(0, 0, "Sync files before exit? (Y/N or Enter/Ctrl-C)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				result = True # (Ctrl-C to refuse exit save)
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")
			if c == "^[": # ESC
				result = True
				break
			if c.lower() == 'n':
				result = True
				break
			if c == "^J" or c.lower() == "y":
				self.window.erase()
				file_window_list = self.engine.get("file_window_list")
				while file_window_list != []:
					file_window = self.file_window = file_window_list[0]
					self.engine.set("current_file_window", file_window)
					self.window_bar.update()
					self.diff_window.view_y = 0
					self.diff_window.is_open = True
					self.diff_window.panel.show()
					self.diff_window.update()
					self.diff_window.toggle()
					while True: # ask if want to save
						self.panel.top()
						self.keepWindowInMainScreen()
						self.window.erase()
						self.window_bar.update()
						self.window.addnstr(0, 0, "Save file? (Y/N or Enter/Ctrl-C)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)
						self.engine.update()

						try:
							c = self.engine.screen.getch()
						except KeyboardInterrupt:
							break
						if c == -1:
							continue

						c = self.engine.curses.keyname(c)
						c = c.decode("utf-8")
						if c.lower() == 'n':
							break
						if c == "^J" or c.lower() == "y":
							self.window.erase()
							file_window.saveFile()
							break
						if c == "^[": # ESC
							break

					file_window_list.remove(file_window)

				result = True
				break

		self.panel.hide()

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
		self.engine.update()
		self.keepWindowInMainScreen()

		self.save_string = self.file_window.file.source

		# savefile string
		# keypress loop: begin catching characters
		self.window.erase()
		prompt = "Save Filename: "
		self.window.addnstr(0, 0, prompt + self.save_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

		if self.save_cursor_x <= self.getWindowMaxX() - 2 and self.save_cursor_x >= 0:
			self.window.chgat(0, self.save_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

		self.engine.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				returnval = False
				self.panel.hide()
				break
			if c == -1:
				continue
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.save_bindings:
				self.save_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.save_bindings["printable-character"](c)
			elif c == "^J": # enter key
				if self.save_string != "":
					break
			elif c == "^[": # ESC
				returnval = False
				self.panel.hide()
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.save_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)

			if self.save_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.save_cursor_x >= 0:
				self.window.chgat(0, self.save_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

			self.engine.update()

		self.file_window.file.source = self.save_string
		self.panel.hide()
		return returnval

	def terminate(self):
		pass
