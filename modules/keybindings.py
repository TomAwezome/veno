import string
##
## @brief      Class for keyboard.
##
class Keyboard:
	##
	## @brief      Constructs the object.
	##
	## @param      self     The object
	## @param      manager  The manager to allow scheduling actions in external Windows
	##
	def __init__(self, manager):

		## The manager to allow scheduling actions in external Windows
		self.manager = manager

		## The binding dictionary. Bindings saved as "keyname"->function instance
		self.bindings = {}

		## FileWindow instance for fileWindow keybindings
		self.fileWindow = self.manager.Windows["fileWindow"]

		## MagicBar instance for magicBar keybindings
		self.magicBar = self.manager.Windows["magicBar"]
		
		## ConfigCustomizer instance for customizer keybindings (only toggle for now)
		self.configCustomizer = self.manager.Windows["configCustomizer"]
		
		self.bind()
	##
	## @brief      Update. grab key and do something with it. 
	##
	## @param      self  The object
	##
	def update(self):
		try:
			c = self.manager.stdscr.getch()
		except KeyboardInterrupt:
			c = -1
			self.magicBar.confirmExitSave()

		while c != -1:
			self.manager.stdscr.timeout(30)
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.bindings:
				if c == "^I":
					self.bindings[c]("\t")
				else:
					self.bindings[c]()

			elif c in string.punctuation + string.digits + string.ascii_letters + " \t":
				self.bindings["printable-character"](c)

			c = self.manager.stdscr.getch()

		if c == -1:
			self.manager.stdscr.timeout(-1)
	##
	## @brief      Terminate Keyboard Manager
	##
	## @param      self  The object
	##
	def terminate(self):
		pass
	##
	## @brief      Binds all keybindings to binding dictionary. Saved as "keyname"->function instance
	##
	## @param      self  The object
	##
	def bind(self):
		self.bindings["KEY_UP"] = self.fileWindow.moveFilecursorUp
		self.bindings["KEY_DOWN"] = self.fileWindow.moveFilecursorDown
		self.bindings["KEY_LEFT"] = self.fileWindow.moveFilecursorLeft
		self.bindings["KEY_RIGHT"] = self.fileWindow.moveFilecursorRight

		self.bindings["printable-character"] = self.fileWindow.enterTextAtFilecursor

		self.bindings["KEY_BACKSPACE"] = self.fileWindow.backspaceTextAtFilecursor
		self.bindings["^H"] = self.fileWindow.backspaceTextAtFilecursor
		self.bindings["KEY_DC"] = self.fileWindow.deleteTextAtFilecursor

		self.bindings["KEY_END"] = self.fileWindow.gotoEndOfLine
		self.bindings["KEY_F(3)"] = self.fileWindow.gotoStartOfFile
		self.bindings["KEY_F(4)"] = self.fileWindow.gotoEndOfFile
		self.bindings["KEY_HOME"] = self.fileWindow.gotoStartOfLine
		self.bindings["KEY_NPAGE"] = self.fileWindow.scrollDown
		self.bindings["KEY_PPAGE"] = self.fileWindow.scrollUp

		self.bindings["^D"] = self.fileWindow.deleteLineAtFilecursor
		self.bindings["^J"] = self.fileWindow.newLineAtFilecursor
		self.bindings["^W"] = self.fileWindow.saveFile
		self.bindings["^I"] = self.fileWindow.enterTextAtFilecursor

		self.bindings["^F"] = self.magicBar.search
		self.bindings["^L"] = self.magicBar.gotoLine
		self.bindings["^G"] = self.magicBar.searchNext
		self.bindings["^R"] = self.magicBar.replace

		self.bindings["^_"] = self.configCustomizer.toggle

		self.bindings["^B"] = self.fileWindow.toggleSelect
		self.bindings["^?"] = self.fileWindow.backspaceTextAtFilecursor
		self.bindings["^K"] = self.fileWindow.copySelect
		self.bindings["^V"] = self.fileWindow.pasteAtFilecursor
		self.bindings["^X"] = self.fileWindow.cutSelect

		self.bindings["kRIT5"] = self.fileWindow.moveViewportRight
		self.bindings["kLFT5"] = self.fileWindow.moveViewportLeft
		self.bindings["kUP5"] = self.fileWindow.moveViewportUp
		self.bindings["kDN5"] = self.fileWindow.moveViewportDown
