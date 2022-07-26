class Debug:
	def __init__(self, engine):
		self.text = ""
		self.count = 0

	def log(self, data):
		self.count += 1
		count_text = f"{self.count}: ".rjust(5)
		self.text += f"\nDEBUG MSG {count_text} {str(data)}"

	def terminate(self):
		pass

