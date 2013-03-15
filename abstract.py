from decimal import Decimal
from datetime import datetime

PAYMODES = ["None",   #  0
"Credit Card",        #  1
"Check",              #  2
"Cash",               #  3
"Transfer",           #  4
"Internal Transfer",  #  5
"Debit Card",         #  6
"Standing Order",     #  7
"Electronic Payment", #  8
"Deposit",            #  9
"FI Fees"]            # 10
PAYMODE_NONE = 0
PAYMODE_CREDIT_CARD = 1
PAYMODE_CASH = 3
PAYMODE_INTERNAL_TRANSFER = 5
PAYMODE_EINZUG = 8
PAYMODE_FEE = 10

class Transaction(object):
	csv_head = "date;paymode;info;payee;description;amount;category\n"
	def __init__(self, date, amount, **kw):
		#date ; paymode ; info ; payee ; description ; amount ; category
		self.date = date
		self.paymode = kw.get('paymode', PAYMODE_NONE)
		self.info = kw.get('info', "")
		self.payee = kw.get('payee', "Unknown")
		self.description = kw.get('description', "")
		self.amount = amount
		self.category = kw.get('category', "")
		self.data = ["date", "paymode", "info", "payee", "description",
			"amount", "category"]

	def _get_csv_date(self):
		return self.date.strftime("%d-%m-%y")
	def _get_csv_paymode(self):
		return str(self.paymode)
	def _get_csv_info(self):
		return self.info
	def _get_csv_payee(self):
		return self.payee
	def _get_csv_description(self):
		return self.description
	def _get_csv_amount(self):
		return "%.2f" % self.amount
	def _get_csv_category(self):
		return self.category

	def to_csv(self):
		return "%s\n"% ";".join(map(
			lambda x: getattr(self, "_get_csv_%s" % x)(), 
			self.data))

class WrongCSVConverterError(Exception): pass

class CSVConverter(object):
	DATE_FORMAT = "%d.%m.%Y"
	DELIMITER = ","
	TRANSACTION_ORDER = ["paymode","info","payee","description","category"]
	FILE_ENCODING = "utf8"

	"""docstring for CSVConverter"""
	def __init__(self, filename):
		self.fh = open(filename, encoding=self.FILE_ENCODING)
		if not self.check():
			self.fh.close()
			raise WrongCSVConverterError
		# self.seekToData()

	@classmethod
	def check(cls, filename):
		raise NotImplementedError

	def getTransactions(self):
		"""is an iterator that returns all Transactions from the file"""
		for line in self.fh:
			yield self.lineToTransaction(line.strip())

	def convert_to(self, new_filename):
		with open(new_filename, "w") as fh:
			for transaction in self.getTransactions():
				fh.write(transaction.to_csv())
		fh.close()

	def to_string(self, value):
	 	return value

	def to_decimal(self, value):
		if " " in value:
			value, _ = value.split(" ", 1)
		return Decimal(value.replace(",", "."))

	def to_date(self, value):
		return datetime.strptime(value, self.DATE_FORMAT)



		