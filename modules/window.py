class Window:
	def __init__(self, manager, name):
		self.manager = manager
		self.name = name
		self.intendedX = 0 			#<-- 
		self.intendedY = 0			#<-- just some
		self.intendedWidth = 1		#<-- default values
		self.intendedHeight = 1		#<--
		self.window = manager.curses.newwin(self.intendedHeight, self.intendedWidth, self.intendedY, self.intendedX)
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

	def keepWindowInMainScreen(self):
		offscreenY = 0
		offscreenX = 0
		offscreen = False
		windowAltered = False
		stdscrMaxX = self.manager.stdscr.getmaxyx()[1]
		stdscrMaxY = self.manager.stdscr.getmaxyx()[0]

		# if actual window does not fit in main screen
		if stdscrMaxY <= self.getWindowMaxY() + self.getWindowBegY():	# if screen size self.intendedX does not fit the window self.intendedX
			offscreen = True
			offscreenY = self.getWindowBegY() + self.getWindowMaxY() - stdscrMaxY
			if self.getWindowBegY() - offscreenY < 0:
				self.window.resize(self.getWindowMaxY() + (self.getWindowBegY() - offscreenY), self.getWindowMaxX())
				windowAltered = True
				offscreenY = self.getWindowBegY() + self.getWindowMaxY() - stdscrMaxY

		if stdscrMaxX <= self.getWindowMaxX() + self.getWindowBegX():
			offscreen = True
			offscreenX = self.getWindowBegX() + self.getWindowMaxX() - stdscrMaxX
			if self.getWindowBegX() - offscreenX < 0:
				self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() + (self.getWindowBegX() - offscreenX))
				windowAltered = True
				offscreenX = self.getWindowBegX() + self.getWindowMaxX() - stdscrMaxX

		if offscreen:
			self.window.mvwin(self.getWindowBegY() - offscreenY, self.getWindowBegX() - offscreenX)
			windowAltered = True

		if stdscrMaxY == self.getWindowMaxY():
			if self.getWindowMaxY() - 1 <= 0:
				self.window.resize(1, self.getWindowMaxX())
			else:
				self.window.resize(self.getWindowMaxY() - 1, self.getWindowMaxX())
			windowAltered = True

		if stdscrMaxX == self.getWindowMaxX():
			if self.getWindowMaxX() - 1 <= 0:
				self.window.resize(self.getWindowMaxY(), 1)
			else:
				self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() - 1)
			windowAltered = True

		# if there is space available to resize window closer to intended dimensions
		if self.intendedHeight > self.getWindowMaxY() and stdscrMaxY > self.getWindowMaxY() + self.getWindowBegY():
			self.window.resize(self.getWindowMaxY() + (stdscrMaxY - self.getWindowMaxY()), self.getWindowMaxX())
			windowAltered = True

		if self.getWindowMaxY() > self.intendedHeight:
			if self.intendedHeight <= 0:
				self.intendedHeight = 1
			self.window.resize(self.intendedHeight, self.getWindowMaxX())
			windowAltered = True

		if self.intendedWidth > self.getWindowMaxX() and stdscrMaxX > self.getWindowMaxX() + self.getWindowBegX():
			self.window.resize(self.getWindowMaxY(), self.getWindowMaxX() + (stdscrMaxX - self.getWindowMaxX()))
			windowAltered = True

		if self.getWindowMaxX() > self.intendedWidth:
			if self.intendedWidth <= 0:
				self.intendedWidth = 1
			self.window.resize(self.getWindowMaxY(), self.intendedWidth)
			windowAltered = True

		# if window can be moved closer to intended position
		if self.intendedY > self.getWindowBegY() and stdscrMaxY > self.getWindowMaxY():
			if stdscrMaxY > self.intendedY + self.getWindowMaxY():
				self.window.mvwin(self.intendedY, self.getWindowBegX())
				windowAltered = True
			elif self.intendedY + self.getWindowMaxY() > stdscrMaxY:
				self.window.mvwin(stdscrMaxY - self.getWindowMaxY(), self.getWindowBegX())
				windowAltered = True

		if self.intendedX > self.getWindowBegX() and stdscrMaxX > self.getWindowMaxX():
			if stdscrMaxX > self.intendedX + self.getWindowMaxX():
				self.window.mvwin(self.getWindowBegY(), self.intendedX)
				windowAltered = True
			elif self.intendedX + self.getWindowMaxX() > stdscrMaxX:
				self.window.mvwin(self.getWindowBegY(), stdscrMaxX - self.getWindowMaxX())
				windowAltered = True

		changeX = self.getWindowBegX()
		changeY = self.getWindowBegY()
		if self.intendedX < self.getWindowBegX() and self.intendedX > 0:
			changeX = self.intendedX

		if self.intendedY < self.getWindowBegY() and self.intendedY > 0:
			changeY = self.intendedY

		if changeX != self.getWindowBegX() or changeY != self.getWindowBegY():
			self.window.mvwin(changeY, changeX)
			windowAltered = True

		if windowAltered:
			self.manager.stdscr.erase()
