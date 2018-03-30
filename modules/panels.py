class Manager:	# has .stdscr, .panel, ..think main WindowPanel for everything, other panels created on this
	def __init__(self):
		import curses #		panel manager has curses. 
		self.curses = curses
		import curses.panel as panel
		stdscr = curses.initscr()
		self.stdscr = stdscr
		self.panel = panel #main panel object everything else goes on.
		self.Windows = {}
		curses.start_color()
		curses.use_default_colors()
		for i in range(0,curses.COLORS):
			curses.init_pair(i+1,i,-1)
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(True)
		curses.curs_set(0)
	def update(self):
		self.panel.update_panels()
		self.stdscr.refresh()
	def addPanel(self, Window, name):
		newPanel = self.panel.new_panel(Window.window)
		self.Windows[name] = Window
		return newPanel
	def terminate(self):
		self.curses.nocbreak()
		self.stdscr.keypad(False)
		self.curses.echo()
		self.curses.endwin()