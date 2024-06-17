from veno.modules.window import Window
class ConfigCustomizerWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		self.intended_y	= self.intended_x = 0
		self.intended_width		= self.getScreenMaxX()
		self.intended_height	= self.getScreenMaxY()

		self.is_open = False

		self.window.erase()
		self.keepWindowInMainScreen()

		if not self.is_open:
			self.panel.hide()
		else:
			self.panel.top()

		self.current_option = 0
		self.viewport_y = 0

		self.top_text_tip = " (Press Ctrl-/ or Ctrl-C to dismiss, Enter or Space to enter sub-menus, scroll and change values with arrow keys) "

		## Config instance.
		self.config = self.engine.get("config")
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
			self.panel.show()
			self.editDict(self.config.options, "CONFIG CUSTOMIZER")

	def bind(self):
		self.bindings = {
			"^_":        self.closeCurrentCustomizer,
			"^[":        self.closeCurrentCustomizer,
			"KEY_LEFT":  self.decrementConfigValue,
			"KEY_RIGHT": self.incrementConfigValue,
			"KEY_UP":    self.moveCurrentOptionUp,
			"KEY_DOWN":  self.moveCurrentOptionDown,
			"^J":        self.descendIntoDict,
			" ":         self.descendIntoDict
		}

	def closeCurrentCustomizer(self, d, name): #d unused; passed to all customizer keybinding functions
		if name == "CONFIG CUSTOMIZER":
			self.toggle()
			self.panel.hide()
		elif name == "COLOR CUSTOMIZER":
			self.intended_x = 0
			self.window.mvwin(0, 0) # for some reason, despite intended_x being 0, kWIMS() does not move it upon leaving a method...
			#self.keepWindowInMainScreen()

		self.current_option = 0
		self.viewport_y = 0

	def decrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if datatype == "bool":
			d[option_keys[self.current_option]] = not d[option_keys[self.current_option]]

		elif datatype == "int":
			if d[option_keys[self.current_option]] > 0:
				d[option_keys[self.current_option]] -= 1

	def incrementConfigValue(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if datatype == "bool":
			d[option_keys[self.current_option]] = not d[option_keys[self.current_option]]

		elif datatype == "int":
			d[option_keys[self.current_option]] += 1

	def moveCurrentOptionUp(self, d, name): #d, name unused; passed to all customizer keybinding functions
		if self.current_option > 0:
			self.current_option -= 1
			if self.current_option < self.viewport_y:
				#self.viewport_y-=1
				self.viewport_y -= self.viewport_y - self.current_option
			if self.current_option > self.getWindowMaxY() + self.viewport_y - 3:
				self.viewport_y += self.current_option - self.viewport_y

	def moveCurrentOptionDown(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		if self.current_option < len(option_keys) - 1: 
			self.current_option += 1
			#if self.getWindowMaxY() == 6:
				#exit()
			if self.current_option > self.getWindowMaxY() + self.viewport_y - 3:
				self.viewport_y += self.current_option - self.viewport_y

	def descendIntoDict(self, d, name): #name unused; passed to all customizer keybinding functions
		option_keys = list(d.keys())
		datatype = str(type(d[option_keys[self.current_option]])).split("'")[1]

		if datatype == "dict":
			if option_keys[self.current_option] == "ColorMap": # custom ColorMap config logic, window resizes to see color changes realtime
				self.editDict(d[option_keys[self.current_option]], "COLOR CUSTOMIZER")
			else:
				self.editDict(d[option_keys[self.current_option]])


	def toggle(self):
		if self.is_open:
			self.is_open = False
		else:
			self.is_open = True

	def editDict(self, d, name="CONFIG DICTIONARY EDITOR"):
		self.window.erase()
		self.current_option = 0
		self.viewport_y = 0
		self.intended_x = 0
		self.intended_width = self.getScreenMaxX()
		self.intended_height = self.getScreenMaxY()

		option_keys = list(d.keys())

		if name == "COLOR CUSTOMIZER":
			self.intended_height = len(option_keys) + 2
			self.intended_width = max(len(str(len(option_keys)) + "\t#"), len("COLOR CUSTOMIZER") + 2)
			# intended_width explained: d.keys will return a number with as many digits..
			self.intended_x = int(self.getScreenMaxX() / 2 - (self.intended_width / 2))
		
		self.keepWindowInMainScreen()
			
		# HAVE to consider screensize. self.window.getmaxyx() at this point should be happily computed.
		# if we wanna config on small displays, do we need scrolling?.....
		# yes. we can do that after we get it displaying based on maxyx.
		if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
			return # window is too small to print anything so quit while we're ahead.
			
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
			tab_expand_size = self.config.options["TabSize"]
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
				self.window.addnstr(i, 1, line_string, self.getWindowMaxX() - 2)

				if name == "COLOR CUSTOMIZER" and self.getWindowMaxX() > len(line_string) + 1:
					self.window.chgat(i, color_highlight_index, len(option_value_string), self.engine.curses.color_pair(option_value))

			else: # it is a dict or list
				self.window.addnstr(i, 1, object_string, self.getWindowMaxX() - 2)

			if self.current_option == option_index:
				self.window.chgat(i, 1, min(self.getWindowMaxX() - 2, len(option_string)), self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)

		self.window.box()
		top_text = name
		if name != "COLOR CUSTOMIZER":
			top_text += self.top_text_tip
		self.window.addnstr(0, 1, top_text, self.getWindowMaxX() - 2, self.engine.curses.A_STANDOUT)
		self.engine.update()
		
		while True:
			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				self.current_option = 0
				self.viewport_y = 0
				if name == "CONFIG CUSTOMIZER":
					self.toggle()
					self.panel.hide()
				elif name == "COLOR CUSTOMIZER":
					self.intended_x = 0
					self.window.mvwin(0, 0) # for some reason, despite intended_x being 0, kWIMS() does not move it upon leaving a method...
					#self.keepWindowInMainScreen()
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")
			if self.getWindowMaxY() <= 2 or self.getWindowMaxX() <= 2:
				#self.toggle() # window is too small to print anything so quit while we're ahead.
				#self.panel.hide()
				#break
				continue

			if c in self.bindings:
				self.bindings[c](d, name)
				if c == "^_" or c == "^[":
					break

			self.intended_width = self.getScreenMaxX()
			self.intended_height = self.getScreenMaxY()
			self.intended_x = 0

			if name == "COLOR CUSTOMIZER":
				self.intended_height = len(d.keys()) + 2
				self.intended_width = max(len(str(len(d.keys())) + "\t#"), len("COLOR CUSTOMIZER") + 2)
				# intended_width explained: d.keys will return a number with as many digits..
				self.intended_x = int(self.getScreenMaxX() / 2 - (self.intended_width / 2))

			self.keepWindowInMainScreen()
			self.window.clear()
			
			for i in range(1, self.getWindowMaxY() - 1): # for each line of window after title text				
				tab_expand_size = self.config.options["TabSize"]
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
					self.window.addnstr(i, 1, line_string, self.getWindowMaxX() - 2)
					if name == "COLOR CUSTOMIZER" and self.getWindowMaxX() > len(line_string) + 1:
						self.window.chgat(i, color_highlight_index, len(option_value_string), self.engine.curses.color_pair(option_value))

				else: # it is a dict or list
					self.window.addnstr(i, 1, object_string, self.getWindowMaxX() - 2)

				if self.current_option == option_index:
					self.window.chgat(i, 1, min(self.getWindowMaxX() - 2, len(option_string)), self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)

			self.window.box()
			top_text = name
			if name != "COLOR CUSTOMIZER":
				top_text += self.top_text_tip
			self.window.addnstr(0, 1, top_text, self.getWindowMaxX() - 2, self.engine.curses.A_STANDOUT)
				
			for i in self.engine.global_objects:
				if not issubclass(type(self.engine.get(i)), Window):
					continue
				if i == "configcustomizer": # this module file name
					continue # to avoid recursive loop

				self.engine.get(i).update()

			self.engine.get("syntaxhighlighting").update()
			self.engine.update()

		self.config.save()
		self.engine.update()

	def terminate(self):
		pass
