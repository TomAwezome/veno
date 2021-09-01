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

		## The manager to allow scheduling actions in external Windows.
		self.manager = manager

		## The binding dictionary. Bindings saved as "keyname": function instance.
		self.bindings = {}

		## FileWindow instance for fileWindow keybindings.
		self.file_window = self.manager.Windows["fileWindow"]

		## MagicBar instance for magicBar keybindings.
		self.magic_bar = self.manager.Windows["magicBar"]
		
		## ConfigCustomizer instance for customizer keybindings. (Only used for toggle)
		self.config_customizer = self.manager.Windows["configCustomizer"]
		
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
			self.magic_bar.confirmExitSave()

		while c != -1:
			self.manager.stdscr.timeout(20)
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

		self.manager.stdscr.timeout(-1)
	##
	## @brief      Terminate Keyboard Manager
	##
	## @param      self  The object
	##
	def terminate(self):
		pass
	##
	## @brief      Binds all keybindings to binding dictionary. Saved as "keyname": function instance.
	##
	## @param      self  The object
	##
	def bind(self):
		self.bindings = {
			"KEY_UP":    self.file_window.moveFilecursorUp,
			"KEY_DOWN":  self.file_window.moveFilecursorDown,
			"KEY_LEFT":  self.file_window.moveFilecursorLeft,
			"KEY_RIGHT": self.file_window.moveFilecursorRight,

			"printable-character": self.file_window.enterTextAtFilecursor,

			"KEY_BACKSPACE": self.file_window.backspaceTextAtFilecursor,
			"^H":            self.file_window.backspaceTextAtFilecursor,
			"^?":            self.file_window.backspaceTextAtFilecursor,

			"KEY_DC": self.file_window.deleteTextAtFilecursor,

			"KEY_END":   self.file_window.gotoEndOfLine,
			"KEY_F(3)":  self.file_window.gotoStartOfFile,
			"KEY_F(4)":  self.file_window.gotoEndOfFile,
			"KEY_HOME":  self.file_window.gotoStartOfLine,
			"KEY_NPAGE": self.file_window.scrollDown,
			"KEY_PPAGE": self.file_window.scrollUp,

			"KEY_BTAB":  self.file_window.unindentSelectedLines,

			"^D": self.file_window.deleteLineAtFilecursor,
			"^J": self.file_window.newLineAtFilecursor,
			"^W": self.file_window.saveFile,
			"^I": self.file_window.enterTextAtFilecursor,

			"^F": self.magic_bar.search,
			"^L": self.magic_bar.gotoLine,
			"^G": self.magic_bar.searchNext,
			"^R": self.magic_bar.replace,

			"^_": self.config_customizer.toggle,

			"^B": self.file_window.toggleSelect,
			"^K": self.file_window.copySelect,
			"^V": self.file_window.pasteAtFilecursor,
			"^X": self.file_window.cutSelect,

			"kRIT5": self.file_window.moveViewportRight,
			"kLFT5": self.file_window.moveViewportLeft,
			"kUP5":  self.file_window.moveViewportUp,
			"kDN5":  self.file_window.moveViewportDown
		}
