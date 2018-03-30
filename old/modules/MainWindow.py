def start(venicGlobals):
	import curses.panel as panel
	curses = venicGlobals["curses"]
	stdscr = curses.initscr()
	curses.start_color()
	curses.use_default_colors()
	for i in range(0,curses.COLORS):
		curses.init_pair(i+1,i,-1)
	global curses, panel, stdscr
	venicGlobals["panel"] = panel
	venicGlobals["stdscr"] = stdscr
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)
	curses.curs_set(0)
def loop(venicGlobals):
	panel.update_panels()
	stdscr.refresh()
def kill(venicGlobals):
	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()
	curses.endwin()

