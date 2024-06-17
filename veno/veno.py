#!/usr/bin/env python3
import traceback, sys
from cProfile import Profile

# set to True to enable profiler and report information on program exit
is_profiling = False

if is_profiling:
	prof = Profile()
	prof.enable()

def profPrintStats():
	if is_profiling:
		for entry in sorted(prof.getstats(), key=lambda e:e.totaltime, reverse=True)[:20]:
			c = entry.code
			if not isinstance(c, str):
				c = f"{c.co_name:<32}Line {c.co_firstlineno:<5} of {c.co_filename}"
			print(f" {round(entry.totaltime, 4):<9}", c)

class EngineException(Exception):
	pass

from veno.modules.engine import Engine
engine = Engine()

engine.setException(EngineException)

result = 0
while True:
	try:
		engine.turn()
	except EngineException:
		engine.terminate()
		break
	except:
		engine.terminate()
		print("")
		highlight = engine.get("pygments_func_highlight")
		if highlight is not None:
			lexer = engine.get("pygments_pytb_lexer")
			formatter = engine.get("pygments_term_formatter")
			trace = highlight(traceback.format_exc(), lexer, formatter)
			print(trace)
		else:
			traceback.print_exc()  # Print the exception
		result = -1
		break

profPrintStats()
sys.exit(result)

