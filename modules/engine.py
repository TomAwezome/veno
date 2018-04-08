#
# Veno Engine. Built to be easily and swiftly customized.
#
class Engine():
	def __init__(self):
		from modules.file import File 											#
		from modules.panels import Manager										# Modules being used: File, Manager, fileWindow, Keyboard
		from modules.fileWindow import FileWindow								# Submodules->Window
		from modules.keybindings import Keyboard
		# from modules.syntaxhighlighting import Highlighter 						#
		self.venicFile = File(self.parseArgs().filename)						# Load file provided as only arg.
		self.panels = Manager()													# Load Manager.
		self.fileWindow = FileWindow(self.panels, "fileWindow", self.venicFile)	# Create fileWindow.
		self.fileWindow.update()												# Update fileWindow contents.
		# self.highlighter = Highlighter(self.panels)
		self.panels.update()													# Update Panel (Manager) contents.
		self.keys = Keyboard(self.panels)										# Load Keyboard module.
	def turn(self):																# Run this method while Engine is running.
		self.fileWindow.update()												#
		self.panels.update()													#
		self.keys.update()														# Grab key input and interpret through bindings.
	def parseArgs(self):														# 
		import argparse															# load arg parser module for file input
		parser = argparse.ArgumentParser()										#
		parser.add_argument("filename", nargs='?' )											# create program parameter, filename/path
		return parser.parse_args()												#
	def terminate(self):														# Terminate all modules in reverse order of initialization.
		self.keys.terminate()
		self.fileWindow.terminate()
		self.panels.terminate()
		self.venicFile.terminate()