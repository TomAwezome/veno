from modules.window import Window
class DebugWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		self.intended_y	= self.intended_x = 0
		self.intended_width		= self.getScreenMaxX()
		self.intended_height	= self.getScreenMaxY() - 5

		self.is_open = False

		self.debug_text = ""
		self.add_count = 0

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

		self.log("Manager Objects:")
		self.log("---------------")
		objects = list(self.manager.objects.keys())
		for obj in objects:
			self.log(f"  {obj}")
		self.log("---------------")

		if window_max_y - 1 < 1:
			return
		self.window.addnstr(0, 1, " DEBUG (Press F12 to dismiss Debug window) ", window_max_x - 2, self.manager.curses.color_pair(0) | self.manager.curses.A_REVERSE)

		lines = self.debug_text.split("\n")
		lines.reverse()
		for line in lines:
			if window_y >= window_max_y - 1:
				break
			self.window.addnstr(window_y, 1, line, window_max_x - 2, self.manager.curses.color_pair(0))
			window_y += 1

	def log(self, data):
		self.add_count += 1
		count_text = f"{self.add_count}: ".rjust(5)
		self.debug_text += f"\nDEBUG MSG " + count_text + str(data)

	def toggle(self):
		if self.is_open:
			self.is_open = False
			self.panel.hide()
		else:
			self.is_open = True
			self.panel.show()

	def terminate(self):
		pass
