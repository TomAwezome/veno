"""
TODO:
 - make Ctrl-V to paste at prompt and sequence cursors from the last filewindow copylines
 - fix Ctrl-C exits without wait for join thread...
 - implement ask and confirm before overwrite existing sequence name
"""

import string, shlex, subprocess, traceback, threading

from modules.window import Window
class RunWindow(Window):
	def __init__(self, engine):
		Window.__init__(self, engine)

		self.config = self.engine.get("config").options

		self.file_window = self.engine.get("current_file_window")

		self.help_text = """
The RunWindow has 3 parts: prompt, sequence edit, and output.

When the RunWindow opens, it opens to a prompt for typing a
command into the 'Run command:' option, or selecting a 
Command Sequence to launch. If no Command Sequences have been
defined, none will appear.

Selecting 'Add Sequence' or pressing Space on an existing
Command Sequence will open the sequence editor, where
commands can be entered that will be sequentially run
whenever the sequence is run.

After creating a sequence and returning to the prompt or typing
a command directly at the 'Run command:' prompt, pressing
Enter while it is selected will launch the command/sequence
and display its output to the body of the RunWindow.
The RunWindow output display implements threading, so
the stdout output can be scrolled in real-time
while commands are still being executed.

		"""

		self.run_prompt_cursor_x = 0
		self.run_string = ""
		self.run_output = ""
		self.run_prompt_choice = 0

		self.run_sequence_choice = 0
		self.run_sequence_cursor_x = 0

		self.is_open = False

		self.bind()

		self.view_y = 0
		self.view_x = 0

		self.spinner_chars = ['/', '-', '\\' , '|']
		self.spinner_index = 0

		self.panel.hide()

	def update(self):
		self.window.erase()
		self.intended_x			= 0
		self.intended_y			= 0
		self.intended_width		= self.getScreenMaxX() - 1
		self.intended_height	= self.getScreenMaxY() - 1
		self.keepWindowInMainScreen()
		self.window.box()
		self.engine.update()
		self.file_window = self.engine.get("current_file_window")
		
		if not self.is_open:
			if not self.panel.hidden:
				self.panel.hide()		
		else:
			self.panel.show()
			self.runPrompt()

	def bind(self):
		self.run_prompt_bindings = {
			"KEY_LEFT":  self.moveRunPromptCursorLeft,
			"KEY_RIGHT": self.moveRunPromptCursorRight,
			"KEY_UP":    self.moveRunPromptChoiceUp,
			"KEY_DOWN":  self.moveRunPromptChoiceDown,
			"printable-character":  self.enterTextAtRunPromptCursor,
			"KEY_BACKSPACE":        self.backspaceAtRunPromptCursor,
			"^?":                   self.backspaceAtRunPromptCursor,
			"^H":                   self.backspaceAtRunPromptCursor,
			"KEY_DC":               self.deleteAtRunPromptCursor,
			"^D":                   self.deleteAtRunPromptCursor,
			"KEY_END":              self.jumpRunPromptCursorToEnd,
			"KEY_HOME":             self.jumpRunPromptCursorToStart,
		}
		self.run_output_bindings = {
			"KEY_LEFT":  self.moveViewLeft,
			"KEY_RIGHT": self.moveViewRight,
			"KEY_UP":    self.moveViewUp,
			"KEY_DOWN":  self.moveViewDown,
			"KEY_NPAGE": self.scrollViewDown,
			"KEY_PPAGE": self.scrollViewUp,
		}
		self.run_help_bindings = {
			"KEY_LEFT":  self.moveViewLeft,
			"KEY_RIGHT": self.moveViewRight,
			"KEY_UP":    self.moveViewUp,
			"KEY_DOWN":  self.moveViewDown,
		}
		self.run_sequence_bindings = {
			"KEY_LEFT":  self.moveRunSequenceCursorLeft,
			"KEY_RIGHT": self.moveRunSequenceCursorRight,
			"KEY_UP":    self.moveRunSequenceChoiceUp,
			"KEY_DOWN":  self.moveRunSequenceChoiceDown,
			"KEY_END":   self.jumpRunSequenceCursorToEnd,
			"KEY_HOME":  self.jumpRunSequenceCursorToStart,
			"^J":        self.selectRunSequenceChoice,
			"^D":        self.deleteRunSequenceCommandChoice,
			"^N":        self.insertRunSequenceCommandAtChoice,
			"KEY_IC":    self.insertRunSequenceCommandAtChoice,
			"printable-character":  self.enterTextAtRunSequenceCursor,
			"KEY_BACKSPACE":        self.backspaceAtRunSequenceCursor,
			"^?":                   self.backspaceAtRunSequenceCursor,
			"^H":                   self.backspaceAtRunSequenceCursor,
			"KEY_DC":               self.deleteAtRunSequenceCursor,
		}

	def moveViewUp(self):
		if self.view_y > 0:
			self.view_y -= 1

	def moveViewDown(self):
		self.view_y += 1

	def moveViewLeft(self):
		if self.view_x > 0:
			self.view_x -= 1

	def moveViewRight(self):
		self.view_x += 1

	def scrollViewDown(self):
		scroll_amount = self.config["ScrollAmount"]
		self.view_y += scroll_amount

	def scrollViewUp(self):
		scroll_amount = self.config["ScrollAmount"]
		self.view_y = max(0, self.view_y - scroll_amount)

	def moveRunPromptChoiceUp(self):
		self.run_prompt_choice = max(0, self.run_prompt_choice - 1)

	def moveRunPromptChoiceDown(self):
		sequence_count = 0
		if "CommandSequences" in self.config:
			for sequence in self.config["CommandSequences"]:
				sequence_count += 1

		# +1 for Run command:, +2 for Add Sequence... and Help...
		choice_count = 1 + sequence_count + 2
		self.run_prompt_choice = min(choice_count - 1, self.run_prompt_choice + 1)
		# choice_count - 1 to cap at max index

	def moveRunPromptCursorLeft(self):
		if self.run_prompt_choice == 0:
			self.run_prompt_cursor_x = max(0, self.run_prompt_cursor_x - 1)

	def moveRunPromptCursorRight(self):
		if self.run_prompt_choice == 0:
			self.run_prompt_cursor_x = min(len(self.run_string), self.run_prompt_cursor_x + 1)

	def jumpRunPromptCursorToStart(self):
		if self.run_prompt_choice == 0:
			self.run_prompt_cursor_x = 0

	def jumpRunPromptCursorToEnd(self):
		if self.run_prompt_choice == 0:
			self.run_prompt_cursor_x = len(self.run_string)

	def enterTextAtRunPromptCursor(self, c):
		if self.run_prompt_choice == 0:
			run_string_left = self.run_string[:self.run_prompt_cursor_x] + c
			run_string_right = self.run_string[self.run_prompt_cursor_x:]
			self.run_string = run_string_left + run_string_right
			self.run_prompt_cursor_x += 1

	def backspaceAtRunPromptCursor(self):
		if self.run_prompt_choice == 0 and self.run_prompt_cursor_x > 0:
			run_string_left = self.run_string[:self.run_prompt_cursor_x - 1]
			run_string_right = self.run_string[self.run_prompt_cursor_x:]
			self.run_string = run_string_left + run_string_right
			self.run_prompt_cursor_x -= 1
		elif self.run_prompt_choice != 0:
			sequence_count = 0
			if "CommandSequences" in self.config:
				for sequence in self.config["CommandSequences"]:
					sequence_count += 1
			choice_count = 1 + sequence_count + 2 # +1 for Run command:, +2 for Add Sequence... and Help...
			if self.run_prompt_choice < choice_count - 2:
				i = 0
				for name, sequence in self.config["CommandSequences"].items():
					if i == self.run_prompt_choice - 1:
						break
					i += 1
				self.config["CommandSequences"].pop(name)
				self.engine.get("config").save()

	def deleteAtRunPromptCursor(self):
		if self.run_prompt_choice == 0 and self.run_prompt_cursor_x + 1 <= len(self.run_string):
			run_string_left = self.run_string[:self.run_prompt_cursor_x]
			run_string_right = self.run_string[self.run_prompt_cursor_x + 1:]
			self.run_string = run_string_left + run_string_right
		elif self.run_prompt_choice != 0:
			sequence_count = 0
			if "CommandSequences" in self.config:
				for sequence in self.config["CommandSequences"]:
					sequence_count += 1
			choice_count = 1 + sequence_count + 2 # +1 for Run command:, +2 for Add Sequence... and Help...
			if self.run_prompt_choice < choice_count - 2:
				i = 0
				for name, sequence in self.config["CommandSequences"].items():
					if i == self.run_prompt_choice - 1:
						break
					i += 1

				# confirm before removing the Command Sequence
				while True:
					self.keepWindowInMainScreen()
					self.window.erase()
					self.window.box()
					self.window.addnstr(1, 1, f"Delete Commmand Sequence '{name}' ? (Y/N)", self.getWindowMaxX() - 1, self.engine.curses.color_pair(4) | self.engine.curses.A_REVERSE)
					self.engine.update()

					try:
						c = self.engine.screen.getch()
					except KeyboardInterrupt:
						return
					if c == -1:
						continue
					c = self.engine.curses.keyname(c)
					c = c.decode("utf-8")
					if c.lower() == 'n':
						return
					if c.lower() == "y":
						break
					if c == "^[": # ESC
						return

				self.config["CommandSequences"].pop(name)
				self.engine.get("config").save()

	def moveRunSequenceChoiceUp(self, sequence, text_list):
		self.run_sequence_cursor_x = 0
		self.run_sequence_choice = max(0, self.run_sequence_choice - 1)

	def moveRunSequenceChoiceDown(self, sequence, text_list):
		self.run_sequence_cursor_x = 0
		# +1 for Name:, +2 for Add Command... and Help...
		choice_count = 1 + len(sequence) + 2
		self.run_sequence_choice = min(choice_count - 1, self.run_sequence_choice + 1)
		# choice_count - 1 to cap at max index

	def moveRunSequenceCursorLeft(self, sequence, text_list):
		self.run_sequence_cursor_x = max(0, self.run_sequence_cursor_x - 1)

	def moveRunSequenceCursorRight(self, sequence, text_list):
		text = text_list[0]
		self.run_sequence_cursor_x = min(len(text), self.run_sequence_cursor_x + 1)

	def jumpRunSequenceCursorToStart(self, sequence, text_list):
		self.run_sequence_cursor_x = 0

	def jumpRunSequenceCursorToEnd(self, sequence, text_list):
		text = text_list[0]
		self.run_sequence_cursor_x = len(text)

	def selectRunSequenceChoice(self, sequence, text_list):
		choice_count = 1 + len(sequence) + 2 # +1 for Name:, +2 for Add Command... and Help...
		if self.run_sequence_choice == choice_count - 1: # Help... (choice_count - 1 to cap at max index)
			self.showHelp()
		elif self.run_sequence_choice == choice_count - 2: # Add Command...
			sequence.append("")
		elif self.run_sequence_choice > 0 and self.run_sequence_choice < len(sequence) + 1:
			sequence.insert(self.run_sequence_choice, "")
			self.run_sequence_choice += 1
			self.run_sequence_cursor_x = 0

	def deleteRunSequenceCommandChoice(self, sequence, text_list):
		if self.run_sequence_choice > 0 and self.run_sequence_choice < len(sequence) + 1:
			sequence.pop(self.run_sequence_choice - 1)

	def insertRunSequenceCommandAtChoice(self, sequence, text_list):
		if self.run_sequence_choice > 0 and self.run_sequence_choice < len(sequence) + 1:
			sequence.insert(self.run_sequence_choice - 1, "")

	def enterTextAtRunSequenceCursor(self, sequence, text_list, c):
		text = text_list[0]
		text = text[:self.run_sequence_cursor_x] + c + text[self.run_sequence_cursor_x:]
		if self.run_sequence_choice == 0: # Name:
			self.run_sequence_cursor_x += 1
			text_list[0] = text
		elif self.run_sequence_choice < len(sequence) + 1:
			sequence[self.run_sequence_choice - 1] = text
			self.run_sequence_cursor_x += 1

	def backspaceAtRunSequenceCursor(self, sequence, text_list):
		text = text_list[0]
		text = text[:self.run_sequence_cursor_x - 1] + text[self.run_sequence_cursor_x:]
		if self.run_sequence_choice == 0: # Name:
			if self.run_sequence_cursor_x > 0:
				self.run_sequence_cursor_x -= 1
				text_list[0] = text
		elif self.run_sequence_choice < len(sequence) + 1:
			if self.run_sequence_cursor_x > 0:
				sequence[self.run_sequence_choice - 1] = text
				self.run_sequence_cursor_x -= 1

	def deleteAtRunSequenceCursor(self, sequence, text_list):
		text = text_list[0]
		if self.run_sequence_cursor_x + 1 <= len(text):
			text = text[:self.run_sequence_cursor_x] + text[self.run_sequence_cursor_x + 1:]
			if self.run_sequence_choice == 0: # Name:
				text_list[0] = text
			elif self.run_sequence_choice < len(sequence) + 1:
				sequence[self.run_sequence_choice - 1] = text

	def runPrompt(self):
		self.config = self.engine.get("config").options
		self.run_prompt_choice = 0
		top_text = " RUN (Press F2/Ctrl-C to dismiss, Enter to select, Space to edit Sequence, Delete/Backspace/Ctrl-D to delete Sequence, scroll with arrow keys) "

		while True: # break out of this loop with enter key
			self.window.erase()
			self.window.box()

			choice_lines = []
			choice_lines.append("Run command: " + self.run_string)

			sequence_count = 0
			if "CommandSequences" in self.config:
				for name, commands in self.config["CommandSequences"].items():
					choice_lines.append(f"Run Sequence '{name}': {commands}")
					sequence_count += 1
			
			choice_lines.append("Add Sequence...")
			choice_lines.append("Help...")

			choice_count = 1 + sequence_count + 2 # +1 for Run command:, +2 for Add Sequence... and Help...

			window_max_x = self.getWindowMaxX()
			window_max_y = self.getWindowMaxY()
			if window_max_y - 1 > 1:
				self.window.addnstr(0, 1, top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)

			window_y = 1
			for line in choice_lines:
				self.window.addnstr(window_y, 1, line, self.getWindowMaxX() - 2, self.engine.curses.color_pair(0))
				if window_y - 1 == self.run_prompt_choice:
					self.window.chgat(window_y, 1, min(self.getWindowMaxX() - 2, len(line)), self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)
				window_y += 1

			if self.run_prompt_choice == 0 and self.run_prompt_cursor_x + len("Run command: ") + 1 <= self.getWindowMaxX() - 2 and self.run_prompt_cursor_x >= 0:
				self.window.chgat(1, self.run_prompt_cursor_x + len("Run command: ") + 1, 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)

			self.engine.update()

			try:
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue
			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.run_prompt_bindings:
				self.run_prompt_bindings[c]()
			elif self.run_prompt_choice == 0 and c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.run_prompt_bindings["printable-character"](c)
			elif c == "^J": # enter key
				if self.run_prompt_choice == 0:
					if self.run_string != "":
						self.runSingleCommand()
					else:
						continue
				elif self.run_prompt_choice == choice_count - 1: # Help... (choice_count - 1 to cap at max index)
					self.showHelp()
				elif self.run_prompt_choice == choice_count - 2: # Add Sequence...
					self.addSequence()
				else: # cursor on a Command Sequence choice to run
					self.runCommandSequence()
			elif c == " " and self.run_prompt_choice >= 1 and self.run_prompt_choice < choice_count - 2:
				i = 0
				for name, sequence in self.config["CommandSequences"].items():
					if i == self.run_prompt_choice - 1:
						break
					i += 1
				self.editSequence(sequence, name)
			elif c == "KEY_F(2)" or c == "^[": # ESC
				break

			self.engine.update()

		self.panel.hide()
		self.toggle()

	def readRunOutput(self, process):
		for line in iter(process.stdout.readline, ''):
			self.run_output += line

	def runCommandSequence(self):
		i = 0
		for name, sequence in self.config["CommandSequences"].items():
			if i == self.run_prompt_choice - 1:
				break
			i += 1

		process = thread = None
		top_text = " RUN OUTPUT (Press F2/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys/PageUp/PageDown) "

		run_string = ""
		i = 1
		if len(sequence) > 0:
			for command in sequence[:-1]:
				if command == '':
					i += 1
					continue
				# TODO: detect command lines ending in & or ;, skip add the && just space it
				run_string += f"echo '' \n\n echo Command {i}: {command} \n\n echo '' \n\n " + command + " \n\n " 
				i += 1
			run_string += f"echo '' \n\n echo Command {i}: {sequence[-1]} \n\n echo '' \n\n " + sequence[-1]
		else:
			run_string = "echo Error: Command Sequence has no commands."

		if run_string != "":
			self.run_output = '\nRun sequence: ' + str(sequence) + '\n'
			
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY()
			self.window.mvwin(0, 0)
			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.box()
			self.engine.update()

			error_text = ""
			try:
				command_num = 1
				for command in sequence:
					args = shlex.split(command)
					command_num += 1
				command = None 
				process = subprocess.Popen(run_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=1, shell=True)
				thread = threading.Thread(target=self.readRunOutput, args=(process,))
				thread.start()
			except:
				if command: # would be None if args shlex check success, value on error
					error_text += f"at Command {command_num}: {command}"
				self.run_output = traceback.format_exc() + error_text

			self.view_y = 0
			self.view_x = 0

			while True:
				lines = self.run_output.split('\n')

				self.intended_x			= 0
				self.intended_y			= 0
				self.intended_width		= self.getScreenMaxX() - 1
				self.intended_height	= self.getScreenMaxY()

				self.keepWindowInMainScreen()
				self.window.erase()
				self.window.box()
				window_y = 1
				window_max_y = self.getWindowMaxY()
				window_max_x = self.getWindowMaxX()
				if window_max_y - 1 > 1:
					self.window.addnstr(0, 1, top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)
				for line in lines[self.view_y:]:
					line = line.expandtabs(self.config["TabSize"])[self.view_x:]
					if window_y >= window_max_y - 1:
						break
					self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
					window_y += 1

				if process and process.poll() is None:
					self.window.addnstr(0, 0, self.spinner_chars[self.spinner_index], 1, self.engine.curses.color_pair(0))
					self.spinner_index += 1
					if self.spinner_index >= len(self.spinner_chars):
						self.spinner_index = 0

				self.engine.update()
				
				try:
					self.engine.screen.timeout(60)
					c = self.engine.screen.getch()
				except KeyboardInterrupt:
					break
				if c == -1:
					continue

				c = self.engine.curses.keyname(c)
				c = c.decode("utf-8")

				if c in self.run_output_bindings:
					self.run_output_bindings[c]()

				if c == "^J" or c == "KEY_F(2)" or c == " " or c == "^[":
					break
		if thread:
			thread.join()
		self.keepWindowInMainScreen()

	def addSequence(self):
		if "CommandSequences" not in self.config:
			self.config["CommandSequences"] = {}
			self.engine.get("config").save()

		new_sequence = []
		new_sequence_name = ""
		
		self.editSequence(new_sequence, new_sequence_name)

	def editSequence(self, sequence, name):
		top_text = " EDIT COMMAND SEQUENCE (Press F2/Ctrl-C to save & dismiss, Enter to select/create command, Ctrl-D to delete command, Ctrl-N to insert command, scroll with arrow keys) "
		self.run_sequence_choice = 0
		self.run_sequence_cursor_x = 0

		while True:
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY()

			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.box()
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()
			if window_max_y - 1 > 1:
				self.window.addnstr(0, 1, top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)

			choice_lines = []
			choice_lines.append("Sequence Name: " + name)
			command_num = 1
			for command in sequence:
				choice_lines.append("Command " + f"{command_num}: ".rjust(4) + command)
				command_num += 1
			choice_lines.append("Add Command...")
			choice_lines.append("Help...")

			window_y = 1
			for line in choice_lines:
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line, self.getWindowMaxX() - 2, self.engine.curses.color_pair(0))
				if window_y - 1 == self.run_sequence_choice:
					self.window.chgat(window_y, 1, min(self.getWindowMaxX() - 2, len(line)), self.engine.curses.color_pair(3) | self.engine.curses.A_REVERSE)
				if window_y - 1 == self.run_sequence_choice and self.run_sequence_choice < len(sequence) + 1 and self.run_prompt_cursor_x + len("Run command: ") + 1 <= self.getWindowMaxX() - 2:
					if self.run_sequence_choice == 0:
						x = self.run_sequence_cursor_x + len("Sequence Name: ") + 1
					else:
						x = self.run_sequence_cursor_x + len("Command ##: ") + 1
					if x < self.getWindowMaxX() - 2:
						self.window.chgat(window_y, x, 1, self.engine.curses.color_pair(2) | self.engine.curses.A_REVERSE)
				window_y += 1

			self.engine.update()
			
			try:
				self.engine.screen.timeout(60)
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			text_list = []
			if self.run_sequence_choice == 0:
				text_list.append(name)
			elif self.run_sequence_choice < len(sequence) + 1:
				text_list.append(sequence[self.run_sequence_choice - 1])
			else:
				text_list.append(name)

			if c in self.run_sequence_bindings:
				last_choice = self.run_sequence_choice
				self.run_sequence_bindings[c](sequence, text_list)
				if self.run_sequence_choice == 0 and last_choice == self.run_sequence_choice:
					name = text_list[0]
			elif c in string.punctuation + string.digits + string.ascii_letters + string.whitespace:
				self.run_sequence_bindings["printable-character"](sequence, text_list, c)
				if self.run_sequence_choice == 0:
					name = text_list[0]

			elif c == "KEY_F(2)" or c == "^[":
				break

		self.config["CommandSequences"][name] = sequence
		self.engine.get("config").save()

	def showHelp(self):
		top_text = " RUN HELP (Press F2/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys) "
		self.view_y = 0
		self.view_x = 0

		while True:
			lines = self.help_text.split('\n')

			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY()

			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.box()
			window_y = 1
			window_max_y = self.getWindowMaxY()
			window_max_x = self.getWindowMaxX()
			if window_max_y - 1 > 1:
				self.window.addnstr(0, 1, top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)
			for line in lines[self.view_y:]:
				line = line.expandtabs(self.config["TabSize"])[self.view_x:]
				if window_y >= window_max_y - 1:
					break
				self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
				window_y += 1

			self.engine.update()
			
			try:
				self.engine.screen.timeout(60)
				c = self.engine.screen.getch()
			except KeyboardInterrupt:
				break
			if c == -1:
				continue

			c = self.engine.curses.keyname(c)
			c = c.decode("utf-8")

			if c in self.run_help_bindings:
				self.run_help_bindings[c]()

			if c == "^J" or c == "KEY_F(2)" or c == " " or c == "^[":
				break

	def runSingleCommand(self):
		process = thread = None
		top_text = " RUN OUTPUT (Press F2/Ctrl-C/Enter/Space to dismiss, scroll with arrow keys/PageUp/PageDown) "

		if self.run_string != "":
			self.run_output = '\nRun command: ' + self.run_string + '\n\n'
			
			self.intended_x			= 0
			self.intended_y			= 0
			self.intended_width		= self.getScreenMaxX() - 1
			self.intended_height	= self.getScreenMaxY()
			self.window.mvwin(0, 0)
			self.keepWindowInMainScreen()
			self.window.erase()
			self.window.box()
			self.engine.update()

			try:
