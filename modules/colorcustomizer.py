# import time
# # file window covers everything about a file and seeing it visually
# # filecursor (current location in file), viewport? (what YOU're seeing), screenCursor (wherever you are has to visible _somehow_).

from modules.window import Window
class ColorCustomizerWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intendedY = 1
		self.intendedWidth = 40
		self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
		self.intendedHeight = 40
		if self.intendedX < 0:
			self.intendedX = 0
		self.isOpen = False
		#self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		self.window.erase()
		self.keepWindowInMainScreen()
		#self.manager.Windows["fileWindow"].panel.top()
		if self.isOpen == False:
			self.panel.hide()
		else:
			self.panel.top()
#		self.panel.hide()
		self.currentOption = 0
	def update(self):
		self.window.erase()
		#totalLines = len(self.manager.Windows["fileWindow"].fileLines)
		self.intendedWidth = len("Customize Highlight Colors")+2
		#self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		#self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		self.intendedX = int(self.manager.stdscr.getmaxyx()[1] / 2 - (self.intendedWidth / 2))
		self.intendedHeight = 19
		self.keepWindowInMainScreen()
		if self.intendedX >= 0:
			self.window.mvwin(self.intendedY, self.intendedX)
		else:
			self.window.mvwin(self.intendedY,0)
			#self.manager.Windows["fileWindow"].intendedX += 1
			#self.manager.Windows["fileWindow"].keepWindowInMainScreen()
		#windowY = 0
		#currentLine = self.manager.Windows["fileWindow"].viewport[1]
#		if self.intendedX >= 0:
		self.window.box()
		if self.isOpen == False:
			if self.panel.hidden == False:
				self.panel.hide()
		else:
			self.panel.top()
			self.window.addnstr(1,1,"Customize Highlight Colors", self.window.getmaxyx()[1]-1, self.manager.curses.color_pair(0))
			for color in self.manager.Objects["config"].options["ColorMap"]:
				self.window.addnstr(2+int(color),6,str(self.manager.Objects["config"].options["ColorMap"][color]),self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(int(self.manager.Objects["config"].options["ColorMap"][color])))
				self.window.addnstr(2+int(color),1,color,self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(0))
#				self.window.addnstr()
				if self.currentOption == int(color):
					self.window.chgat(2+int(color),1,1,self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
			self.manager.update()
			while True:
				try:
					c = self.manager.stdscr.getch()
				except KeyboardInterrupt:
					self.toggle()
					self.panel.hide()
					break
				if c == -1:
					continue
				c = self.manager.curses.keyname(c)
				c = c.decode("utf-8")
				if c == "KEY_LEFT":
					if self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] > 0:
						self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] -= 1
				if c == "KEY_RIGHT":
					self.manager.Objects["config"].options["ColorMap"][str(self.currentOption)] += 1
				if c == "KEY_UP":
					if self.currentOption > 0:
						self.currentOption -= 1
				if c == "KEY_DOWN":
					if self.currentOption < len(self.manager.Objects["config"].options["ColorMap"])-1: 
						self.currentOption += 1
				if c == "^_":
					self.toggle()
					self.panel.hide()
					break
				for color in self.manager.Objects["config"].options["ColorMap"]:
					self.window.addnstr(2+int(color),6,str(self.manager.Objects["config"].options["ColorMap"][color]),self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(int(self.manager.Objects["config"].options["ColorMap"][color])))
					self.window.addnstr(2+int(color),1,color,self.window.getmaxyx()[1]-1,self.manager.curses.color_pair(0))
					if self.currentOption == int(color):
						self.window.chgat(2+int(color),1,1,self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)
				self.manager.Objects["highlighter"].update()
				self.manager.update()
			self.manager.Objects["config"].save()
			self.manager.update()

		#self.panel.top()
		#self.manager.Windows["fileWindow"].intendedX = len(str(len(self.manager.Windows["fileWindow"].fileLines)))+1
		#while windowY < self.window.getmaxyx()[0] and windowY+currentLine < totalLines:
			#self.window.addstr(windowY,0,str(currentLine+windowY+1)+(" "*(len(str(totalLines))-len(str(currentLine+windowY+1))))+"┃")
			#windowY += 1
		# self.manager.Windows["fileWindow"].update()
		# self.manager.Windows["fileWindow"].panel.top()
		# self.manager.update()
	def toggle(self):
		if self.isOpen == True:
			self.isOpen = False
		else:
			self.isOpen = True
	def terminate(self):
		pass

























