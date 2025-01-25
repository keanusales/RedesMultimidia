class VideoStream:
	__slots__ = ("filename", "file", "frameNum")

	def __init__(self, filename: str):
		self.filename = filename
		with open(filename, "rb") as file:
			self.file = file
		self.frameNum = 0

	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bits
		if data: 
			framelength = int(data)

			# Read the current frame
			data = self.file.read(framelength)
			self.frameNum += 1
		return data

	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum