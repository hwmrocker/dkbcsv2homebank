from abstract import CSVConverter

class DKBVisa(CSVConverter):
	"""docstring for DKB"""
	def __init__(self, arg):
		super(DKB, self).__init__()
		self.arg = arg

