import string, shlex, subprocess, traceback

from modules.window import Window
class RunWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		self.config = self.engine.get("config").options

		self.run_cursor_x = 0
		self.run_string = ""
		self.run_output = ""
		self.top_text = " RUN OUTPUT (Press F2/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys) "

		self.run_cursor_bindings = {}
		self.bind()

		self.view_y = 0
		self.view_x = 0

		self.panel.hide()

	def update(self):
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1
		self.keepWindowInMainScreen()
		self.engine.update()

	def bind(self):

		self.run_cursor_bindings = {
			"KEY_LEFT":             self.moveRunCursorLeft,
			"KEY_RIGHT":            self.moveRunCursorRight,
			"KEY_BACKSPACE":        self.backspaceAtRunCursor,
			"^?":                   self.backspaceAtRunCursor,
			"^H":                   self.backspaceAtRunCursor,
			"KEY_DC":               self.deleteAtRunCursor,
			"KEY_HOME":             self.moveRunCursorToStart,
			"KEY_END":              self.moveRunCursorToEnd,
			"printable-character":  self.enterTextAtRunCursor
		}

		self.run_window_bindings = {
			"KEY_LEFT":  self.moveViewLeft,
			"KEY_RIGHT": self.moveViewRight,
			"KEY_UP":    self.moveViewUp,
			"KEY_DOWN":  self.moveViewDown
		}

	def moveViewUp(self):
		if self.view_y > 0:
			self.view_y -= 1

	def moveViewDown(self):
		self.view_y += 1

	def moveViewLeft(self):
		if self.view_x > 0:
			self.view_x -= 1

	def moveViewRight(self):
		self.view_x += 1


	def moveRunCursorLeft(self):
		if self.run_cursor_x > 0:
			self.run_cursor_x -= 1

	def moveRunCursorRight(self):
		if self.run_cursor_x < len(self.run_string):
			self.run_cursor_x += 1

	def backspaceAtRunCursor(self):
		if self.run_cursor_x > 0:
			search_string_left = self.run_string[:self.run_cursor_x - 1]
			search_string_right = self.run_string[self.run_cursor_x:]
			self.run_string = search_string_left + search_string_right
			self.run_cursor_x -= 1

	def deleteAtRunCursor(self):
		if self.run_cursor_x + 1 <= len(self.run_string): # if there is text to the right of our cursor
			search_string_left = self.run_string[:self.run_cursor_x]
			search_string_right = self.run_string[self.run_cursor_x + 1:]
			self.run_string = search_string_left + search_string_right

	def moveRunCursorToStart(self):
		if self.run_cursor_x > 0:
			self.run_cursor_x = 0

	def moveRunCursorToEnd(self):
		if self.run_cursor_x < len(self.run_string):
			self.run_cursor_x = len(self.run_string)

	def enterTextAtRunCursor(self, text):
		run_string_left = self.run_string[:self.run_cursor_x] + text
		run_string_right = self.run_string[self.run_cursor_x:]
		self.run_string = run_string_left + run_string_right
		self.run_cursor_x += 1

	def run(self):
		self.panel.show()
		self.panel.top()
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getScreenMaxY() - 2
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.engine.update()
		
		self.config = self.engine.get("config").options

		prompt = "Run command: "

		self.window.addnstr(0, 0, prompt + self.run_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)

		if self.run_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.run_cursor_x >= 0:
			self.window.chgat(0, self.run_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

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

			if c in self.run_cursor_bindings:
				self.run_cursor_bindings[c]()
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.run_cursor_bindings["printable-character"](c)
			elif c == "^J": # enter key
				break
			elif c == "^[": # ESC
				self.panel.hide()
				return

			self.keepWindowInMainScreen()
			self.window.addnstr(0, 0, prompt + self.run_string, self.getWindowMaxX() - 1, self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)

			if self.run_cursor_x + len(prompt) <= self.getWindowMaxX() - 2 and self.run_cursor_x >= 0:
				self.window.chgat(0, self.run_cursor_x + len(prompt), 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

			self.engine.update()

		if self.run_string != "":
			self.run_output = '\n' + prompt + self.run_string + '\n\n'
			
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY()
			self.window.mvwin(0, 0)
			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.box()
			self.engine.update()

			try:
				args = shlex.split(self.run_string)
				with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=1) as p:
					for line in p.stdout:
						self.run_output += line
			except:
				self.run_output = traceback.format_exc()

			self.view_y = 0
			self.view_x = 0

			lines = self.run_output.split('\n')

			while True:
				self.intended_x			= 0
				self.intended_y			= 0
				self.intended_width		= self.getScreenMaxX() - 1
				self.intended_height	= self.getScreenMaxY()

				self.keepWindowInMainScreen()
				self.window.erase()
				self.window.box()
				window_y = 1
				window_max_y = self.getWindowMaxY()
				window_max_x = self.getWindowMaxX()
				if window_max_y - 1 > 1:
					self.window.addnstr(0, 1, self.top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)
				for line in lines[self.view_y:]:
					line = line.expandtabs(self.config["TabSize"])[self.view_x:]
					if window_y >= window_max_y - 1:
						break
					self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
					window_y += 1

				self.engine.update()
				
				try:
					c = self.engine.screen.getch()
				except KeyboardInterrupt:
					break
				if c == -1:
					continue

				c = self.engine.curses.keyname(c)
				c = c.decode("utf-8")

				if c in self.run_window_bindings:
					self.run_window_bindings[c]()

				if c == "^J" or c == "KEY_F(2)" or c == " " or c == "^[":
					break

		self.keepWindowInMainScreen()
		self.panel.hide()

	def terminate(self):
		pass
