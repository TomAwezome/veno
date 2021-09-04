import pygments
import pygments.lexers as lexers
from pygments.formatters import IRCFormatter

##
## @brief      Class for highlighter.
##
class Highlighter:
	##
	## @brief      Constructs the object.
	##
	## @param      self     This object
	## @param      manager  The manager to allow access to drawing on window object in FileWindow
	##
	def __init__(self, manager):
		## The manager to allow access to drawing on window object in FileWindow. TODO: replace manager with Window variable to further scale Highlighter
		self.manager = manager

		## Pygments formatter IRCFormatter
		self.irc = IRCFormatter

		## Lexer for filetype
		self.lexer = None

		## color_map dictionary with format of {"highlighterColorCode":RenderedColorCode}
		self.color_map = self.manager.get("config").options["ColorMap"]
		
		## FileWindow highlighter is attached to.
		self.file_window = self.manager.get("currentFileWindow")
		
		try:
			try:
				self.lexer = lexers.guess_lexer_for_filename(
						self.file_window.file.source,
						self.file_window.file.contents
					)
			except:
				self.lexer = lexers.guess_lexer(
						self.file_window.file.contents
					)
			if self.lexer.name == "PHP":
				self.lexer = lexers.PhpLexer(startinline=True)
		except:
			pass
		self.file_window.is_modified = True
	##
	## @brief      Update syntax highlighting on fileWindow
	##
	## @param      self  This object
	##
	def update(self):

		self.file_window = self.manager.get("currentFileWindow")

		viewport_x = self.file_window.getViewportX()
		viewport_y = self.file_window.getViewportY()
		window_max_y = self.file_window.getWindowMaxY()
		window_max_x = self.file_window.getWindowMaxX()
		window_code_lines = self.file_window.file_lines
		window_code_string = '\n'.join(window_code_lines)
		tab_expand_size = self.manager.get("config").options["TabExpandSize"]

		if self.lexer and self.file_window.is_modified:
			highlighted_code_string = pygments.highlight(window_code_string, self.lexer, self.irc())
			## **Highlighted** code lines from window_code_lines (which is default defined as file_lines[viewport_y:viewport_y + window_max_y])
			self.highlighted_code_lines = highlighted_code_string.split('\n')
			leading_newlines = 0
			for line in window_code_lines:
				if line == '':
					leading_newlines += 1
				else:
					break
			window_code_lines.reverse()
			trailing_newlines = 0
			for line in window_code_lines:
				if line == '':
					trailing_newlines += 1
				else:
					break
			window_code_lines.reverse()
			if trailing_newlines > 0:
				self.highlighted_code_lines.extend([''] * trailing_newlines)
			if leading_newlines > 0:
				self.highlighted_code_lines.reverse()
				self.highlighted_code_lines.extend([''] * leading_newlines)
				self.highlighted_code_lines.reverse()

			self.file_window.is_modified = False
		elif not self.lexer:
			highlighted_code_string = window_code_string
			self.highlighted_code_lines = highlighted_code_string.split('\n')
			
			
		window_y = viewport_y
		for line in self.highlighted_code_lines[window_y:window_y + window_max_y]:
			proper_line = line
			proper_line = proper_line.replace('\x1d', '')
			line_index = 0
			# at this point, each line is a string which has been colored, irregardless of the window x size
			# tabs are a \t character, and ctrl-C is a \x03 character; not expanded for tabs
			if '\x03' in proper_line:
				color_instances = proper_line.count('\x03')
				is_opener = is_closer = False
				opener_count = closer_count = 0
				color_data = [[]] # [[color, start, num]]
				color_data_row_index = 0
				while color_instances > 0:
					colorIndex = proper_line.find('\x03', line_index)
					line_index = colorIndex + 1
					# so what we want is this: start by checking for numbers (I THINK that pygments is working such that colors are simply one number, which uses two digits (none of that 3,5 crap))
					#			   if it's the number sequence we're expecting: that is now our point IN THE STRING DATA (NO TABS!) that our coloring begins
					#			   if there's no number sequence AFTER STARTING WITH A SEQUENCE: that is the point IN THE STRING DATA that our coloring stops
					# how to convert DATA index into TABBED index? after all, that's what's being tossed to the window we are changing the attributes of!
					# ... oh, do i need to subtract from the formatted string? given that its internal character indexes are technically being changed by the presence of ^C characters...
					window_line = window_code_lines[window_y][:colorIndex]
					if (colorIndex - (opener_count * 3) - closer_count) + (len(window_line.expandtabs(tab_expand_size)) - len(window_line)) - viewport_x > window_max_x:
					# if color is offscreen right	
						if is_closer and color_data[color_data_row_index][1] - viewport_x < window_max_x - 1:
						# if is closer, and opener is on screen
							color_data[color_data_row_index][1] = max(color_data[color_data_row_index][1] - viewport_x, 0)
							color_data[color_data_row_index].append(window_max_x + viewport_x - color_data[color_data_row_index][1])
							color_data_row_index += 1
							closer_count += 1
							is_closer = False
							color_data.append([])
						else:
						# else (is opener, or opener is also offscreen right)
							color_data.pop()
						break
					if not is_opener and not is_closer:
						if str.isdigit(proper_line[colorIndex + 1:colorIndex + 3]):
							is_opener = True
					if is_closer:
						if color_data[color_data_row_index][1] - viewport_x < 0:
						# if opener is offscreen
							if (colorIndex - (opener_count * 3) - closer_count) + (len(window_line.expandtabs(tab_expand_size)) - len(window_line)) - viewport_x > 0:
							# if closer is on screen
								color_data[color_data_row_index][1] = 0
								color_data[color_data_row_index].append((colorIndex - (opener_count * 3) - closer_count) + (len(window_line.expandtabs(tab_expand_size)) - len(window_line)) - viewport_x)
							else:
							# else (closer is not on screen)
								color_data.pop()
								color_data_row_index -= 1
						else:
						# else (opener is on screen)
							color_data[color_data_row_index].append((colorIndex - (opener_count * 3) - closer_count) + (len(window_line.expandtabs(tab_expand_size)) - len(window_line)) - color_data[color_data_row_index][1])
							color_data[color_data_row_index][1] = color_data[color_data_row_index][1] - viewport_x

						color_data_row_index += 1
						closer_count += 1
						is_closer = False
						color_data.append([])
					if is_opener:
						color_data[color_data_row_index].append(proper_line[colorIndex + 1:colorIndex + 3])
						color_data[color_data_row_index].append((colorIndex - (opener_count * 3) - closer_count) + (len(window_line.expandtabs(tab_expand_size)) - len(window_line)))
						opener_count += 1
						is_opener = False
						is_closer = True
					color_instances -= 1
				for row in color_data:
					if row != []:
						self.file_window.window.chgat(window_y - viewport_y, row[1], row[2], self.manager.curses.color_pair(self.color_map[str(int(row[0]))]))
			window_y += 1
			if window_y > viewport_y + window_max_y-1:
				break
		self.drawSelect()
		self.file_window.drawCursor()

	##
	## @brief      Terminates Highlighter
	##
	## @param      self  This object
	##
	def terminate(self):
		pass

	##
	## @brief      Highlight text between filecursor and selectPosition, this allows onscreen coloration to show what text is currently being selected.
	##
	## @param      self  This object
	##
	def drawSelect(self):

		self.file_window = self.manager.get("currentFileWindow")

		filecursor_x = self.file_window.getFilecursorX()
		filecursor_y = self.file_window.getFilecursorY()
		select_x = self.file_window.getSelectX()
		select_y = self.file_window.getSelectY()
		viewport_x = self.file_window.getViewportX()
		viewport_y = self.file_window.getViewportY()
		window_max_y = self.file_window.getWindowMaxY()
		tab_expand_size = self.manager.get("config").options["TabExpandSize"]

		if self.file_window.is_select_on:

			start_y = min(filecursor_y, select_y)
			end_y = max(filecursor_y, select_y)
			if start_y == end_y:
				start_x = min(filecursor_x, select_x)
				end_x = max(filecursor_x, select_x)
			elif start_y == filecursor_y:
				start_x = filecursor_x
				end_x = select_x
			elif start_y == select_y:
				start_x = select_x
				end_x = filecursor_x
					
			y_offset = 0
			for line in self.file_window.file_lines[viewport_y:viewport_y + window_max_y]: # for each line of window contents
				if viewport_y + y_offset in range(start_y, end_y + 1): # if selection on screen

					if start_y == end_y:
					# if start and end on same line
						# chgat blue from extendTabString[start[0]:end[0]]
						tab_diff = len(line[:start_x].expandtabs(tab_expand_size)) - len(line[:start_x])
						if start_x - viewport_x + tab_diff < 0:
						# if start is off screen
							chgx = 0 # start blue from left edge of window.
							chgl = end_x - viewport_x # this should work. but. end[0] doesn't care if tabs are before it, spacing bugged. need new/same tabdiff?
							tab_diff_end = len(line[:end_x].expandtabs(tab_expand_size)) - len(line[:end_x]) # similar tab difference but based on sel ends
							chgl += tab_diff_end
							if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
								chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						else:
						# else start is on screen
							chgx = start_x - viewport_x + tab_diff
							chgl = len(line[start_x:end_x].expandtabs(tab_expand_size))

						self.file_window.window.chgat(start_y - viewport_y, chgx, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)

					elif start_y == viewport_y + y_offset:
					# elif line is line that select starts on
						tab_diff = len(line[:start_x].expandtabs(tab_expand_size)) - len(line[:start_x])
						if start_x - viewport_x + tab_diff < 0:
						# if start is off screen
							chgx = 0
							chgl = len(line.expandtabs(tab_expand_size)) - viewport_x
							if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
								chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.
						else:
						# else start is on screen
							chgx = start_x - viewport_x + tab_diff
							chgl = len(line[start_x:].expandtabs(tab_expand_size))

						self.file_window.window.chgat(y_offset, chgx, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue from start[0] to end of line

					elif end_y == viewport_y + y_offset:
					# elif line is line that select ends on
						chgl = len(line[:end_x].expandtabs(tab_expand_size)) - viewport_x
						if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
							chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.

						self.file_window.window.chgat(y_offset, 0, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue from start to end[0] of line

					else:
					# elif line is between start and end
						chgl = len(line.expandtabs(tab_expand_size)) - viewport_x
						if chgl < 0: # as viewport scrolls right, highlight length calculation dips into negative once start and end are both off screen.
							chgl = 0 # this nulls the length argument of the chgat function, so anything from here is ensured not to change any characters.

						self.file_window.window.chgat(y_offset, 0, chgl, self.manager.curses.color_pair(5) | self.manager.curses.A_REVERSE)
						# chgat blue whole line

				y_offset += 1
