def start(venicGlobals):
	import argparse # venic is required to be started with a filename, need to parse the arg for it
	parser = argparse.ArgumentParser()      # initialize argument parser
	parser.add_argument("filename") # add an argument to our program, we need a file
	args = parser.parse_args()      # actually parse the arguments Venic was given
	file = open(args.filename)
	fileString = file.read()
	file.close()
	venicGlobals["venicFile"] = fileString
	venicGlobals["venicFileName"] = args.filename
def loop(venicGlobals):
	pass
def kill(venicGlobals):
	pass
