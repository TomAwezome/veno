import json, os
from pathlib import Path
import copy

##
## @brief      Class for config stuff.
##
class Config:
	##
	## @brief      Constructs this Config object.
	##
	## @param      self    This object
	##
	def __init__(self, engine):
		self.engine = engine

		self.default_options = {
			"TabSize": 4,
			"TabCharMode": True,
			"LineWrapLength": 40,
			"AutoIndent": True,
			"ShowLineNumbers": True,
			"UseLineWrap": False,
			"BracketMatching": True,
			"QuoteMatching": True,
			"AngleBracketMatching": False,
			"FindRegexMode": False,
			"ReplaceRegexMode": False,
			"ScrollAmount": 20,
			"LanguageOverrides": {
				"py": {
					"TabCharMode": True,
					"TabSize": 4,
				},
				"js": {
					"TabCharMode": False,
					"TabSize": 2,
				}
			},
			"LexerOverride": "",
			"LexerOverrideMode": False,
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
				for ext, vals in self.default_options["LanguageOverrides"].items():
					if ext not in self.options["LanguageOverrides"]:
						self.options["LanguageOverrides"][ext] = vals
					for key, val in vals.items():
						if key not in self.options["LanguageOverrides"][ext]:
							self.options["LanguageOverrides"][ext][key] = val
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

		self.standard_options = copy.deepcopy(self.options) # backup a 'standard' config to use for filetypes with no overrides

		self.last_filename = current_filename = self.engine.filenames[0]
		extension = os.path.splitext(current_filename)[1][1:]
		if extension in self.options["LanguageOverrides"]:
			self.options = {**self.options, **self.options["LanguageOverrides"][extension]}

	def update(self):
		current_filename = self.engine.get("current_file_window").file.source
		if current_filename == self.last_filename:
			return # bail to save time
		self.last_filename = current_filename
		extension = os.path.splitext(current_filename)[1][1:]
		if extension in self.options["LanguageOverrides"]:
			self.options = {**self.options, **self.options["LanguageOverrides"][extension]}
		else: # if no overrides for current file, iterate through language overrides and reset config vals back to standard_options value if current values match overrides
			lang_changes = {}
			for ext in self.options["LanguageOverrides"]:
				for key in self.options["LanguageOverrides"][ext]:
					if key not in lang_changes:
						lang_changes[key] = []
					lang_changes[key].append(self.options["LanguageOverrides"][ext][key])
			for key, val in lang_changes.items():
				if key in self.options and key in self.standard_options and self.options[key] in val:
					self.options[key] = self.standard_options[key]

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
