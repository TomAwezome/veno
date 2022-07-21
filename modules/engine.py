import argparse # load arg parser module for file input

from modules.config import Config
from modules.file import File
from modules.manager import Manager
from modules.filewindow import FileWindow
from modules.keybindings import Keyboard
from modules.syntaxhighlighting import Highlighter
from modules.windowbar import WindowBar
from modules.linenumbers import LineNumbersWindow
from modules.configcustomizer import ConfigCustomizerWindow
from modules.linejumpbar import LineJumpBar
from modules.savebar import SaveBar
from modules.searchbar import SearchBar
from modules.debugwindow import DebugWindow
from modules.openbar import OpenBar
from modules.helpwindow import HelpWindow
from modules.diffwindow import DiffWindow

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
		filenames = self.parseArgs().filename or ["untitled.txt"]

		self.exception = Exception

		## Config instance for editor.
		self.config = Config(filenames[0])
		## File instance list to be used by editor.
		self.files = []
		## FileWindow instance list.
		self.file_window_list = []
		## Panel Manager instance for modules.
		self.manager = Manager()												# Load Manager.
		self.manager.set("config", self.config)
		self.manager.set("file_window_list", self.file_window_list)
		
		self.manager.set("File", File)
		self.manager.set("FileWindow", FileWindow)

		for filename in filenames:
			try:
				file = File(filename)
				self.files.append(file)											# Load file provided as only arg.
				file_window = FileWindow(self.manager, "", file)		# Create fileWindow.
				self.file_window_list.append(file_window)
				file_window.update()											# Update fileWindow contents.
			except IsADirectoryError:
				pass
		if self.file_window_list != []:
			self.manager.set("current_file_window", self.file_window_list[0])
		else: # filewindow list can be empty if provided arg is a directory and no other filename args are given
			file = File("untitled.txt")
			self.files.append(file)
			file_window = FileWindow(self.manager, "", file)
			self.file_window_list.append(file_window)
			file_window.update()
			self.manager.set("current_file_window", self.file_window_list[0])

		## Highlighter instance to colorize FileWindow contents.
		self.highlighter = Highlighter(self.manager)
		self.manager.set("highlighter", self.highlighter)
		## WindowBar Window instance to print list of windows in use by veno.
		self.window_bar = WindowBar(self.manager, "window_bar")
		## LineNumbers Window instance to display next to FileWindow.
		self.line_numbers = LineNumbersWindow(self.manager, "line_numbers")
		## ConfigCustomizer Window instance to allow modifying configuration.
		self.config_customizer = ConfigCustomizerWindow(self.manager, "config_customizer")
		## LineJumpBar Window instance to pop-up for prompting line number to jump to in current FileWindow.
		self.line_jump_bar = LineJumpBar(self.manager, "line_jump_bar")
		## SaveBar Window instance to pop-up for prompting save filename for current FileWindow.
		self.save_bar = SaveBar(self.manager, "save_bar")
		## SearchBar Window instance to pop-up for prompting find (and replace) text for current FileWindow.
		self.search_bar = SearchBar(self.manager, "search_bar")
		## DebugWindow instance to print debug information to.
		self.debug_window = DebugWindow(self.manager, "debug_window")
		## OpenBar Window instance to pop-up for prompting open filename for opening additional file.
		self.open_bar = OpenBar(self.manager, "open_bar")
		## HelpWindow instance to pop-up for displaying basic Help information.
		self.help_window = HelpWindow(self.manager, "help_window")
		## DiffWindow instance to pop-up for displaying diff of file on disk vs file in editor.
		self.diff_window = DiffWindow(self.manager, "diff_window")
		## Keyboard Manager instance to interpret key input.
		self.keys = Keyboard(self.manager)										# Load Keyboard module.
		self.manager.update()													# Update Panel Manager contents.
	##
	## @brief      Turn the engine once.
	##
	## @param      self  This object
	##
	def turn(self):
		self.window_bar.update()
		self.line_jump_bar.update()
		self.save_bar.update()
		self.search_bar.update()
		self.manager.get("current_file_window").update()
		self.line_numbers.update()
		self.highlighter.update()
		self.config_customizer.update()
		self.open_bar.update()
		self.debug_window.update()
		self.help_window.update()
		self.diff_window.update()
		self.manager.update()
		self.keys.update()														# Grab key input and interpret through bindings.

	def setException(self, e):
		self.exception = e
		self.manager.set("EngineException", e)

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
	## @brief      terminate engine
	##
	## @param      self  This object
	##
	def terminate(self):														# Terminate all modules in reverse order of initialization.
		self.keys.terminate()
		for file_window in self.file_window_list:
			file_window.terminate()
		self.manager.terminate()
		for file in self.files:
			file.terminate()
