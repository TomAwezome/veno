# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class LineNumbersWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)

		## FileWindow instance that LineNumbersWindow is attached to.
		self.fileWindow = self.manager.Windows["fileWindow"]

		self.intendedY = self.fileWindow.getWindowBegY()
		self.intendedWidth = 5
		self.intendedX = self.fileWindow.getWindowBegX() - self.intendedWidth
		self.intendedHeight = self.fileWindow.getWindowMaxY()
		if self.intendedX < 0:
			self.intendedX = 0

		totalLines = len(self.fileWindow.fileLines)
		self.fileWindow.intendedX = len(str(totalLines)) + 1

		self.window.erase()
		self.keepWindowInMainScreen()
		self.fileWindow.panel.top()

	def update(self):
		self.window.erase()

		totalLines = len(self.fileWindow.fileLines)
		self.intendedWidth = len(str(totalLines)) + 2
		self.fileWindow.intendedX = len(str(totalLines)) + 1
		self.fileWindow.intendedWidth = self.getStdscrMaxX() - self.fileWindow.intendedX - 1
		self.fileWindow.keepWindowInMainScreen()
		self.intendedX = self.fileWindow.getWindowBegX() - self.intendedWidth + 1
		self.intendedHeight = self.fileWindow.getWindowMaxY()

		self.keepWindowInMainScreen()

		if self.intendedX >= 0:
			self.window.mvwin(self.intendedY, self.intendedX)
		else:
			self.window.mvwin(self.intendedY, 0)
			self.fileWindow.intendedX += 1
			self.fileWindow.keepWindowInMainScreen()

		windowY = 0
		currentLine = self.fileWindow.getViewportY()
		self.fileWindow.intendedX = len(str(totalLines)) + 1
		if self.intendedWidth <= self.getWindowMaxX():
			while windowY < self.getWindowMaxY() and windowY + currentLine < totalLines:
				lineNumberString = str(currentLine + windowY + 1)
				self.window.addstr(windowY, 0, lineNumberString + (" " * (len(str(totalLines)) - len(lineNumberString))) + "┃")
				windowY += 1

	def terminate(self):
 		pass
