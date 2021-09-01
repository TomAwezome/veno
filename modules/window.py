class Window:
	def __init__(self, manager, name):
		self.manager = manager
		self.name = name
		self.intended_x			= 0 #  
		self.intended_y			= 0 # default
		self.intended_width		= 1 # values
		self.intended_height	= 1	# 
		self.window = manager.curses.newwin(self.intended_height, self.intended_width, self.intended_y, self.intended_x)
		self.window.erase()
		self.keepWindowInMainScreen()
		self.panel = self.manager.addPanel(self, self.name)

	def update(self):
		self.window.erase()
		self.keepWindowInMainScreen()
		self.window.box()

	def terminate(self):
		pass

	def getWindowMaxY(self):
		return self.window.getmaxyx()[0]

	def getWindowMaxX(self):
		return self.window.getmaxyx()[1]

	def getWindowBegY(self):
		return self.window.getbegyx()[0]

	def getWindowBegX(self):
		return self.window.getbegyx()[1]

	def getStdscrMaxY(self):
		return self.manager.stdscr.getmaxyx()[0]
		
	def getStdscrMaxX(self):
		return self.manager.stdscr.getmaxyx()[1]

	def getStdscrBegY(self):
		return self.manager.stdscr.getbegyx()[0]
		
	def getStdscrBegX(self):
		return self.manager.stdscr.getbegyx()[1]

	def keepWindowInMainScreen(self):
		offscreen_y = 0
		offscreen_x = 0
		is_offscreen = False
		is_window_altered = False
		stdscr_max_x = self.manager.stdscr.getmaxyx()[1]
		stdscr_max_y = self.manager.stdscr.getmaxyx()[0]

		# if actual window does not fit in main screen
		if stdscr_max_y <= self.getWindowMaxY() + self.getWindowBegY():
		# if screen size self.intended_x does not fit the window self.intended_x
			is_offscreen = True
			offscreen_y = self.getWindowBegY() + self.getWindowMaxY() - stdscr_max_y
			if self.getWindowBegY() - offscreen_y < 0:
				self.window.resize(self.getWindowMaxY() + (self.getWindowBegY() - offscreen_y), self.getWindowMaxX())
				is_window_altered = True
				offscreen_y = self.getWindowBegY() + self.getWindowMaxY() - stdscr_max_y

		if stdscr_max_x <= self.getWindowMaxX() + self.getWindowBegX():
			is_offscreen = True
			offscreen_x = self.getWindowBegX() + self.getWindowMaxX() - stdscr_max_x
			if self.getWindowBegX() - offscreen_x < 0:
				self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() + (self.getWindowBegX() - offscreen_x))
				is_window_altered = True
				offscreen_x = self.getWindowBegX() + self.getWindowMaxX() - stdscr_max_x

		if is_offscreen:
			self.window.mvwin(self.getWindowBegY() - offscreen_y, self.getWindowBegX() - offscreen_x)
			is_window_altered = True

		if stdscr_max_y == self.getWindowMaxY():
			if self.getWindowMaxY() - 1 <= 0:
				self.window.resize(1, self.getWindowMaxX())
			else:
				self.window.resize(self.getWindowMaxY() - 1, self.getWindowMaxX())
			is_window_altered = True

		if stdscr_max_x == self.getWindowMaxX():
			if self.getWindowMaxX() - 1 <= 0:
				self.window.resize(self.getWindowMaxY(), 1)
			else:
				self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() - 1)
			is_window_altered = True

		# if there is space available to resize window closer to intended dimensions
		if self.intended_height > self.getWindowMaxY() and stdscr_max_y > self.getWindowMaxY() + self.getWindowBegY():
			self.window.resize(self.getWindowMaxY() + (stdscr_max_y - self.getWindowMaxY()), self.getWindowMaxX())
			is_window_altered = True

		if self.getWindowMaxY() > self.intended_height:
			if self.intended_height <= 0:
				self.intended_height = 1
			self.window.resize(self.intended_height, self.getWindowMaxX())
			is_window_altered = True

		if self.intended_width > self.getWindowMaxX() and stdscr_max_x > self.getWindowMaxX() + self.getWindowBegX():
			self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() + (stdscr_max_x - self.getWindowMaxX()))
			is_window_altered = True

		if self.getWindowMaxX() > self.intended_width:
			if self.intended_width <= 0:
				self.intended_width = 1
			self.window.resize(self.getWindowMaxY(), self.intended_width)
			is_window_altered = True

		# if window can be moved closer to intended position
		if self.intended_y > self.getWindowBegY() and stdscr_max_y > self.getWindowMaxY():
			if stdscr_max_y > self.intended_y + self.getWindowMaxY():
				self.window.mvwin(self.intended_y, self.getWindowBegX())
				is_window_altered = True
			elif self.intended_y + self.getWindowMaxY() > stdscr_max_y:
				self.window.mvwin(stdscr_max_y - self.getWindowMaxY(), self.getWindowBegX())
				is_window_altered = True

		if self.intended_x > self.getWindowBegX() and stdscr_max_x > self.getWindowMaxX():
			if stdscr_max_x > self.intended_x + self.getWindowMaxX():
				self.window.mvwin(self.getWindowBegY(), self.intended_x)
				is_window_altered = True
			elif self.intended_x + self.getWindowMaxX() > stdscr_max_x:
				self.window.mvwin(self.getWindowBegY(), stdscr_max_x - self.getWindowMaxX())
				is_window_altered = True

		change_x = self.getWindowBegX()
		change_y = self.getWindowBegY()
		if self.intended_x < self.getWindowBegX() and self.intended_x > 0:
			change_x = self.intended_x

		if self.intended_y < self.getWindowBegY() and self.intended_y > 0:
			change_y = self.intended_y

		if change_x != self.getWindowBegX() or change_y != self.getWindowBegY():
			self.window.mvwin(change_y, change_x)
			is_window_altered = True

		if is_window_altered:
			self.manager.stdscr.erase()
