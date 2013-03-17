from abstract import CSVConverter, PAYMODE_CASH

class PersonalExpense(CSVConverter):
	DATE_FORMAT = "%Y-%m-%d"
	AMOUNT_INDEX = 2
	DATE_INDEX = 3
	TRANSACTION_ORDER = ["paymode","info","payee","description","category"]

	def __init__(self, filename):
		super(PersonalExpense, self).__init__(filename)

	def check(self):
		line = next(self.fh).strip()
		# print(line.count(","))
		assert line.count(",") == 3
		cat, subcat, amount, date = line.split(",")
		# print(amount)
		# print(self.to_decimal(amount))
		try:
			# self.to_decimal("2012-01-12")
			self.to_decimal(amount)
			self.to_date(date)
		except:
			return False
		return True

	def get_paymode(self, elements, transaction_dict):
		return PAYMODE_CASH

	def get_info(self, elements, transaction_dict):
		return

	def get_payee(self, elements, transaction_dict):
		return

	def get_description(self, elements, transaction_dict):
		return

	def get_category(self, elements, transaction_dict):
		return