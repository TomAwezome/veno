import string
def start(venicGlobals):
	import os
	global keybindingModules, keybindingNameList
	keybindingListFile = open(venicGlobals["modulesDir"] + "/keybindings/enabled")
	keybindingFileList = [line.rstrip('\n') for line in keybindingListFile]
	keybindingListFile.close()
	
	keybindingNameList = []
	keybindingModules = {}
	
	for keybindingModule in keybindingFileList:
		keybindingName = keybindingModule
		if "ctrl-" in keybindingModule:
			keybindingName = "^"+keybindingModule[5:]
		keybindingModules[keybindingName] = venicGlobals["importlib"].import_module("modules.keybindings."+keybindingModule)
		keybindingNameList.append(keybindingName)
#		print(keybindingName)
def loop(venicGlobals):
	c = venicGlobals["stdscr"].getch()
	if c == -1:
		return
	else:
		pass
	c = venicGlobals["curses"].keyname(c)
	c = c.decode("utf-8")
		
	# so somehow, maybe in a similar way to how the module stuff worked, I need to grab the keybinding python files that have
	# their function calls to various global things, and interpret them based on name(?) and the getkey() value of c
	if c in keybindingNameList:
		keybindingModules[c].run(venicGlobals["modules"])
	elif c in string.punctuation + string.digits + string.ascii_letters + " \t":
		keybindingModules["printable-character"].run(venicGlobals["modules"], c)

def kill(venicGlobals):
	pass
