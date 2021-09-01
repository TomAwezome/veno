##
## @brief      Class for file.
##
class File:
	##
	## @brief      Constructs the object.
	##
	## @param      self    The object
	## @param      source  The file location as a string
	##
	def __init__(self, source):
		self.source = source	# source should be a filename string
		try:
			file = open(source)
			self.exists = True
			self.contents = file.read()
			file.close()
		except TypeError:
			self.contents = ""
			self.source = ""
			self.exists = False
		except FileNotFoundError:
			self.contents = ""
			self.exists = False

	##
	## @brief      save altered contents to File
	##
	## @param      self        The object
	## @param      fileString  The altered contents
	##
	def save(self, fileString):
		if self.source != "":
			file = open(self.source, "w")
			file.write(fileString)
			file.close()

	##
	## @brief      terminates File
	##
	## @param      self  The object
	##
	## @return     None
	##
	def terminate(self):
		pass
