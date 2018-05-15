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
							   "LineWrapLength": 100,
							   "ColorMap": {
											"0":9,
											"1":9,
											"2":10,#class,def,try,if,break,while,for,ints,pass
											"3":9,
											"4":9,
											"5":11,#quotes
											"6":10,#in,and,or
											"7":11,#class/function name, 
											"8":9,
											"9":9,
											"10":4,#self,modules,literals
											"11":9,
											"12":9,
											"13":9,
											"14":9,
											"15":9 # Comments. This color.
											}
		}
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
			self.options = self.defaultOptions
			self.text = json.dumps(self.options, sort_keys=True, indent=4, separators=(',', ': '))
			home = str(Path.home())
			file = open(home+'/.veno', "w")
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