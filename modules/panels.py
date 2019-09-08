##
## @brief      Class for manager. has .stdscr, .panel, ..think main WindowPanel for everything, other panels created on this
##
class Manager:
	##
	## @brief      Constructs the object.
	##
	## @param      self  The object
	##
	def __init__(self):
		import curses
		## panel manager has curses. 
		self.curses = curses
		import curses.panel as panel
		stdscr = curses.initscr()
		## screen variable
		self.stdscr = stdscr
		## main panel object everything else goes on.
		self.panel = panel
		## Dictionary of Window instances
		self.Windows = {}
		self.Objects = {}
		curses.start_color()
		curses.use_default_colors()
		for i in range(0,curses.COLORS):
			curses.init_pair(i+1,i,-1)
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(True)
		curses.curs_set(0)
		stdscr.timeout(30)
	##
	## @brief      Update Panel Manager
	##
	## @param      self  The object
	##
	def update(self):
		self.panel.update_panels()
		self.stdscr.refresh()
	##
	## @brief      Adds a panel.
	##
	## @param      self    The object
	## @param      Window  source Window object
	## @param      name    name of panel to be used in dictionary as key
	##
	def addPanel(self, Window, name):
		newPanel = self.panel.new_panel(Window.window)
		self.Windows[name] = Window
		return newPanel
	##
	## @brief      Terminate Manager
	##
	## @param      self  The object
	##
	def terminate(self):
		self.curses.nocbreak()
		self.stdscr.keypad(False)
		self.curses.echo()
		self.curses.endwin()
