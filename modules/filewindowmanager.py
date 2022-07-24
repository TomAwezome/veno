"""
this needs the logic for:
- swap the file windows
- open the files up at init and set internal variables
- maintain current_file_window state 
- terminate all the filewindows at shutdown
"""
class FileWindowManager:
	def __init__(self, engine):
		self.engine = engine
		
		self.file_window_list = []
		self.engine.set("file_window_list", self.file_window_list)
		
		File = self.engine.get("File")
		FileWindow = self.engine.get("FileWindow")

		for filename in self.engine.filenames:
			try:
				file = File(filename)
#				self.files.append(file)											# Load file provided as only arg.
				file_window = FileWindow(self.engine, file)		# Create fileWindow.
				self.file_window_list.append(file_window)
				file_window.update()											# Update fileWindow contents.
			except IsADirectoryError:
				pass

		if self.file_window_list != []:
			self.engine.set("current_file_window", self.file_window_list[0])
		else: # filewindow list can be empty if provided arg is a directory and no other filename args are given
			file = File("untitled.txt")
#			self.files.append(file)
			file_window = FileWindow(self.engine, file)
			self.file_window_list.append(file_window)
			file_window.update()
			self.engine.set("current_file_window", self.file_window_list[0])

	def update(self):
		self.engine.get("current_file_window").update()
		pass

	def terminate(self):
		pass
