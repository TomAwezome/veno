from modules.window import Window
class LineNumbersWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		## FileWindow instance that LineNumbersWindow is attached to.
		self.file_window = self.manager.get("current_file_window")

		self.intended_y			= self.file_window.getWindowBegY()
		self.intended_width		= 5
		self.intended_x			= self.file_window.getWindowBegX() - self.intended_width
		self.intended_height	= self.file_window.getWindowMaxY()
		if self.intended_x < 0:
			self.intended_x = 0

		total_lines = len(self.file_window.file_lines)
		self.file_window.intended_x = len(str(total_lines)) + 1

		self.window.erase()
		self.keepWindowInMainScreen()
		self.file_window.panel.top()

	def update(self):
		self.window.erase()

		self.file_window = self.manager.get("current_file_window")
		
		if not self.manager.get("config").options["ShowLineNumbers"]:
			self.file_window.intended_x	= 0
			self.file_window.window.mvwin(self.file_window.intended_y, self.file_window.intended_x)
			self.file_window.keepWindowInMainScreen()
			return

		total_lines = len(self.file_window.file_lines)
		self.intended_width = len(str(total_lines)) + 2

		self.file_window.intended_x		= len(str(total_lines)) + 1
		self.file_window.intended_width	= self.getScreenMaxX() - self.file_window.intended_x - 1
		self.file_window.keepWindowInMainScreen()

		self.intended_x			= self.file_window.getWindowBegX() - self.intended_width + 1
		self.intended_height	= self.file_window.getWindowMaxY()
		self.keepWindowInMainScreen()

		if self.intended_x >= 0:
			self.window.mvwin(self.intended_y, self.intended_x)
		else:
			self.window.mvwin(self.intended_y, 0)
			self.file_window.intended_x += 1
			self.file_window.keepWindowInMainScreen()

		window_y = 0
		current_line = self.file_window.getViewportY()
		self.file_window.intended_x = len(str(total_lines)) + 1
		if self.intended_width <= self.getWindowMaxX():
			while window_y < self.getWindowMaxY() and window_y + current_line < total_lines:
				line_number_string = str(current_line + window_y + 1)
				self.window.addstr(window_y, 0, line_number_string + (" " * (len(str(total_lines)) - len(line_number_string))) + " ", self.manager.curses.A_REVERSE)
				window_y += 1

	def terminate(self):
 		pass