#				args = shlex.split(self.run_string)
				process = subprocess.Popen(self.run_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=1, shell=True)
				thread = threading.Thread(target=self.readRunOutput, args=(process,))
				thread.start()
			except:
				self.run_output = traceback.format_exc()

			self.view_y = 0
			self.view_x = 0

			while True:
				lines = self.run_output.split('\n')

				self.intended_x			= 0
				self.intended_y			= 0
				self.intended_width		= self.getScreenMaxX() - 1
				self.intended_height	= self.getScreenMaxY()

				self.keepWindowInMainScreen()
				self.window.erase()
				self.window.box()
				window_y = 1
				window_max_y = self.getWindowMaxY()
				window_max_x = self.getWindowMaxX()
				if window_max_y - 1 > 1:
					self.window.addnstr(0, 1, top_text, window_max_x - 2, self.engine.curses.color_pair(0) | self.engine.curses.A_REVERSE)
				for line in lines[self.view_y:]:
					line = line.expandtabs(self.config["TabSize"])[self.view_x:]
					if window_y >= window_max_y - 1:
						break
					self.window.addnstr(window_y, 1, line, window_max_x - 2, self.engine.curses.color_pair(0))
					window_y += 1

				if process and process.poll() is None:
					self.window.addnstr(0, 0, self.spinner_chars[self.spinner_index], 1, self.engine.curses.color_pair(0))
					self.spinner_index += 1
					if self.spinner_index >= len(self.spinner_chars):
						self.spinner_index = 0

				self.engine.update()
				
				try:
					self.engine.screen.timeout(60)
					c = self.engine.screen.getch()
				except KeyboardInterrupt:
					break
				if c == -1:
					continue

				c = self.engine.curses.keyname(c)
				c = c.decode("utf-8")

				if c in self.run_output_bindings:
					self.run_output_bindings[c]()

				if c == "^J" or c == "KEY_F(2)" or c == " " or c == "^[":
					break
		if thread:
			thread.join()
		self.keepWindowInMainScreen()

	def toggle(self):
		if self.is_open:
			self.is_open = False
		else:
			self.is_open = True

	def terminate(self):
		pass
