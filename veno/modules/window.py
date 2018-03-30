class Window:
	def __init__(self, manager, name):
		self.manager = manager
		self.name = name
		self.intendedX = 0 			#<-- 
		self.intendedY = 0			#<-- just some
		self.intendedWidth = 1		#<-- default values
		self.intendedHeight = 1	#<--
		self.window = manager.curses.newwin(self.intendedHeight, self.intendedWidth, self.intendedY, self.intendedX)
		self.window.erase()
		self.keepWindowInMainScreen()
		self.panel = self.manager.addPanel(self, self.name)
		#self.panel.top()
	def update(self):
		self.window.erase()
		self.keepWindowInMainScreen()
		self.window.box()
	def terminate(self):
		pass
	def keepWindowInMainScreen(self):
		offscreenY = 0
		offscreenX = 0
		offscreen = False
		windowAltered = False
		# if actual window does not fit in main screen
		if self.manager.stdscr.getmaxyx()[0] <= self.window.getmaxyx()[0] + self.window.getbegyx()[0]:	# if screen size self.intendedX does not fit the window self.intendedX
			offscreen = True
			offscreenY = self.window.getbegyx()[0]+self.window.getmaxyx()[0]-self.manager.stdscr.getmaxyx()[0]
			if self.window.getbegyx()[0]-offscreenY < 0:
				self.window.resize(self.window.getmaxyx()[0]+(self.window.getbegyx()[0]-offscreenY),self.window.getmaxyx()[1])
				windowAltered = True
				offscreenY = self.window.getbegyx()[0]+self.window.getmaxyx()[0]-self.manager.stdscr.getmaxyx()[0]
		if self.manager.stdscr.getmaxyx()[1] <= self.window.getmaxyx()[1] + self.window.getbegyx()[1]:
			offscreen = True
			offscreenX = self.window.getbegyx()[1]+self.window.getmaxyx()[1]-self.manager.stdscr.getmaxyx()[1]
			if self.window.getbegyx()[1]-offscreenX < 0:
				self.window.resize(self.window.getmaxyx()[0],self.window.getmaxyx()[1]+(self.window.getbegyx()[1]-offscreenX))
				windowAltered = True
				offscreenX = self.window.getbegyx()[1]+self.window.getmaxyx()[1]-self.manager.stdscr.getmaxyx()[1]
		if offscreen:
			self.window.mvwin(self.window.getbegyx()[0]-offscreenY,self.window.getbegyx()[1]-offscreenX)
			windowAltered = True
		if self.manager.stdscr.getmaxyx()[0] == self.window.getmaxyx()[0]:
			if self.window.getmaxyx()[0]-1 <= 0:
				self.window.resize(1,self.window.getmaxyx()[1])
			else:
				self.window.resize(self.window.getmaxyx()[0]-1,self.window.getmaxyx()[1])
			windowAltered = True
		if self.manager.stdscr.getmaxyx()[1] == self.window.getmaxyx()[1]:
			if self.window.getmaxyx()[1]-1 <= 0:
				self.window.resize(self.window.getmaxyx()[0], 1)
			else:
				self.window.resize(self.window.getmaxyx()[0], self.window.getmaxyx()[1]-1)
			windowAltered = True
		# if there is space available to resize window closer to intended dimensions
		if self.intendedHeight > self.window.getmaxyx()[0] and self.manager.stdscr.getmaxyx()[0] > self.window.getmaxyx()[0]+self.window.getbegyx()[0]:
			self.window.resize(self.window.getmaxyx()[0]+(self.manager.stdscr.getmaxyx()[0]-self.window.getmaxyx()[0]),self.window.getmaxyx()[1])
			windowAltered = True
		if self.window.getmaxyx()[0] > self.intendedHeight:
			if self.intendedHeight <= 0:
				self.intendedHeight = 1
			self.window.resize(self.intendedHeight,self.window.getmaxyx()[1])
			windowAltered = True
		if self.intendedWidth > self.window.getmaxyx()[1] and self.manager.stdscr.getmaxyx()[1] > self.window.getmaxyx()[1]+self.window.getbegyx()[1]:
			self.window.resize(self.window.getmaxyx()[0],self.window.getmaxyx()[1]+(self.manager.stdscr.getmaxyx()[1]-self.window.getmaxyx()[1]))
			windowAltered = True
		if self.window.getmaxyx()[1] > self.intendedWidth:
			if self.intendedWidth <= 0:
				self.intendedWidth = 1
			self.window.resize(self.window.getmaxyx()[0],self.intendedWidth)
			windowAltered = True
		# if window can be moved closer to intended position
		if self.intendedY > self.window.getbegyx()[0] and self.manager.stdscr.getmaxyx()[0] > self.window.getmaxyx()[0]:
			if self.manager.stdscr.getmaxyx()[0] > self.intendedY+self.window.getmaxyx()[0]:
				self.window.mvwin(self.intendedY,self.window.getbegyx()[1])
				windowAltered = True
			elif self.intendedY+self.window.getmaxyx()[0] > self.manager.stdscr.getmaxyx()[0]:
				self.window.mvwin(self.manager.stdscr.getmaxyx()[0]-self.window.getmaxyx()[0],self.window.getbegyx()[1])
				windowAltered = True
		if self.intendedX > self.window.getbegyx()[1] and self.manager.stdscr.getmaxyx()[1] > self.window.getmaxyx()[1]:
			if self.manager.stdscr.getmaxyx()[1] > self.intendedX+self.window.getmaxyx()[1]:
				self.window.mvwin(self.window.getbegyx()[0],self.intendedX)
				windowAltered = True
			elif self.intendedX+self.window.getmaxyx()[1] > self.manager.stdscr.getmaxyx()[1]:
				self.window.mvwin(self.window.getbegyx()[0],self.manager.stdscr.getmaxyx()[1]-self.window.getmaxyx()[1])
				windowAltered = True
		changeX = self.window.getbegyx()[1]
		changeY = self.window.getbegyx()[0]
		if self.intendedX < self.window.getbegyx()[1] and self.intendedX > 0:
			changeX = self.intendedX
		if self.intendedY < self.window.getbegyx()[0] and self.intendedY > 0:
			changeY = self.intendedY
		if changeX != self.window.getbegyx()[1] or changeY != self.window.getbegyx()[0]:
			self.window.mvwin(changeY, changeX)
			windowAltered = True
		if windowAltered:
			self.manager.stdscr.erase()