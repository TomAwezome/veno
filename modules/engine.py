from modules.config import Config
from modules.file import File
from modules.panels import Manager
from modules.fileWindow import FileWindow
from modules.keybindings import Keyboard
from modules.syntaxhighlighting import Highlighter
from modules.magicbar import MagicBar
from modules.linenumbers import LineNumbersWindow
from modules.configcustomizer import ConfigCustomizerWindow

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
		# Modules being used: Config, File, Manager, FileWindow, Keyboard, LineNumbers, MagicBar, ConfigCustomizer, SyntaxHighlighting
		filenames = self.parseArgs().filename or ["untitled.txt"]

		## Config instance for editor.
		self.config = Config(filenames[0])
		## File instance list to be used by editor.
		self.files = []
		## FileWindow instance list.
		self.file_window_list = []
		## Panel Manager instance for modules.
		self.manager = Manager()												# Load Manager.
		self.manager.add("config", self.config)
		self.manager.add("file_window_list", self.file_window_list)

		for filename in filenames:
			try:
				file = File(filename)
				self.files.append(file)											# Load file provided as only arg.
				file_window = FileWindow(self.manager, "fileWindow", file)		# Create fileWindow.
				self.file_window_list.append(file_window)
				file_window.update()											# Update fileWindow contents.
			except IsADirectoryError:
				pass		
		if self.file_window_list != []:
			self.manager.add("current_file_window", self.file_window_list[0])
		else: # filewindow list can be empty if provided arg is a directory and no other filename args are given
			file = File("untitled.txt")
			self.files.append(file)
			file_window = FileWindow(self.manager, "fileWindow", file)
			self.file_window_list.append(file_window)
			file_window.update()
			self.manager.add("current_file_window", self.file_window_list[0])

		## Highlighter instance to colorize FileWindow contents.
		self.highlighter = Highlighter(self.manager)
		self.manager.add("highlighter", self.highlighter)
		## MagicBar Window instance to perform various file utilities.
		self.magic_bar = MagicBar(self.manager, "magicBar")
		## LineNumbers Window instance to display next to FileWindow.
		self.line_numbers = LineNumbersWindow(self.manager, "lineNumbers")
		## ConfigCustomizer Window instance to allow modifying configuration.
		self.config_customizer = ConfigCustomizerWindow(self.manager, "configCustomizer")
		## Keyboard Manager instance to interpret key input.
		self.keys = Keyboard(self.manager)										# Load Keyboard module.
		self.manager.update()													# Update Panel Manager contents.
	##
	## @brief      Turn the engine once.
	##
	## @param      self  This object
	##
	def turn(self):
		self.magic_bar.update()
		self.manager.get("current_file_window").update()
		self.line_numbers.update()
		self.highlighter.update()
		self.config_customizer.update()
		self.manager.update()
		self.keys.update()														# Grab key input and interpret through bindings.
	##
	## @brief      Parses arguments given via command line
	##
	## @param      self  This object
	##
	def parseArgs(self):														# 
		import argparse															# load arg parser module for file input
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
