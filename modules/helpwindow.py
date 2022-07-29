import random

from modules.window import Window
class HelpWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		self.is_open = False

		self.panel.hide()
		
		self.help_top_text = " HELP (Press F1/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys) "

		self.help_logo_text = """
                 #               
                 ##              
 ##   ## ####### ###  ##  ##### 
 ##   ## ##      #### ## ##   ##
 ##   ## ####### ####### ##   ##
  ## ##  ##      ### ### ##   ##
   ###   ####### ###  ##  ##### 
    #                  #         
"""

		self.help_header_text = """

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
		bindings = self.engine.get("bindings")
		items = bindings.items()
		self.help_body_text += "Ctrl-C:".ljust(22) + "Cancel / Quit (Global Keybinding)\n\n"
		for key, val in items:
			key = key.replace("^", "Ctrl-")
			body_line_left = f"{key}:".ljust(22)
			body_line_right = f"{val}".replace("<bound method ", "")
			body_line_right = body_line_right[:body_line_right.index(" ")] + "\n"
			self.help_body_text += body_line_left + body_line_right

		text = self.help_header_text + self.help_body_text
		lines = text.split("\n")

		color = random.randint(2,8)
		
		while True:
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY() - 1

			self.keepWindowInMainScreen()
			self.engine.update()

			self.window.erase()

			window_y = 1
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()
			self.window.box()
			if window_max_y - 1 > 1:
				self.window.addnstr(0, 1, self.help_top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)
			for line in self.help_logo_text.split('\n')[self.view_y:]:
				if window_y >= window_max_y - 1:
					break
				window_x = 0
				for char in line:
					if window_x >= window_max_x - 1:
						break
					if char == '#':
						self.window.chgat(window_y, window_x, 1, self.engine.curses.color_pair(color) | self.engine.curses.A_REVERSE)
					window_x += 1
				window_y += 1
			for line in lines[max(0, self.view_y - self.help_logo_text.count('\n')):]:
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
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

			if c == "^J" or c == "KEY_F(1)" or c == " " or c == "^[":
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
