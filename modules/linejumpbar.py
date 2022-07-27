import string

from modules.window import Window
class LineJumpBar(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		## FileWindow instance LineJumpBar is attached to.
		self.file_window = self.engine.get("current_file_window")

		self.line_jump_cursor_x = 0
		self.line_jump_string = ""

		# Functions are stored in these dictionaries for LineJumpBar curses getch() loops.
		self.line_jump_bindings = {}
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
			line_jump_string_left = self.line_jump_string[:self.line_jump_cursor_x - 1]
			line_jump_string_right = self.line_jump_string[self.line_jump_cursor_x:]
			self.line_jump_string = line_jump_string_left + line_jump_string_right
			self.line_jump_cursor_x -= 1

	def deleteAtLineJumpCursor(self):
		if self.line_jump_cursor_x + 1 <= len(self.line_jump_string): # if there is text to the right of our cursor
			line_jump_string_left = self.line_jump_string[:self.line_jump_cursor_x]
			line_jump_string_right = self.line_jump_string[self.line_jump_cursor_x + 1:]
			self.line_jump_string = line_jump_string_left + line_jump_string_right

	def moveLineJumpCursorToStart(self):
		if self.line_jump_cursor_x > 0:
			self.line_jump_cursor_x = 0

	def moveLineJumpCursorToEnd(self):
		if self.line_jump_cursor_x < len(self.line_jump_string):
			self.line_jump_cursor_x = len(self.line_jump_string)

	def enterDigitAtLineJumpCursor(self, digit):
		line_jump_string_left = self.line_jump_string[:self.line_jump_cursor_x] + digit
		line_jump_string_right = self.line_jump_string[self.line_jump_cursor_x:]
		self.line_jump_string = line_jump_string_left + line_jump_string_right
		self.line_jump_cursor_x += 1

	def jumpToLine(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.engine.update()

		prompt = "Line: "

		self.window.addnstr(0, 0, prompt + self.line_jump_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(7) | self.engine.curses.A_REVERSE)

		if self.line_jump_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.line_jump_cursor_x >= 0:
			self.window.chgat(0, self.line_jump_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

		self.engine.update()

		while True: # break out of this loop with enter key
			self.window.erase()
			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				self.panel.hide()
				return
			if c == -1:
				continue
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.line_jump_bindings:
				self.line_jump_bindings[c]()
			elif c in string.digits:
				self.line_jump_bindings["digit"](c)
			elif c == "^J": # enter key
				break

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.line_jump_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(7) | self.engine.curses.A_REVERSE)

			if self.line_jump_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.line_jump_cursor_x >= 0:
				self.window.chgat(0, self.line_jump_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

			self.engine.update()

		if self.line_jump_string != "":
			lineNumber = int(self.line_jump_string)
			if lineNumber > 0:
				self.file_window.jumpToLine(lineNumber - 1)

		self.keepWindowInMainScreen()
		self.panel.hide()

	def terminate(self):
		pass
