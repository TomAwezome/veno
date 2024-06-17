from veno.modules.window import Window
class DiffWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		## FileWindow instance DiffWindow is attached to.
		self.file_window = self.engine.get("current_file_window")

		self.config = self.engine.get("config").options

		self.is_open = False

		self.panel.hide()

		self.view_y = 0
		self.view_x = 0

		self.bindings = {}

		self.bind()

	def update(self):
		if not self.is_open:
			return

		self.panel.top()

		self.config = self.engine.get("config").options

		tab_expand_size = self.config["TabSize"]

		self.file_window = self.engine.get("current_file_window")
		filename = self.file_window.file.source
		
		diff_result = self.file_window.diff()
		diff_lines = []
		for line in diff_result:
			diff_lines.append(line.expandtabs(tab_expand_size))
		if len(diff_result) == 0:
			diff_lines = ["", f"No differences between file on disk and file in memory. [ {filename} ]"]
		
		while True:
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY() - 1

			self.keepWindowInMainScreen()
			self.engine.update()

			self.window.erase()
			self.window.box()

			window_y = 1
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()

			if window_max_y - 1 < 1:
				return
			self.window.addnstr(0, 1, " DIFF (Press Ctrl-T/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys/PageUp/PageDown)", window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)

			for line in diff_lines[self.view_y:]:
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line[self.view_x:].rstrip(), window_max_x - 2, self.engine.curses.color_pair(0))
				if line != "":
					if line[0] == '-':
						self.window.chgat(window_y, 1, min(len(line[self.view_x:]), window_max_x - 2), self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)
					elif line[0] == '+':
						self.window.chgat(window_y, 1, min(len(line[self.view_x:]), window_max_x - 2), self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)
				window_y += 1

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				self.toggle()
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.bindings:
				self.bindings[c]()

			if c == "^J" or c == "^T" or c == " " or c == "^[":
				self.toggle()
				break

	def bind(self):
		self.bindings = {
			"KEY_LEFT":  self.moveViewLeft,
			"KEY_RIGHT": self.moveViewRight,
			"KEY_UP":    self.moveViewUp,
			"KEY_DOWN":  self.moveViewDown,
			"KEY_NPAGE": self.scrollViewDown,
			"KEY_PPAGE": self.scrollViewUp,
		}

	def toggle(self):
		if self.is_open:
			self.is_open = False
			self.panel.hide()
		else:
			self.view_y = 0
			self.view_x = 0
			self.is_open = True
			self.panel.show()

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

	def scrollViewDown(self):
		scroll_amount = self.config["ScrollAmount"]
		self.view_y += scroll_amount

	def scrollViewUp(self):
		scroll_amount = self.config["ScrollAmount"]
		self.view_y = max(0, self.view_y - scroll_amount)

	def terminate(self):
		pass
