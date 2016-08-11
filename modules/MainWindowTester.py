import time

def start(venicGlobals):
	testWindow = venicGlobals["curses"].newwin(venicGlobals["curses"].LINES, venicGlobals["curses"].COLS,0,0)
	testWindow.erase()
	testWindow.box()
	testWindow.addstr("wowie bucko")
	testPanel = venicGlobals["panel"].new_panel(testWindow)
	venicGlobals["testpanel"] = testPanel
	venicGlobals["testwindow"] = testWindow	
	venicGlobals["yes"] = "yes"
	testPanel.bottom()
def loop(venicGlobals):
	venicGlobals["testwindow"].addstr(5,5,"lol what")
	time.sleep(1)
def kill(venicGlobals):
	pass
