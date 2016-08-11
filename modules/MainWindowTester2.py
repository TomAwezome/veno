import time

def start(venicGlobals):
	global testWindow
	testWindow = venicGlobals["curses"].newwin(10, 10,9,9)
	testWindow.erase()
	testWindow.box()
	testWindow.addstr("wowie bucko2")
	testPanel = venicGlobals["panel"].new_panel(testWindow)
	venicGlobals["testpanel2"] = testPanel
#	venicGlobals["testwindow2"] = testWindow
	venicGlobals["yes2"] = "yes"
	testPanel.top()
def loop(venicGlobals):
	testWindow.addstr(5,5,"lol")
	time.sleep(1)
def kill(venicGlobals):
	pass
