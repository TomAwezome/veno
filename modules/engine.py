import argparse # load arg parser module for file input
import importlib
import inspect
import curses
import curses.panel as panel

## List of modules to NOT call __init__ during module import, and NOT call terminate() during program shutdown.
## These modules will only globally store class definition, without creating instances.
MODULE_INIT_EXCLUDES = ["file", "filewindow"]

## List of modules to import.
## Unless specified in the excludes list, imported module's class __init__ is called to create global module instances.
MODULE_IMPORT_ORDER = [
	"config",
	"file",
	"filewindow",
	"filewindowmanager",
	"syntaxhighlighting",
#	"windowbar",
	"linenumbers",
#	"configcustomizer",
#	"linejumpbar",
#	"savebar",
#	"searchbar",
	"debugwindow",
#	"openbar",
	"helpwindow",
#	"diffwindow",
	"keybindings",
]

# List of modules to call update() method on each Engine.turn().
MODULE_UPDATE_ORDER = [
	"keybindings",
#	"windowbar",
#	"linejumpbar",
#	"savebar",
#	"searchbar",
	"filewindowmanager",
	"linenumbers",
	"syntaxhighlighting",
#	"configcustomizer",
#	"openbar",
	"debugwindow",
	"helpwindow",
#	"diffwindow",
]

##
## @brief      Veno Engine Class. Built to be easily and swiftly customized.
##
class Engine():
	##
	## @brief      Constructs this Engine object.
	##
	## @param      self  This object
	##
	def __init__(self):
		self.curses = curses

		## screen variable
		self.screen = curses.initscr()
		## main panel object everything else goes on.
		self.panel = panel

		curses.start_color()
		curses.use_default_colors()
		for i in range(0,curses.COLORS):
			curses.init_pair(i + 1, i, -1)
		curses.noecho()
		curses.cbreak()
		self.screen.keypad(True)
		curses.curs_set(0)
		self.screen.timeout(30)

		self.filenames = self.parseArgs().filename or ["untitled.txt"]

		## Dictionary of global objects
		self.global_objects = {}

		self.module_list = []
		self.module_classes  = {}
		self.module_instances = {}
		for module_name in MODULE_IMPORT_ORDER:
			m = importlib.import_module("modules." + module_name)
			self.module_list.append(m)
			self.module_classes[module_name] = class_tuple = inspect.getmembers(m, inspect.isclass)[0]
			if module_name not in MODULE_INIT_EXCLUDES:
				self.module_instances[module_name] = obj = class_tuple[1](self) # call imported module class's __init__ with Engine as arg
				self.set(module_name, obj)
			else:
				self.set(class_tuple[1].__name__, class_tuple[1]) # put module class definition into global objects dictionary with module class name as key

		self.exception = Exception

	##
	## @brief      Turn the engine once.
	##
	## @param      self  This object
	##
	def turn(self):
		for module_name in MODULE_UPDATE_ORDER:
			self.module_instances[module_name].update()
		self.update()

	##
	## @brief      Update curses panels
	##
	## @param      self  This object
	##
	def update(self):
		self.panel.update_panels()
		self.screen.refresh()

	def setException(self, e):
		self.exception = e
		self.set("EngineException", e)

	##
	## @brief      Parses arguments given via command line
	##
	## @param      self  This object
	##
	def parseArgs(self):														# 
		parser = argparse.ArgumentParser()										#
		parser.add_argument("filename", nargs='*')								# create program parameter, filename/path
		return parser.parse_args()												#

	##
	## @brief      Get an object.
	##
	## @param      self    This object
	## @param      name    Name of the object to get.
	##
	def get(self, name):
		if name in self.global_objects:
			return self.global_objects[name]
		return None

	##
	## @brief      Set an object key/value pair in the engine object dictionary.
	##
	## @param      self    This object
	## @param      name    Name (key) of the object
	## @param      obj     The object (value) to add
	##
	def set(self, name, obj):
		if name == "" or name is None:
			return None
		self.global_objects[name] = obj
		return obj

	##
	## @brief      Adds a panel.
	##
	## @param      self    This object
	## @param      window  source Window object (window.py)
	##
	def addPanel(self, window):
		return self.panel.new_panel(window.window)

	##
	## @brief      terminate engine
	##
	## @param      self  This object
	##
	def terminate(self):														# Terminate all modules in reverse order of initialization.
		self.curses.nocbreak()
		self.screen.keypad(False)
		self.curses.echo()
		self.curses.endwin()
		MODULE_IMPORT_ORDER.reverse()
		for module_name in MODULE_IMPORT_ORDER:
			if module_name not in MODULE_INIT_EXCLUDES:
				self.module_instances[module_name].terminate()

