import curses
import curses.panel as panel

##
## @brief      Class for managing global program objects, window panel instances, and ncurses screen.
##             New window panels are created on top of the base ncurses panel object.
##
class Manager:
	##
	## @brief      Constructs this Manager object.
	##
	## @param      self  This object
	##
	def __init__(self):
		## panel manager has curses. 
		self.curses = curses
		## screen variable
		self.screen = curses.initscr()
		## main panel object everything else goes on.
		self.panel = panel
		## Dictionary of global objects
		self.objects = {}

		curses.start_color()
		curses.use_default_colors()
		for i in range(0,curses.COLORS):
			curses.init_pair(i + 1, i, -1)
		curses.noecho()
		curses.cbreak()
		self.screen.keypad(True)
		curses.curs_set(0)
		self.screen.timeout(30)
	##
	## @brief      Update Panel Manager
	##
	## @param      self  This object
	##
	def update(self):
		self.panel.update_panels()
		self.screen.refresh()

	##
	## @brief      Terminate Manager
	##
	## @param      self  This object
	##
	def terminate(self):
		self.curses.nocbreak()
		self.screen.keypad(False)
		self.curses.echo()
		self.curses.endwin()
		
	##
	## @brief      Adds a panel.
	##
	## @param      self    This object
	## @param      Window  source Window object
	## @param      name    name of panel to be used in dictionary as key
	##
	def addPanel(self, Window, name):
		new_panel = self.panel.new_panel(Window.window)
		self.add(name, Window)
		return new_panel

	##
	## @brief      Get an object.
	##
	## @param      self    This object
	## @param      name    Name of the object to get.
	##
	def get(self, name):
		if name in self.objects:
			return self.objects[name]
		else:
			return None
			
	##
	## @brief      Add an object to the manager.
	##
	## @param      self    This object
	## @param      name    Name of the object to add.
	## @param      obj     The object to add
	##
	def add(self, name, obj):
		self.objects[name] = obj
		return obj
