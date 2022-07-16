import string

from modules.window import Window
class WindowBar(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		
		## FileWindow instance MagicBar is attached to.
		self.file_window = self.manager.get("current_file_window")
		
		self.config = self.manager.get("config").options

		self.panel.top()

	def update(self):
		self.file_window = self.manager.get("current_file_window")
		self.save_string = self.file_window.file.source

		self.cursor = self.file_window.filecursor

		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= self.getStdscrMaxY()
		self.intended_width		= self.getStdscrMaxX() - 1
		self.intended_height	= 1

		self.keepWindowInMainScreen()
		self.manager.update()
		self.keepWindowInMainScreen()

		idle_string = "    "
		highlight_x_start = 0
		highlight_x_len = 0
		for file_window in self.manager.get("file_window_list"):
			if file_window == self.file_window:
				if len(idle_string) + len(file_window.file.source) + 2 >= self.getWindowMaxX() - 1:
					idle_string = "... "
				highlight_x_start = len(idle_string)
				idle_string += file_window.file.source
				highlight_x_len = len(idle_string) - highlight_x_start
				idle_string += "  "
			else:
				idle_string += file_window.file.source + "  "
		idle_string += "  "

		if len(idle_string) - 2 >= self.getWindowMaxX() - 1:
			idle_string = idle_string[:self.getWindowMaxX() - 4] + "..."

		self.window.addnstr(0, 0, idle_string, self.getWindowMaxX() - 1, self.manager.curses.A_REVERSE)
		self.window.chgat(0, highlight_x_start, min(highlight_x_len, self.getWindowMaxX() - 1), self.manager.curses.color_pair(2) | self.manager.curses.A_REVERSE | self.manager.curses.A_BOLD)


		self.manager.update()

	def terminate(self):
		pass

