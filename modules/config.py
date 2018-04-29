import json
from pathlib import Path

##
## @brief      Class for config stuff.
##
class Config:
	##
	## @brief      Constructs the object.
	##
	## @param      self    The object
	##
	def __init__(self):
		self.defaultOptions = {"TabExpandSize": 4,
							   "UseLineWrap": False,
							   "LineWrapLength": 100}
		try:
			home = str(Path.home())
			file = open(home + "/.veno")
			self.text = file.read()
			# read json text for config options
			try:
				self.options = json.loads(self.text)
			except:
				self.options = self.defaultOptions
			file.close()
		except FileNotFoundError:
			# make json text for config options
			self.text = ""
			self.exists = False
			self.options = self.defaultOptions
			self.text = json.dumps(self.options, sort_keys=True, indent=4, separators=(',', ': '))
			home = str(Path.home())
			file = open(home+'/.veno', "w")
			file.write(self.text)
			file.close()


	def save(self):
		pass
		# if self.exists:
		# if self.source != "":
		# 	file = open(self.source, "w")
		# 	file.write(fileString)
		# 	file.close()
		# else:
		# 	# magic Bar request filename
		# 	file = open(self.source, "w")
		# 	file.write(fileString)
		# 	file.close()


	## @brief      terminates Config
	##
	## @param      self  The object
	##
	## @return     None
	##
	def terminate(self):
		pass