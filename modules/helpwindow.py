from modules.window import Window
class HelpWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		self.is_open = False

		self.panel.hide()
		
		self.help_top_text = " HELP (Press Enter to dismiss Help window) "

		self.help_header_text = """
VENO

Multi-purpose text/code editor meant for easy and vast expandability.

"""
		self.help_body_text = ""
		
		self.view_y = 0

		self.bindings = {}

		self.bind()

	def update(self):
		if not self.is_open:
			return

		self.panel.top()

		self.help_body_text = "Keybindings:\n\n"
		bindings = self.manager.get("keybindings")
		items = bindings.items()
		for key, val in items:
			key = key.replace("^", "Ctrl-")
			body_line_left = f"{key}:".ljust(21)
			body_line_right = f"{val}\n"
			self.help_body_text += body_line_left + body_line_right

		text = self.help_header_text + self.help_body_text
		lines = text.split("\n")

		while True:
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getStdscrMaxX() - 1
			self.intended_height	= self.getStdscrMaxY() - 1

			self.keepWindowInMainScreen()
			self.manager.update()

			self.window.erase()

			window_y = 1
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()
			self.window.box()
			if window_max_y - 1 > 1:
				self.window.addnstr(0, 1, self.help_top_text, window_max_x - 2, self.manager.curses.color_pair(0) | self.manager.curses.A_REVERSE)
			for line in lines[self.view_y:]:
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line, window_max_x - 2, self.manager.curses.color_pair(4))
				window_y += 1

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

			if c in self.bindings:
				self.bindings[c]()

			if c == "^J" or c == "KEY_F(1)":
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

