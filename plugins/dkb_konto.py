from abstract import CSVConverter

DESC = '"Buchungstag";"Wertstellung";"Buchungstext";"Auftraggeber/Begünstigter";"Verwendungszweck";"Kontonummer";"BLZ";"Betrag (EUR)";\n'
class DKBKonto(CSVConverter):
	"""docstring for DKB"""

	FILE_ENCODING = "latin-1"
	DATE_FORMAT = "%d.%m.%Y"
	AMOUNT_INDEX = 6
	DATE_INDEX = 1
	DELIMITER = ";"
	STRIP = '"'
	def __init__(self, filename):
		super(DKBKonto, self).__init__(filename)
	
	def check(self):
# 1 "Kontonummer:";"12774055 / Internet-Konto";
# 2
# 3 "Von:";"27.12.2012";
# 4 "Bis:";"04.01.2013";
# 5 "Kontostand vom:";"500,00";
# 6
# 7 "Buchungstag";"Wertstellung";"Buchungstext";"Auftraggeber/Begünstigter";"Verwendungszweck";"Kontonummer";"BLZ";"Betrag (EUR)";
# 8 "04.01.2013";"04.01.2013";"LASTSCHRIFT";"AZ REAL ESTATE GERMANY";"X X 01.01.13-31.01.13-GM WOHNEN 01.01.13-31.01.13-VZ BK 01.01.13-31.01.13-VZ HK X ";"905001200";"60080000";"-1.091,00";
		def get_data(line, assert_type=None, convert=lambda x:x):
			csv_type, value = list(map(lambda x:x.strip('"'), line.strip(";\n").split(";")))
			if assert_type:
				assert csv_type == assert_type
			return convert(value) 
		try:
			firstline = self.fh.readline()
			# print(firstline)
			assert firstline.startswith('"Kontonummer:"')
			assert self.fh.readline() == '\n'
			von = get_data(self.fh.readline(), assert_type="Von:", convert=self.to_date)
			bis = get_data(self.fh.readline(), assert_type="Bis:", convert=self.to_date)
			# saldo = get_data(self.fh.readline(), assert_type="Saldo:")
			datum = get_data(self.fh.readline(), assert_type="Kontostand vom:")
			assert self.fh.readline() == '\n'
			desc = self.fh.readline()
			assert desc == DESC, "\n%r\n%r" % ( desc, DESC)
		except Exception as e:
			self.fh.close()
			print(e)
			raise
			return False
		return True
