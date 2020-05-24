# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class LineNumbersWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intendedY = self.manager.Windows["fileWindow"].getWindowBegY()
		self.intendedWidth = 5
		self.intendedX = self.manager.Windows["fileWindow"].getWindowBegX() - self.intendedWidth
		self.intendedHeight = self.manager.Windows["fileWindow"].getWindowMaxY()
		if self.intendedX < 0:
			self.intendedX = 0
		totalLines = len(self.manager.Windows["fileWindow"].fileLines)
		self.manager.Windows["fileWindow"].intendedX = len(str(totalLines)) + 1
		self.window.erase()
		self.keepWindowInMainScreen()
		self.manager.Windows["fileWindow"].panel.top()
	def update(self):
		self.window.erase()
		totalLines = len(self.manager.Windows["fileWindow"].fileLines)
		self.intendedWidth = len(str(totalLines)) + 2
		self.manager.Windows["fileWindow"].intendedX = len(str(totalLines)) + 1
		self.manager.Windows["fileWindow"].intendedWidth = self.getStdscrMaxX() - self.manager.Windows["fileWindow"].intendedX - 1
		self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		self.intendedX = self.manager.Windows["fileWindow"].getWindowBegX() - self.intendedWidth + 1
		self.intendedHeight = self.manager.Windows["fileWindow"].getWindowMaxY()
		self.keepWindowInMainScreen()
		if self.intendedX >= 0:
			self.window.mvwin(self.intendedY, self.intendedX)
		else:
			self.window.mvwin(self.intendedY, 0)
			self.manager.Windows["fileWindow"].intendedX += 1
			self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		windowY = 0
		currentLine = self.manager.Windows["fileWindow"].getViewportY()
		self.manager.Windows["fileWindow"].intendedX = len(str(totalLines)) + 1
		if self.intendedWidth <= self.getWindowMaxX():
			while windowY < self.getWindowMaxY() and windowY + currentLine < totalLines:
				self.window.addstr(windowY, 0, str(currentLine + windowY + 1) + (" " * (len(str(totalLines)) - len(str(currentLine + windowY + 1)))) + "┃")
				windowY += 1
	def terminate(self):
 		pass
