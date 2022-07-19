import string

from modules.window import Window
class OpenBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		self.open_cursor_x = 0
		self.open_string = ""

		# Functions are stored in these dictionaries for OpenBar curses getch() loops.
		self.open_bindings		= {}
		self.bind()

		self.panel.hide()

	def update(self):

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

		self.open_bindings = {
			"KEY_LEFT":      self.moveOpenCursorLeft,
			"KEY_RIGHT":     self.moveOpenCursorRight,
			"KEY_BACKSPACE": self.backspaceAtOpenCursor,
			"^?":            self.backspaceAtOpenCursor,
			"^H":            self.backspaceAtOpenCursor,
			"KEY_DC":        self.deleteAtOpenCursor,
			"KEY_HOME":      self.moveOpenCursorToStart,
			"KEY_END":       self.moveOpenCursorToEnd,

			"printable-character": self.enterTextAtOpenCursor
		}

	def moveOpenCursorLeft(self):
		if self.open_cursor_x > 0:
			self.open_cursor_x -= 1

	def moveOpenCursorRight(self):
		if self.open_cursor_x < len(self.open_string):
			self.open_cursor_x += 1

	def backspaceAtOpenCursor(self):
		if self.open_cursor_x > 0:
			open_string_left = self.open_string[:self.open_cursor_x - 1]
			open_string_right = self.open_string[self.open_cursor_x:]
			self.open_string = open_string_left + open_string_right
			self.open_cursor_x -= 1

	def deleteAtOpenCursor(self):
		if self.open_cursor_x + 1 <= len(self.open_string): # if there is text to the right of our cursor
			open_string_left = self.open_string[:self.open_cursor_x]
			open_string_right = self.open_string[self.open_cursor_x + 1:]
			self.open_string = open_string_left + open_string_right

	def moveOpenCursorToStart(self):
		if self.open_cursor_x > 0:
			self.open_cursor_x = 0

	def moveOpenCursorToEnd(self):
		if self.open_cursor_x < len(self.open_string):
			self.open_cursor_x = len(self.open_string)

	def enterTextAtOpenCursor(self, text):
		open_string_left = self.open_string[:self.open_cursor_x] + text
		open_string_right = self.open_string[self.open_cursor_x:]
		self.open_string = open_string_left + open_string_right
		self.open_cursor_x += 1

	def openFile(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getStdscrMaxY() - 2
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		result = True
		
		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		# openfile string
		# keypress loop: begin catching characters
		self.window.erase()
		prompt = "Open Filename: "
		self.window.addnstr(0, 0, prompt + self.open_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)

		if self.open_cursor_x <= self.getWindowMaxX() - 2 and self.open_cursor_x >= 0:
			self.window.chgat(0, self.open_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

		self.manager.update()
		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				result = False
				self.panel.hide()
				break
			if c == -1:
				continue
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.open_bindings:
				self.open_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.open_bindings["printable-character"](c)
			elif c == "^J": # enter key
				if self.open_string != "":
					break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.open_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)

			if self.open_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.open_cursor_x >= 0:
				self.window.chgat(0, self.open_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		File = self.manager.get("File")
		FileWindow = self.manager.get("FileWindow")
		file = File(self.open_string)
		file_window = FileWindow(self.manager, "", file)		# Create fileWindow.
		self.manager.get("file_window_list").append(file_window)

		self.panel.hide()
		
		return result

	def terminate(self):
		pass
