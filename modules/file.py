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
		## source should be a file location as String.
		self.source = source
		if source != None:
			file = open(source);
		## contents of file as String
			self.contents = file.read()
			file.close()
		else:
			self.contents = ""
			self.source = "veno.save.tmp"
	##
	## @brief      save altered contents to File
	##
	## @param      self        The object
	## @param      fileString  The altered contents
	##

	def save(self, fileString):
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