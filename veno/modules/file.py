class File:
	def __init__(self, source):
		self.source = source	# source should be a filename string, I'm assuming it'll end up being relative...
		file = open(source);
		self.contents = file.read()
		file.close()
	def save(self, fileString):
		file = open(self.source, "w")
		file.write(fileString)
		file.close()
	def terminate(self):
		pass