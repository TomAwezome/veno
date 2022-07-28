from modules.window import Window
class DebugWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		self.intended_y	= self.intended_x = 0
		self.intended_width		= self.getScreenMaxX()
		self.intended_height	= self.getScreenMaxY() - 5

		self.is_open = False

		self.debug = self.engine.get("debug")

		self.window.erase()
		self.keepWindowInMainScreen()

		self.panel.hide()

	def update(self):
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= 0
		self.intended_width		= self.getScreenMaxX()
		self.intended_height	= self.getScreenMaxY() - 5
		self.keepWindowInMainScreen()
		self.window.box()

		window_y = 1
		window_max_y = self.getWindowMaxY()
		window_max_x = self.getWindowMaxX()
		
		if not self.is_open:
			return

		self.panel.top()

		if window_max_y - 1 < 1:
			return
		self.window.addnstr(0, 1, " DEBUG (Press F12 to dismiss) ", window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)

		self.debug.log("Global Objects:")

		items = self.engine.global_objects.items()
		for key, val in items:
			self.debug.log(f"    {key}".ljust(26) + f"{val}")

		lines = self.debug.text.split("\n")
		if len(lines) > window_max_y + 2:
			lines = lines[len(lines) - window_max_y + 2:]
		for line in lines:
			if window_y >= window_max_y - 1:
				break
			self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
			window_y += 1

	def toggle(self):
		if self.is_open:
			self.is_open = False
			self.panel.hide()
		else:
			self.is_open = True
			self.panel.show()

	def terminate(self):
		pass
		
