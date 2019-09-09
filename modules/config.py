import json
import os
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
	def __init__(self, filename):
		self.defaultOptions = {
			"TabExpandSize": 4,
			"TabLength": 4,
			"UseLineWrap": False,
			"LineWrapLength": 100,
			"LanguageOverrides": {
				"py": {
					"TabLength": "char"
				},
				"js": {
					"TabLength": 2
				}
			},
			"ColorMap": {
				"0": 8,
				"1": 8,
				"2": 2,#class,def,try,if,break,while,for,ints,pass
				"3": 8,
				"4": 8,
				"5": 3,#quotes
				"6": 2,#in,and,or
				"7": 3,#class/function name, 
				"8": 8,
				"9": 8,
				"10": 4,#self,modules,literals
				"11": 8,
				"12": 8,
				"13": 8,
				"14": 8,
				"15": 1 # Comments. This color.
			}
		}
		try:
			home = str(Path.home())
			file = open(home + "/.veno")
			self.text = file.read()
			# read json text for config options
			try:
				self.options = {**self.defaultOptions, **json.loads(self.text)}
			except:
				self.options = self.defaultOptions
			file.close()
		except FileNotFoundError:
			home = str(Path.home())
			file = open(home+'/.veno', "w")
			file.write("{}")
			self.options = self.defaultOptions
			file.close()
		extension = os.path.splitext(filename)[1][1:]
		if extension in self.options["LanguageOverrides"]:
			self.options = {**self.options, **self.options["LanguageOverrides"][extension]}
	def save(self):
		self.text = json.dumps(self.options, sort_keys=True, indent=4, separators=(',', ': '))
		home = str(Path.home())
		file = open(home+'/.veno',"w")
		file.write(self.text)
		file.close()

	## @brief      terminates Config
	##
	## @param      self  The object
	##
	## @return     None
	##
	def terminate(self):
		pass
