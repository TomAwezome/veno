##
## @brief      Class for file.
##
class File:
	##
	## @brief      Constructs this File object.
	##
	## @param      self    This object
	## @param      source  The file location as a string
	##
	def __init__(self, source):
		self.source = source
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
	## @brief      Save altered contents to File
	##
	## @param      self        This object
	## @param      fileString  The altered contents as a string
	##
	def save(self, fileString):
		if self.source != "":
			file = open(self.source, "w")
			file.write(fileString)
			file.close()

	##
	## @brief      Terminate this File
	##
	## @param      self  This object
	##
	## @return     None
	##
	def terminate(self):
		pass
