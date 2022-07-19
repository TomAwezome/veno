from modules.window import Window
class HelpWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		self.is_open = False

		self.panel.hide()

	def update(self):
		if not self.is_open:
			return

		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= 0
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= self.getStdscrMaxY() - 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		self.manager.update()

		self.panel.top()

		while True:
			self.keepWindowInMainScreen()

			self.window.erase()
			self.window.addnstr(0, 0, "HELP (Press Enter to dismiss Help window)", self.getWindowMaxX() - 1, self.manager.curses.color_pair(4) | self.manager.curses.A_REVERSE)
			# todo make help text a larger string and use loop logic to within-window-bounds print help text from top line to bottom line

			self.manager.update()

			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.toggle()
				break
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if c == "^J":
				self.toggle()
				break

	def toggle(self):
		if self.is_open:
			self.is_open = False
			self.panel.hide()
		else:
			self.is_open = True
			self.panel.show()

	def terminate(self):
		pass

