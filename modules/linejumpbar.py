import string

from modules.window import Window
class LineJumpBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		## FileWindow instance LineJumpBar is attached to.
		self.file_window = self.manager.get("current_file_window")

		self.config = self.manager.get("config").options

		self.line_jump_cursor_x = 0
		self.line_jump_string = ""

		# Functions are stored in these dictionaries for LineJumpBar curses getch() loops.
		self.line_jump_bindings = {}
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

		self.line_jump_bindings = {
			"KEY_LEFT":      self.moveLineJumpCursorLeft,
			"KEY_RIGHT":     self.moveLineJumpCursorRight,
			"KEY_BACKSPACE": self.backspaceAtLineJumpCursor,
			"^?":            self.backspaceAtLineJumpCursor,
			"^H":            self.backspaceAtLineJumpCursor,
			"KEY_DC":        self.deleteAtLineJumpCursor,
			"KEY_HOME":      self.moveLineJumpCursorToStart,
			"KEY_END":       self.moveLineJumpCursorToEnd,
			"digit":         self.enterDigitAtLineJumpCursor
		}

	def moveLineJumpCursorLeft(self):
		if self.line_jump_cursor_x > 0:
			self.line_jump_cursor_x -= 1

	def moveLineJumpCursorRight(self):
		if self.line_jump_cursor_x < len(self.line_jump_string):
			self.line_jump_cursor_x += 1

	def backspaceAtLineJumpCursor(self):
		if self.line_jump_cursor_x > 0:
			search_string_left = self.line_jump_string[:self.line_jump_cursor_x - 1]
			search_string_right = self.line_jump_string[self.line_jump_cursor_x:]
			self.line_jump_string = search_string_left + search_string_right
			self.line_jump_cursor_x -= 1

	def deleteAtLineJumpCursor(self):
		if self.line_jump_cursor_x + 1 <= len(self.line_jump_string): # if there is text to the right of our cursor
			search_string_left = self.line_jump_string[:self.line_jump_cursor_x]
			search_string_right = self.line_jump_string[self.line_jump_cursor_x + 1:]
			self.line_jump_string = search_string_left + search_string_right

	def moveLineJumpCursorToStart(self):
		if self.line_jump_cursor_x > 0:
			self.line_jump_cursor_x = 0

	def moveLineJumpCursorToEnd(self):
		if self.line_jump_cursor_x < len(self.line_jump_string):
			self.line_jump_cursor_x = len(self.line_jump_string)

	def enterDigitAtLineJumpCursor(self, digit):
		search_string_left = self.line_jump_string[:self.line_jump_cursor_x] + digit
		search_string_right = self.line_jump_string[self.line_jump_cursor_x:]
		self.line_jump_string = search_string_left + search_string_right
		self.line_jump_cursor_x += 1

	def jumpToLine(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getStdscrMaxY() - 2
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()

		prompt = "Line: "

		self.window.addnstr(0, 0, prompt + self.line_jump_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

		if self.line_jump_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.line_jump_cursor_x >= 0:
			self.window.chgat(0, self.line_jump_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

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

			if c in self.line_jump_bindings:
				self.line_jump_bindings[c]()
			elif c in string.digits:
				self.line_jump_bindings["digit"](c)
			elif c == "^J": # enter key
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.line_jump_string, self.getWindowMaxX() - 1, self.manager.curses.color_pair(7) | self.manager.curses.A_REVERSE)

			if self.line_jump_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.line_jump_cursor_x >= 0:
				self.window.chgat(0, self.line_jump_cursor_x + len(prompt), 1, self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE)

			self.manager.update()

		if self.line_jump_string != "":
			lineNumber = int(self.line_jump_string)
			if lineNumber > 0:
				self.file_window.jumpToLine(lineNumber - 1)

		self.keepWindowInMainScreen()
		self.panel.hide()

	def terminate(self):
		pass
