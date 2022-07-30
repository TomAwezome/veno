class FileWindowManager:
	def __init__(self, engine):
		self.engine = engine
		
		self.file_window_list = []
		self.engine.set("file_window_list", self.file_window_list)
		
		File = self.engine.get("File")
		FileWindow = self.engine.get("FileWindow")

		for filename in self.engine.filenames:
			try:
				file_window = FileWindow(self.engine, File(filename))		# Create fileWindow.
				self.file_window_list.append(file_window)
				file_window.update()											# Update fileWindow contents.
			except IsADirectoryError:
				pass

		if self.file_window_list != []:
			self.current_file_window = self.file_window_list[0]
			self.engine.set("current_file_window", self.current_file_window)
		else: # filewindow list can be empty if provided arg is a directory and no other filename args are given
			self.current_file_window = FileWindow(self.engine, File("untitled.txt"))
			self.file_window_list.append(self.current_file_window)
			file_window.update()
			self.engine.set("current_file_window", self.current_file_window)

	def update(self):
		self.current_file_window = self.engine.get("current_file_window")
		self.current_file_window.update()

	def terminate(self):
		for file_window in self.file_window_list:
			file_window.terminate()


# FUNCTIONS TO BE CALLED EXTERNALLY

		
	##
	## @brief      Change FileWindow instance to which keybindings are bound to the previous instance.
	##
	## @param      self  This object
	##
	def selectPrevFileWindow(self):
		self.current_file_window.panel.hide()
		old_copy_lines = self.current_file_window.copy_lines # share copied text globally across fileWindows
		if self.file_window_list.index(self.current_file_window) - 1 >= 0:
			self.current_file_window = self.file_window_list[self.file_window_list.index(self.current_file_window) - 1]
		else:
			self.current_file_window = self.file_window_list[len(self.file_window_list) - 1]
		self.engine.set("current_file_window", self.current_file_window) # re-set current file window in engine
		self.current_file_window.panel.show()
		self.current_file_window.is_modified = True
		self.current_file_window.copy_lines = old_copy_lines

	##
	## @brief      Change FileWindow instance to which keybindings are bound to the next instance.
	##
	## @param      self  This object
	##
	def selectNextFileWindow(self):
		self.current_file_window.panel.hide()
		old_copy_lines = self.current_file_window.copy_lines # share copied text globally across fileWindows
		if self.file_window_list.index(self.current_file_window) + 1 < len(self.file_window_list):
			self.current_file_window = self.file_window_list[self.file_window_list.index(self.current_file_window) + 1]
		else:
			self.current_file_window = self.file_window_list[0]
		self.engine.set("current_file_window", self.current_file_window) # re-set current file window in engine
		self.current_file_window.panel.show()
		self.current_file_window.is_modified = True
		self.current_file_window.copy_lines = old_copy_lines

	##
	## @brief      Close FileWindow instance.
	##
	## @param      self  This object
	##
	def closeFileWindow(self):
		save_bar = self.engine.get("savebar")
		if save_bar is not None and not save_bar.confirmCloseSave():
			return
		file_window_to_remove = self.current_file_window
		self.selectNextFileWindow()
		if file_window_to_remove is not self.engine.get("current_file_window"):
			self.file_window_list.remove(file_window_to_remove)
		else:
			self.engine.get("keybindings").leave(confirm=False)

	def getViewportX(self):
		return self.current_file_window.getViewportX()

	def getViewportY(self):
		return self.current_file_window.getViewportY()

	def getFilecursorX(self):
		return self.current_file_window.getFilecursorX()

	def getFilecursorY(self):
		return self.current_file_window.getFilecursorY()

	def getSelectX(self):
		return self.current_file_window.getSelectX()

	def getSelectY(self):
		return self.current_file_window.getSelectY()

	def setSelectX(self, x):
		return self.current_file_window.setSelectX(x)
	
	def setSelectY(self, y):
		return self.current_file_window.setSelectY(y)

	def setViewportX(self, x):
		return self.current_file_window.setViewportX(x)

	def setViewportY(self, y):
		return self.current_file_window.setViewportY(y)

	def setFilecursorX(self, x):
		return self.current_file_window.setFilecursorX(x)

	def setFilecursorY(self, y):
		return self.current_file_window.setFilecursorY(y)

	def toggleSelect(self):
		return self.current_file_window.toggleSelect()

	def selectAll(self):
		return self.current_file_window.selectAll()

	def copySelect(self, toggle=True):
		return self.current_file_window.copySelect(toggle)

	def cutSelect(self):
		return self.current_file_window.cutSelect()

	def pasteAtFilecursor(self):
		return self.current_file_window.pasteAtFilecursor()

	def moveViewportDown(self):
		return self.current_file_window.moveViewportDown()

	def moveViewportUp(self):
		return self.current_file_window.moveViewportUp()

	def moveViewportRight(self):
		return self.current_file_window.moveViewportRight()

	def moveViewportLeft(self):
		return self.current_file_window.moveViewportLeft()

	def scrollViewportDown(self):
		return self.current_file_window.scrollViewportDown()

	def scrollViewportUp(self):
		return self.current_file_window.scrollViewportUp()

	def moveFilecursorUp(self):
		return self.current_file_window.moveFilecursorUp()

	def moveFilecursorDown(self):
		return self.current_file_window.moveFilecursorDown()

	def moveFilecursorLeft(self, dist=1):
		return self.current_file_window.moveFilecursorLeft(dist)

	def moveFilecursorRight(self, dist=1):
		return self.current_file_window.moveFilecursorRight(dist)

	def moveViewportToCursorX(self):
		return self.current_file_window.moveViewportToCursorX()

	def moveViewportToCursorY(self):
		return self.current_file_window.moveViewportToCursorY()

	def moveViewportToCursor(self):
		return self.current_file_window.moveViewportToCursor()

	def jumpToLine(self, line_num, preserve_x = False):
		return self.current_file_window.jumpToLine(line_num, preserve_x)

	def gotoStartOfFile(self):
		return self.current_file_window.gotoStartOfFile()

	def gotoEndOfFile(self):
		return self.current_file_window.gotoEndOfFile()

	def gotoStartOfLine(self):
		return self.current_file_window.gotoStartOfLine()

	def gotoEndOfLine(self):
		return self.current_file_window.gotoEndOfLine()

	def unindentSelectedLines(self):
		return self.current_file_window.unindentSelectedLines()

	def indentSelectedLines(self, text):
		return self.current_file_window.indentSelectedLines(text)

	def enterTextAtFilecursor(self, text):
		return self.current_file_window.enterTextAtFilecursor(text)

	def newLineAtFilecursor(self, auto_indent_override=True):
		return self.current_file_window.newLineAtFilecursor(auto_indent_override)

	def backspaceTextAtFilecursor(self):
		return self.current_file_window.backspaceTextAtFilecursor()

	def saveFile(self):
		return self.current_file_window.saveFile()

	def scrollFilecursorDown(self):
		return self.current_file_window.scrollFilecursorDown()

	def scrollFilecursorUp(self):
		return self.current_file_window.scrollFilecursorUp()

	def deleteLineAtFilecursor(self):
		return self.current_file_window.deleteLineAtFilecursor()

	def deleteTextAtFilecursor(self):
		return self.current_file_window.deleteTextAtFilecursor()
