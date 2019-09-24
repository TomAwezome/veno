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
			self.manager.Windows["magicBar"].confirmExitSave()
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
		self.bindings["KEY_UP"] = self.manager.Windows["fileWindow"].moveFilecursorUp
		self.bindings["KEY_DOWN"] = self.manager.Windows["fileWindow"].moveFilecursorDown
		self.bindings["KEY_LEFT"] = self.manager.Windows["fileWindow"].moveFilecursorLeft
		self.bindings["KEY_RIGHT"] = self.manager.Windows["fileWindow"].moveFilecursorRight
		self.bindings["printable-character"] = self.manager.Windows["fileWindow"].enterTextAtFilecursor
		self.bindings["KEY_BACKSPACE"] = self.manager.Windows["fileWindow"].backspaceTextAtFilecursor
		self.bindings["KEY_DC"] = self.manager.Windows["fileWindow"].deleteTextAtFilecursor
		self.bindings["KEY_END"] = self.manager.Windows["fileWindow"].gotoEndOfLine
		self.bindings["KEY_F(3)"] = self.manager.Windows["fileWindow"].gotoStartOfFile
		self.bindings["KEY_F(4)"] = self.manager.Windows["fileWindow"].gotoEndOfFile
		self.bindings["KEY_HOME"] = self.manager.Windows["fileWindow"].gotoStartOfLine
		self.bindings["KEY_NPAGE"] = self.manager.Windows["fileWindow"].scrollDown
		self.bindings["KEY_PPAGE"] = self.manager.Windows["fileWindow"].scrollUp
		self.bindings["^D"] = self.manager.Windows["fileWindow"].deleteLineAtFilecursor
		self.bindings["^J"] = self.manager.Windows["fileWindow"].newLineAtFilecursor
		self.bindings["^W"] = self.manager.Windows["fileWindow"].saveFile
		self.bindings["^I"] = self.manager.Windows["fileWindow"].enterTextAtFilecursor
		self.bindings["^F"] = self.manager.Windows["magicBar"].search
		self.bindings["^L"] = self.manager.Windows["magicBar"].gotoLine
		self.bindings["^G"] = self.manager.Windows["magicBar"].searchNext
		self.bindings["^R"] = self.manager.Windows["magicBar"].replace
		self.bindings["^_"] = self.manager.Windows["configCustomizer"].toggle
		self.bindings["^B"] = self.manager.Windows["fileWindow"].toggleSelect
		self.bindings["^?"] = self.manager.Windows["fileWindow"].backspaceTextAtFilecursor
		self.bindings["^K"] = self.manager.Windows["fileWindow"].copySelect
		self.bindings["^V"] = self.manager.Windows["fileWindow"].pasteAtFilecursor
		self.bindings["^X"] = self.manager.Windows["fileWindow"].cutSelect
		self.bindings["kRIT5"] = self.manager.Windows["fileWindow"].moveViewportRight
		self.bindings["kLFT5"] = self.manager.Windows["fileWindow"].moveViewportLeft
		self.bindings["kUP5"] = self.manager.Windows["fileWindow"].moveViewportUp
		self.bindings["kDN5"] = self.manager.Windows["fileWindow"].moveViewportDown
