# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class LineNumbersWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intendedY = self.manager.Windows["fileWindow"].window.getbegyx()[0]
		self.intendedWidth = 5
		self.intendedX = self.manager.Windows["fileWindow"].window.getbegyx()[1] - self.intendedWidth
		self.intendedHeight = self.manager.Windows["fileWindow"].window.getmaxyx()[0]
		if self.intendedX < 0:
			self.intendedX = 0
		self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		self.window.erase()
		self.keepWindowInMainScreen()
		self.manager.Windows["fileWindow"].panel.top()
	def update(self):
		self.window.erase()
		totalLines = len(self.manager.Windows["fileWindow"].fileLines)
		self.intendedWidth = len(str(totalLines))+2
		self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		self.manager.Windows["fileWindow"].intendedWidth = self.manager.stdscr.getmaxyx()[1] - self.manager.Windows["fileWindow"].intendedX - 1
		self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		self.intendedX = self.manager.Windows["fileWindow"].window.getbegyx()[1] - self.intendedWidth+1
		self.intendedHeight = self.manager.Windows["fileWindow"].window.getmaxyx()[0]
		self.keepWindowInMainScreen()
		if self.intendedX >= 0:
			self.window.mvwin(self.intendedY, self.intendedX)
		else:
			self.window.mvwin(self.intendedY,0)
			self.manager.Windows["fileWindow"].intendedX += 1
			self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		windowY = 0
		currentLine = self.manager.Windows["fileWindow"].viewport[1]
		self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		while windowY < self.window.getmaxyx()[0] and windowY+currentLine < totalLines:
			self.window.addstr(windowY,0,str(currentLine+windowY+1)+(" "*(len(str(totalLines))-len(str(currentLine+windowY+1))))+"┃")
			windowY += 1
	def terminate(self):
 		pass
