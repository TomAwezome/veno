import argparse # load arg parser module for file input
import importlib
import inspect
import curses
import curses.panel as panel
import traceback

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
	"windowbar",
	"linenumbers",
	"configcustomizer",
	"linejumpbar",
	"diffwindow",
	"savebar",
	"searchbar",
	"debugwindow",
	"openbar",
	"helpwindow",
	"keybindings",
]

# List of modules to call update() method on each Engine.turn().
MODULE_UPDATE_ORDER = [
	"keybindings",
	"config",
	"windowbar",
	"linejumpbar",
	"savebar",
	"searchbar",
	"filewindowmanager",
	"linenumbers",
	"syntaxhighlighting",
	"configcustomizer",
	"openbar",
	"debugwindow",
	"helpwindow",
	"diffwindow",
]

MODULE_CLASSES = {
	"config": "Config",
	"file": "File",
	"filewindow": "FileWindow",
	"filewindowmanager": "FileWindowManager",
	"syntaxhighlighting": "Highlighter",
	"windowbar": "WindowBar",
	"linenumbers": "LineNumbersWindow",
	"configcustomizer": "ConfigCustomizerWindow",
	"linejumpbar": "LineJumpBar",
	"savebar": "SaveBar",
	"searchbar": "SearchBar",
	"debugwindow": "DebugWindow",
	"openbar": "OpenBar",
	"helpwindow": "HelpWindow",
	"diffwindow": "DiffWindow",
	"keybindings": "Keyboard",
}

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
		for module_name in [name for name in MODULE_IMPORT_ORDER if importlib.util.find_spec("modules." + name) == None]:
			self.errorPrompt(f"[{module_name}] in 'import' list: FILE NOT FOUND.", "import", module_name)
		for module_name in [name for name in MODULE_UPDATE_ORDER if name not in MODULE_IMPORT_ORDER]:
			self.errorPrompt(f"[{module_name}] in 'update' list: NOT FOUND in 'import' list.", "update", module_name)
		for module_name in [name for name in MODULE_IMPORT_ORDER if name not in MODULE_CLASSES]:
			self.errorPrompt(f"[{module_name}] in 'import' list: NO VALUE in 'module class' dictionary.", "import", module_name)

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
			try:
				m = importlib.import_module("modules." + module_name)
			except:
				self.panic(f"[{module_name}] in 'import' list: ERROR during import.")
			self.module_list.append(m)
			module_class_name = MODULE_CLASSES[module_name]
			class_definition = ([c for n, c in inspect.getmembers(m, inspect.isclass) if n == module_class_name] or [None])[0]
			if class_definition == None:
				self.panic(f"[{module_name}] in 'import' list: class <{module_class_name}> NOT FOUND.\n"
					"Possible typo? Check MODULE_CLASSES in engine.py, and check {module_name}.py", False)
			self.module_classes[module_name] = (module_class_name, class_definition)
			if module_name not in MODULE_INIT_EXCLUDES:
				class_function_name_list = [n for n, f in inspect.getmembers(class_definition, inspect.isfunction)]
				if "terminate" not in class_function_name_list:
					self.panic(f"[{module_name}] in 'import' list: {module_class_name}.terminate() function NOT FOUND.", False)
				if module_name in MODULE_UPDATE_ORDER and "update" not in class_function_name_list:
					self.panic(f"[{module_name}] in 'import' list: {module_class_name}.update() function NOT FOUND.", False)
				try:
					self.module_instances[module_name] = class_instance = class_definition(self) # call imported module class's __init__ with Engine as arg
				except:
					self.panic(f"[{module_name}] in 'import' list: ERROR during initialization.")

				self.set(module_name, class_instance)
			else:
				self.set(module_class_name, class_definition) # put module class definition into global objects dictionary with module class name as key

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

	def errorPrompt(self, prompt, list_name, module_name):
		response = ""
		prompt = "\n" + str(prompt) + f"\nRemove from '{list_name}' list for this launch? (y/n) "
		while response != "y" and response != "n":
			response = input(prompt)
		if response == "y":
			if list_name == "import":
				MODULE_IMPORT_ORDER.remove(module_name)
			elif list_name == "update":
				MODULE_UPDATE_ORDER.remove(module_name)
		else:
			exit(-1)

	def panic(self, prompt, is_exception=True):
		self.terminate()
		print("\n" + str(prompt) + "\n")
		if is_exception:
			highlight = self.get("pygments_func_highlight")
			if highlight is not None:
				lexer = self.get("pygments_pytb_lexer")
				formatter = self.get("pygments_term_formatter")
				trace_text = "".join(traceback.format_exc())
				trace = highlight(trace_text, lexer, formatter)
				print(trace)
			else:
				traceback.print_exc()  # Print the exception
		print("")
		exit(-1)

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
				if module_name in self.module_instances:
					self.module_instances[module_name].terminate()

