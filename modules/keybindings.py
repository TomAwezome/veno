import string, inspect

KEYBINDINGS = {
	"KEY_UP":    "filewindowmanager.moveFilecursorUp",
	"KEY_DOWN":  "filewindowmanager.moveFilecursorDown",
	"KEY_LEFT":  "filewindowmanager.moveFilecursorLeft",
	"KEY_RIGHT": "filewindowmanager.moveFilecursorRight",

	"printable-character": "filewindowmanager.enterTextAtFilecursor",

	"KEY_BACKSPACE": "filewindowmanager.backspaceTextAtFilecursor",
	"^H":            "filewindowmanager.backspaceTextAtFilecursor",
	"^?":            "filewindowmanager.backspaceTextAtFilecursor",

	"KEY_DC": "filewindowmanager.deleteTextAtFilecursor",

	"KEY_F(2)": "runwindow.run",

	"KEY_END":   "filewindowmanager.gotoEndOfLine",
	"KEY_F(3)":  "filewindowmanager.gotoStartOfFile",
	"KEY_F(4)":  "filewindowmanager.gotoEndOfFile",
	"KEY_F(5)":  "filewindowmanager.selectPrevFileWindow",
	"KEY_F(6)":  "filewindowmanager.selectNextFileWindow",
	"KEY_HOME":  "filewindowmanager.gotoStartOfLine",
	"KEY_NPAGE": "filewindowmanager.scrollFilecursorDown",
	"KEY_PPAGE": "filewindowmanager.scrollFilecursorUp",
	"kPRV3":     "filewindowmanager.scrollViewportUp",
	"kNXT3":     "filewindowmanager.scrollViewportDown",
	"kPRV5":     "filewindowmanager.scrollViewportUp",
	"kNXT5":     "filewindowmanager.scrollViewportDown",

	"KEY_BTAB":  "filewindowmanager.unindentSelectedLines",

	"^_": "configcustomizer.toggle",

	"^O": "openbar.openFile",

	"^T": "diffwindow.toggle",
	"^L": "linejumpbar.jumpToLine",
	"^F": "searchbar.search",
	"^G": "searchbar.searchNext",
	"^R": "searchbar.replace",

	"^D": "filewindowmanager.deleteLineAtFilecursor",
	"^J": "filewindowmanager.newLineAtFilecursor",
	"^W": "filewindowmanager.saveFile",
	"^I": "filewindowmanager.enterTextAtFilecursor",

	"^A": "filewindowmanager.selectAll",
	"^B": "filewindowmanager.toggleSelect",
	"^K": "filewindowmanager.copySelect",
	"^V": "filewindowmanager.pasteAtFilecursor",
	"^X": "filewindowmanager.cutSelect",

	"kRIT5": "filewindowmanager.moveViewportRight",
	"kLFT5": "filewindowmanager.moveViewportLeft",
	"kUP5":  "filewindowmanager.moveViewportUp",
	"kDN5":  "filewindowmanager.moveViewportDown",

	"KEY_F(9)":  "filewindowmanager.closeFileWindow",
	"KEY_F(1)":  "helpwindow.toggle",
	"KEY_F(12)": "debugwindow.toggle",
}

##
## @brief      Class for keyboard.
##
class Keyboard:
	##
	## @brief      Constructs this Keyboard object.
	##
	## @param      self     This object
	## @param      engine  The engine to allow scheduling actions in external Windows
	##
	def __init__(self, engine):

		## The engine to allow scheduling actions in external Windows.
		self.engine = engine

		## The binding dictionary. Bindings saved as "keyname": function instance.
		self.bindings = {}

		self.bind()
		
	##
	## @brief      Update. grab key and do something with it. 
	##
	## @param      self  This object
	##
	def update(self):
		try:
			c = self.engine.screen.getch()
		except KeyboardInterrupt:
			c = -1
			self.leave()

		while c != -1:
			self.engine.screen.timeout(20)
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.bindings:
				if c == "^I":
					self.bindings[c]("\t")
				else:
					self.bindings[c]()

			elif c == "^[": # ESC
				c = -1
				self.leave()

			elif c in string.punctuation + string.digits + string.ascii_letters + " \t":
				self.bindings["printable-character"](c)


			c = self.engine.screen.getch()

		self.engine.screen.timeout(-1)

	def leave(self, confirm=True):
		if confirm:
			save_bar = self.engine.get("savebar")
			if save_bar is not None and not save_bar.confirmExitSave():
				return
		exception = self.engine.get("EngineException")
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
		self.bindings = {}
		for key, val in KEYBINDINGS.items():
			objname_and_mthname = val.split('.')
			if len(objname_and_mthname) != 2:
				response = ''
				while response != 'y':
					response = self.engine.errorPrompt(f"KEYBINDINGS dictionary key '{key}' invalid value: {val}\nKeybinding must be removed.")
				continue
			object_name = objname_and_mthname[0]
			method_name = objname_and_mthname[1]
			global_object = self.engine.get(object_name)
			if global_object is None:
				response = ''
				while response != 'y':
					response = self.engine.errorPrompt(f"KEYBINDINGS dictionary key '{key}' no global object named '{object_name}'\nKeybinding must be removed.")
				continue
			object_method_dict = dict((key, value) for key, value in inspect.getmembers(global_object, inspect.ismethod))
			if method_name not in object_method_dict:
				response = ''
				while response != 'y':
					response = self.engine.errorPrompt(f"KEYBINDINGS dictionary key '{key}' no method named '{method_name}' in object '{object_name}'\nKeybinding must be removed.")
				continue

			self.bindings[key] = object_method_dict[method_name]

		self.engine.set("bindings", self.bindings)

