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
		from modules.file import File 											#
		from modules.panels import Manager										# Modules being used: File, Manager, fileWindow, Keyboard
		from modules.fileWindow import FileWindow								# Submodules->Window
		from modules.keybindings import Keyboard								#
		from modules.syntaxhighlighting import Highlighter 						#
		from modules.magicbar import MagicBar
		## File instance to be used in editor.
		self.venicFile = File(self.parseArgs().filename)						# Load file provided as only arg.
		## Panel Manager instance for modules
		self.panels = Manager()													# Load Manager.
		## FileWindow instance using File to begin editor
		self.fileWindow = FileWindow(self.panels, "fileWindow", self.venicFile)	# Create fileWindow.
		self.fileWindow.update()												# Update fileWindow contents.
		## Highlighter instance to colorize FileWindow contents
		self.highlighter = Highlighter(self.panels)
		self.panels.update()													# Update Panel (Manager) contents.
		## Keyboard Manager instance to interpret key input
		self.magicbar = MagicBar(self.panels, "magicBar")
		self.keys = Keyboard(self.panels)										# Load Keyboard module.
	##
	## @brief      Turn the engine once.
	##
	## @param      self  The object
	##
	def turn(self):																# Run this method while Engine is running.
		self.magicbar.update()
		self.fileWindow.update()
		self.highlighter.update()												#
		self.panels.update()													#
		self.keys.update()														# Grab key input and interpret through bindings.
	##
	## @brief      Parses arguments given via command line
	##
	## @param      self  The object
	##
	def parseArgs(self):														# 
		import argparse															# load arg parser module for file input
		parser = argparse.ArgumentParser()										#
		parser.add_argument("filename", nargs='?')											# create program parameter, filename/path
		return parser.parse_args()												#
	##
	## @brief      terminate engine
	##
	## @param      self  The object
	##
	def terminate(self):														# Terminate all modules in reverse order of initialization.
		self.keys.terminate()
#		debug = self.highlighter.highlightedCodeLines
		self.fileWindow.terminate()
		self.panels.terminate()
		self.venicFile.terminate()
#		print(debug)
