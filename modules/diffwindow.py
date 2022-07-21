from difflib import unified_diff as diff

from modules.window import Window
class DiffWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		## FileWindow instance SearchBar is attached to.
		self.file_window = self.manager.get("current_file_window")

		self.is_open = False

		self.panel.hide()

		self.view_y = 0

		self.bindings = {}

		self.bind()

	def update(self):
		if not self.is_open:
			return

		self.panel.top()

		self.file_window = self.manager.get("current_file_window")
		
		File = self.manager.get("File")
		file = File(self.file_window.file.source)
		disk_file_lines = file.contents.splitlines()
		
		diff_result = diff(disk_file_lines, self.file_window.file_lines, "File on disk", "File in memory")
		diff_lines = []
		for line in diff_result:
			diff_lines.append(line)
		
		while True:
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY() - 1

			self.keepWindowInMainScreen()
			self.manager.update()

			self.window.erase()
			self.window.box()

			window_y = 1
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()

			if window_max_y - 1 < 1:
				return
			self.window.addnstr(0, 1, " DIFF (Press Ctrl-T to dismiss Diff window) ", window_max_x - 2, self.manager.curses.color_pair(0) | self.manager.curses.A_REVERSE)

			for line in diff_lines[self.view_y:]:
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line, window_max_x - 2, self.manager.curses.color_pair(0))
				window_y += 1

			self.manager.update()

			try:
				c = self.manager.screen.getch()
			except KeyboardInterrupt:
				self.toggle()
				break
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.bindings:
				self.bindings[c]()

			if c == "^J" or c == "^T":
				self.toggle()
				break

	def bind(self):
		self.bindings = {
#			"KEY_LEFT":  self.moveViewLeft,
#			"KEY_RIGHT": self.moveViewRight,
			"KEY_UP":    self.moveViewUp,
			"KEY_DOWN":  self.moveViewDown
		}

	def toggle(self):
		if self.is_open:
			self.is_open = False
			self.panel.hide()
		else:
			self.view_y = 0
			self.is_open = True
			self.panel.show()

	def moveViewUp(self):
		if self.view_y > 0:
			self.view_y -= 1

	def moveViewDown(self):
		self.view_y += 1

	def terminate(self):
		pass

