import string

##
## @brief      Class for keyboard.
##
class Keyboard:
	##
	## @brief      Constructs this Keyboard object.
	##
	## @param      self     This object
	## @param      manager  The manager to allow scheduling actions in external Windows
	##
	def __init__(self, manager):

		## The manager to allow scheduling actions in external Windows.
		self.manager = manager

		## The binding dictionary. Bindings saved as "keyname": function instance.
		self.bindings = {}

		## FileWindow instance for fileWindow keybindings.
		self.file_window = self.manager.get("current_file_window")

		self.line_jump_bar = self.manager.get("line_jump_bar")

		self.save_bar = self.manager.get("save_bar")

		self.search_bar = self.manager.get("search_bar")

		self.debug_window = self.manager.get("debug_window")

		self.open_bar = self.manager.get("open_bar")

		self.help_window = self.manager.get("help_window")

		self.diff_window = self.manager.get("diff_window")

		## ConfigCustomizer instance for customizer keybindings. (Only used for toggle)
		self.config_customizer = self.manager.get("config_customizer")

		self.bind()
		
	##
	## @brief      Update. grab key and do something with it. 
	##
	## @param      self  This object
	##
	def update(self):
		try:
			c = self.manager.screen.getch()
		except KeyboardInterrupt:
			c = -1
			self.leave()

		while c != -1:
			self.manager.screen.timeout(20)
			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.bindings:
				if c == "^I":
					self.bindings[c]("\t")
				else:
					self.bindings[c]()

			elif c in string.punctuation + string.digits + string.ascii_letters + " \t":
				self.bindings["printable-character"](c)

			c = self.manager.screen.getch()

		self.manager.screen.timeout(-1)

	def leave(self):
		if not self.save_bar.confirmExitSave():
			return
		exception = self.manager.get("EngineException")
		raise exception

	##
	## @brief      Terminate Keyboard Manager
	##
	## @param      self  This object
	##
	def terminate(self):
		pass

	##
	## @brief      Binds all keybindings to binding dictionary. Saved as "keyname": function instance.
	##
	## @param      self  This object
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
			"KEY_F(5)":  self.selectPrevFileWindow,
			"KEY_F(6)":  self.selectNextFileWindow,
			"KEY_HOME":  self.file_window.gotoStartOfLine,
			"KEY_NPAGE": self.file_window.scrollDown,
			"KEY_PPAGE": self.file_window.scrollUp,

			"KEY_BTAB":  self.file_window.unindentSelectedLines,

			"KEY_F(1)": self.help_window.toggle,

			"^T": self.diff_window.toggle,

			"^D": self.file_window.deleteLineAtFilecursor,
			"^J": self.file_window.newLineAtFilecursor,
			"^W": self.file_window.saveFile,
			"^I": self.file_window.enterTextAtFilecursor,

			"^O": self.open_bar.openFile,

			"^F": self.search_bar.search,
			"^L": self.line_jump_bar.jumpToLine,
			"^G": self.search_bar.searchNext,
			"^R": self.search_bar.replace,

			"^_": self.config_customizer.toggle,

			"^A": self.file_window.selectAll,
			"^B": self.file_window.toggleSelect,
			"^K": self.file_window.copySelect,
			"^V": self.file_window.pasteAtFilecursor,
			"^X": self.file_window.cutSelect,

			"kRIT5": self.file_window.moveViewportRight,
			"kLFT5": self.file_window.moveViewportLeft,
			"kUP5":  self.file_window.moveViewportUp,
			"kDN5":  self.file_window.moveViewportDown,

			"KEY_F(9)": self.closeFileWindow,
			"KEY_F(12)": self.debug_window.toggle,
			"^[": self.leave
		}

		self.manager.set("keybindings", self.bindings)
		
	##
	## @brief      Change FileWindow instance to which keybindings are bound to the previous instance.
	##
	## @param      self  This object
	##
	def selectPrevFileWindow(self):
		self.file_window = self.manager.get("current_file_window")
		self.file_window.panel.hide()
		old_copy_lines = self.file_window.copy_lines # share copied text globally across fileWindows
		file_window_list = self.manager.get("file_window_list")
		if file_window_list.index(self.file_window) - 1 >= 0:
			self.file_window = file_window_list[file_window_list.index(self.file_window) - 1]
		else:
			self.file_window = file_window_list[len(file_window_list) - 1]
		self.manager.set("current_file_window", self.file_window) # re-set current file window in manager
		self.file_window.panel.top()
		self.file_window.panel.show()
		self.file_window.is_modified = True
		self.file_window.copy_lines = old_copy_lines
		self.bind() # kludge ... bindings array holds function pointers to specific FileWindow object instances... we have to rebind to keep this implementation...

	##
	## @brief      Change FileWindow instance to which keybindings are bound to the next instance.
	##
	## @param      self  This object
	##
	def selectNextFileWindow(self):
		self.file_window = self.manager.get("current_file_window")
		self.file_window.panel.hide()
		old_copy_lines = self.file_window.copy_lines # share copied text globally across fileWindows
		file_window_list = self.manager.get("file_window_list")
		if file_window_list.index(self.file_window) + 1 < len(file_window_list):
			self.file_window = file_window_list[file_window_list.index(self.file_window) + 1]
		else:
			self.file_window = file_window_list[0]
		self.manager.set("current_file_window", self.file_window) # re-set current file window in manager
		self.file_window.panel.top()
		self.file_window.panel.show()
		self.file_window.is_modified = True
		self.file_window.copy_lines = old_copy_lines
		self.bind() # kludge ... bindings array holds function pointers to specific FileWindow object instances... we have to rebind to keep this implementation...

	##
	## @brief      Close FileWindow instance.
	##
	## @param      self  This object
	##
	def closeFileWindow(self):
		if not self.save_bar.confirmExitSave():
			# TODO clean up how this confirm is handled and then revise above logic in leave()
			return
		file_window_to_remove = self.manager.get("current_file_window")
		self.selectNextFileWindow()
		if file_window_to_remove is not self.manager.get("current_file_window"):
			window_list = self.manager.get("file_window_list")
			window_list.remove(file_window_to_remove)
		else:
			pass # TODO do something different if trying to close last filewindow in active list

