from modules.window import Window
class ConfigCustomizerWindow(Window):
	def __init__(self, manager, name):
		Window.__init__(self, manager, name)
		self.intended_y = self.intended_x = 0
		self.intended_width = self.getStdscrMaxX()
		self.intended_height = self.getStdscrMaxY()
		self.is_open = False
		self.window.erase()
		self.keepWindowInMainScreen()

		if not self.is_open:
			self.panel.hide()
		else:
			self.panel.top()

		self.current_option = 0
		self.viewport_y = 0
		
		## Config instance.
		self.config = self.manager.Objects["config"]

		## ConfigCustomizer keybindings dictionary stores functions
		self.bindings = {}
		self.bind()

	def update(self):
		self.window.erase()
		self.keepWindowInMainScreen()
		
		if not self.is_open:
			if not self.panel.hidden:
				self.panel.hide()
		
		else:
			self.panel.top()
			self.editDict(self.config.options, "Config Customizer")

	def bind(self):
		self.bindings = {
			"^_":        self.closeCurrentCustomizer,
			"KEY_LEFT":  self.decrementConfigValue,
			"KEY_RIGHT": self.incrementConfigValue,
			"KEY_UP":    self.moveCurrentOptionUp,
			"KEY_DOWN":  self.moveCurrentOptionDown,
			"^J":        self.descendIntoDict,
			" ":         self.descendIntoDict
		}

	def closeCurrentCustomizer(self, d, name): #d unused; passed to all customizer keybinding functions
		if name == "Config Customizer":
			self.toggle()
			self.panel.hide()
		elif name == "Color Customizer":
			self.intended_x = 0
			self.window.mvwin(0, 0) # for some reason, despite intended_x being 0, kWIMS() does not move it upon leaving a method...
			#self.keepWindowInMainScreen()

		self.current_option = 0
		self.viewport_y = 0

	def decrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if option_keys[self.current_option] == "TabLength":
			# custom TabLength config logic
			if datatype == "int": # if TabLength is currently already an integer
				if d[option_keys[self.current_option]] > 1:
					d[option_keys[self.current_option]] -= 1
				else: # no TabLength zero, char instead
					d[option_keys[self.current_option]] = "char"

		elif datatype == "bool":
			d[option_keys[self.current_option]] = not d[option_keys[self.current_option]]

		elif datatype == "int":
			if d[option_keys[self.current_option]] > 0:
				d[option_keys[self.current_option]] -= 1

	def incrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if option_keys[self.current_option] == "TabLength": # custom TabLength config logic
			if d[option_keys[self.current_option]] == "char":
				d[option_keys[self.current_option]] = 1
			elif datatype == "int": # if TabLength is currently already an integer
				d[option_keys[self.current_option]] += 1

		elif datatype == "bool":
			d[option_keys[self.current_option]] = not d[option_keys[self.current_option]]

		elif datatype == "int":
			d[option_keys[self.current_option]] += 1

	def moveCurrentOptionUp(self, d, name): #d, name unused; passed to all customizer keybinding functions
		if self.current_option > 0:
			self.current_option -= 1
			if self.current_option < self.viewport_y:
				#self.viewport_y-=1
				self.viewport_y -= self.viewport_y - self.current_option
			if self.current_option > self.getWindowMaxY() + self.viewport_y - 4:
				self.viewport_y += self.current_option - self.viewport_y

	def moveCurrentOptionDown(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		if self.current_option < len(option_keys) - 1: 
			self.current_option += 1
			#if self.getWindowMaxY() == 6:
				#exit()
			if self.current_option > self.getWindowMaxY() + self.viewport_y - 4:
				self.viewport_y += self.current_option - self.viewport_y

	def descendIntoDict(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if datatype == "dict":
			if option_keys[self.current_option] == "ColorMap": # custom ColorMap config logic, window resizes to see color changes realtime
				self.editDict(d[option_keys[self.current_option]], "Color Customizer")
			else:
				self.editDict(d[option_keys[self.current_option]])


	def toggle(self):
		if self.is_open:
			self.is_open = False
		else:
			self.is_open = True

	def editDict(self, d, name="Dictionary Editor"):
		self.window.erase()
		self.current_option = 0
		self.viewport_y = 0
		self.intended_x = 0
		self.intended_width = self.getStdscrMaxX()
		self.intended_height = self.getStdscrMaxY()

		option_keys = list(d.keys())

		if name == "Color Customizer":
			self.intended_height = len(option_keys) + 3
			self.intended_width = max(len(str(len(option_keys)) + "\t#"), len("Color Customizer") + 2)
			# intended_width explained: d.keys will return a number with as many digits..
			self.intended_x = int(self.getStdscrMaxX() / 2 - (self.intended_width / 2))
		
		self.keepWindowInMainScreen()
		self.window.box()
			
		# HAVE to consider screensize. self.window.getmaxyx() at this point should be happily computed.
		# if we wanna config on small displays, do we need scrolling?.....
		# yes. we can do that after we get it displaying based on maxyx.
		if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
			return # window is too small to print anything so quit while we're ahead.

		self.window.addnstr(1, 1, name, self.getWindowMaxX() - 2, self.manager.curses.A_STANDOUT)
			
		# Explaining some possibly hard to read code;
		# this for loop increments i over a range of 1...windowMaxY to do the following with i:
		# 1) ensure that i+viewport_y (to be used in option_keys index) won't exceed option_keys max index
		# 2) check type of value at option_keys[i+viewport_y-1], if dict or list, show value as ...
		#    (... is to indicate that another config menu will come up and pressing Enter is needed.)
		# 3) add text to screen row i+1 for windowMaxX-2 characters
		#    (+1 since title takes up row 1, row 0 is box but accounted for since range begins at 1)
		#    (-2 since text is offset by 1 to not print over box, and to not print on the box 1 off from the right border)
		# 4) if current line in loop is one with current_option on it, highlight the key text

		for i in range(1, self.getWindowMaxY() - 1): # for each line of window after title text
			tab_expand_size = self.config.options["TabExpandSize"]
			option_index = i + self.viewport_y - 1
			if option_index >= len(option_keys):
				break
			option_string = option_keys[option_index]
			option_value = d[option_string]
			option_value_string = str(option_value)
			option_type = str(type(option_value)).split("'")[1]
			line_string = str(option_string + "\t" + option_value_string).expandtabs(tab_expand_size)
			object_string = str(option_string + "\t...").expandtabs(tab_expand_size)
			color_highlight_index = len(str(option_string + "\t").expandtabs(tab_expand_size)) + 1

			if option_type != "dict" and option_type != "list":
				self.window.addnstr(i + 1, 1, line_string, self.getWindowMaxX() - 2)

				if name == "Color Customizer" and self.getWindowMaxX() > len(line_string) + 1:
					self.window.chgat(i + 1, color_highlight_index, len(option_value_string), self.manager.curses.color_pair(option_value))

			else: # it is a dict or list
				self.window.addnstr(i + 1, 1, object_string, self.getWindowMaxX() - 2)

			if self.current_option == option_index:
				self.window.chgat(i + 1, 1, min(self.getWindowMaxX() - 2, len(option_string)), self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

		self.window.box()
		self.manager.update()
		
		while True:
			try:
				c = self.manager.stdscr.getch()
			except KeyboardInterrupt:
				self.current_option = 0
				self.viewport_y = 0
				if name == "Config Customizer":
					self.toggle()
					self.panel.hide()
				elif name == "Color Customizer":
					self.intended_x = 0
					self.window.mvwin(0, 0) # for some reason, despite intended_x being 0, kWIMS() does not move it upon leaving a method...
					#self.keepWindowInMainScreen()
				break
			if c == -1:
				continue

			c = self.manager.curses.keyname(c)
			c = c.decode("utf-8")
			if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
				#self.toggle() # window is too small to print anything so quit while we're ahead.
				#self.panel.hide()
				#break
				continue

			if c in self.bindings:
				self.bindings[c](d, name)
				if c == "^_":
					break

			self.intended_width = self.getStdscrMaxX()
			self.intended_height = self.getStdscrMaxY()
			self.intended_x = 0

			if name == "Color Customizer":
				self.intended_height = len(d.keys()) + 3
				self.intended_width = max(len(str(len(d.keys())) + "\t#"), len("Color Customizer") + 2)
				# intended_width explained: d.keys will return a number with as many digits..
				self.intended_x = int(self.getStdscrMaxX() / 2 - (self.intended_width / 2))

			self.keepWindowInMainScreen()
			self.window.clear()
			
			self.window.addnstr(1, 1, name, self.getWindowMaxX() - 2, self.manager.curses.A_STANDOUT)
			for i in range(1, self.getWindowMaxY() - 1): # for each line of window after title text				
				tab_expand_size = self.config.options["TabExpandSize"]
				option_index = i + self.viewport_y - 1				
				if option_index >= len(option_keys):
					break
				option_string = option_keys[option_index]
				option_value = d[option_string]
				option_value_string = str(option_value)
				option_type = str(type(option_value)).split("'")[1]
				line_string = str(option_string + "\t" + option_value_string).expandtabs(tab_expand_size)
				object_string = str(option_string + "\t...").expandtabs(tab_expand_size)
				color_highlight_index = len(str(option_string + "\t").expandtabs(tab_expand_size)) + 1

			
				if option_type != "dict" and option_type != "list":
					self.window.addnstr(i + 1, 1, line_string, self.getWindowMaxX() - 2)
					if name == "Color Customizer" and self.getWindowMaxX() > len(line_string) + 1:
						self.window.chgat(i + 1, color_highlight_index, len(option_value_string), self.manager.curses.color_pair(option_value))

				else: # it is a dict or list
					self.window.addnstr(i + 1, 1, object_string, self.getWindowMaxX() - 2)

				if self.current_option == option_index:
					self.window.chgat(i + 1, 1, min(self.getWindowMaxX() - 2, len(option_string)), self.manager.curses.color_pair(3) | self.manager.curses.A_REVERSE)

			self.window.box()
				
			for i in self.manager.Windows:
				if self.manager.Windows[i].name == "configCustomizer": # name given in engine init
					continue # to avoid recursive loop

				self.manager.Windows[i].update()

			self.manager.Objects["highlighter"].update()
			self.manager.update()

		self.config.save()
		self.manager.update()

	def terminate(self):
		pass
