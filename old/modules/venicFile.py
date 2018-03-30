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
	try:
		try:
			venicGlobals["lexer"] = venicGlobals["pygments"].lexers.guess_lexer_for_filename(args.filename,fileString)
		except:
			venicGlobals["lexer"] = venicGlobals["pygments"].lexers.guess_lexer(fileString)
		if venicGlobals["lexer"].name == "PHP":
			venicGlobals["lexer"] = venicGlobals["pygments"].lexers.PhpLexer(startinline=True)
	except:
		venicGlobals["lexer"] = None
def loop(venicGlobals):
	pass
def kill(venicGlobals):
	pass
