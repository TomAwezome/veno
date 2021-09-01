##
## @brief      Veno Engine Class. Built to be easily and swiftly customized.
##
class Engine():
	##
	## @brief      Constructs the object.
	##
	## @param      self  The object
	##
	def __init__(self):
		# Modules being used: File, Manager, FileWindow, Keyboard, LineNumbers, MagicBar, ConfigCustomizer, SyntaxHighlighting
		from modules.config import Config
		from modules.file import File
		from modules.panels import Manager
		from modules.fileWindow import FileWindow
		from modules.keybindings import Keyboard
		from modules.syntaxhighlighting import Highlighter
		from modules.magicbar import MagicBar
		from modules.linenumbers import LineNumbersWindow
		from modules.configcustomizer import ConfigCustomizerWindow
		filename = self.parseArgs().filename or "untitled.txt"
		## Config instance for editor.
		self.config = Config(filename)
		## File instance to be used in editor.
		self.file = File(filename)												# Load file provided as only arg.
		## Panel Manager instance for modules.
		self.panels = Manager()													# Load Manager.
		self.panels.Objects["config"] = self.config
		## FileWindow instance using File to begin editor.
		self.file_window = FileWindow(self.panels, "fileWindow", self.file)		# Create fileWindow.
		self.file_window.update()												# Update fileWindow contents.
		## Highlighter instance to colorize FileWindow contents.
		self.highlighter = Highlighter(self.panels)
		self.panels.Objects["highlighter"] = self.highlighter
		## MagicBar Window instance to perform various file utilities.
		self.magic_bar = MagicBar(self.panels, "magicBar")
		## LineNumbers Window instance to display next to FileWindow.
		self.line_numbers = LineNumbersWindow(self.panels, "lineNumbers")
		## ConfigCustomizer Window instance to allow modifying configuration.
		self.config_customizer = ConfigCustomizerWindow(self.panels, "configCustomizer")
		## Keyboard Manager instance to interpret key input.
		self.keys = Keyboard(self.panels)										# Load Keyboard module.
		self.panels.update()													# Update Panel (Manager) contents.
	##
	## @brief      Turn the engine once.
	##
	## @param      self  The object
	##
	def turn(self):
		self.magic_bar.update()
		self.file_window.update()
		self.line_numbers.update()
		self.highlighter.update()
		self.config_customizer.update()
		self.panels.update()
		self.keys.update()														# Grab key input and interpret through bindings.
	##
	## @brief      Parses arguments given via command line
	##
	## @param      self  The object
	##
	def parseArgs(self):														# 
		import argparse															# load arg parser module for file input
		parser = argparse.ArgumentParser()										#
		parser.add_argument("filename", nargs='?')								# create program parameter, filename/path
		return parser.parse_args()												#
	##
	## @brief      terminate engine
	##
	## @param      self  The object
	##
	def terminate(self):														# Terminate all modules in reverse order of initialization.
		self.keys.terminate()
		self.file_window.terminate()
		self.panels.terminate()
		self.file.terminate()
