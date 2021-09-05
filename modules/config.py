import json, os
from pathlib import Path

##
## @brief      Class for config stuff.
##
class Config:
	##
	## @brief      Constructs this Config object.
	##
	## @param      self    This object
	##
	def __init__(self, filename):
		self.default_options = {
			"TabExpandSize": 4,
			"TabLength": 4,
			"LineWrapLength": 40,
			"AutoIndent": True,
			"UseLineWrap": False,
			"BracketMatching": True,
			"QuoteMatching": True,
			"ScrollAmount": 20,
			"LanguageOverrides": {
				"py": {
					"TabLength": "char"
				},
				"js": {
					"TabLength": 2
				}
			},
			"ColorMap": {
				"0": 7,
				"1": 7,
				"2": 2, # class, def, try, if, break, while, for, ints, pass
				"3": 7,
				"4": 7,
				"5": 3, # quotes
				"6": 2, # in, and, or
				"7": 5, #class/function name
				"8": 7,
				"9": 7,
				"10": 4, # self, modules, literals
				"11": 7,
				"12": 7,
				"13": 7,
				"14": 7,
				"15": 6 # Comments. This color.
			}
		}
		try:
			home = str(Path.home())
			file = open(home + "/.veno")
			self.text = file.read()
			file.close()

			# read json text for config options
			try:
				json_dict = json.loads(self.text) # load config json file in as dictionary
				self.options = {**self.default_options, **json_dict} # set config options as default options, overridden by config file settings
				if len(json_dict) < len(self.default_options): # if config file has less entries than default, .veno is old and will be updated
					self.save()
			except:
				self.options = self.default_options

		except FileNotFoundError:
			home = str(Path.home())
			file = open(home + '/.veno', "w")
			file.write("{}")
			self.options = self.default_options
			file.close()

		extension = os.path.splitext(filename)[1][1:]
		if extension in self.options["LanguageOverrides"]:
			self.options = {**self.options, **self.options["LanguageOverrides"][extension]}

	def save(self):
		self.text = json.dumps(self.options, sort_keys=True, indent=4, separators=(',', ': '))
		home = str(Path.home())
		file = open(home + '/.veno', "w")
		file.write(self.text)
		file.close()

	## @brief      terminates Config
	##
	## @param      self  This object
	##
	## @return     None
	##
	def terminate(self):
		pass
