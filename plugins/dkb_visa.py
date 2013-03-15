from abstract import CSVConverter

VISA_DESC = '"Umsatz abgerechnet";"Wertstellung";"Belegdatum";"Umsatzbeschreibung";"Betrag (EUR)";"Ursprünglicher Betrag";\n'
class DKBVisa(CSVConverter):
	"""docstring for DKB"""

	FILE_ENCODING = "latin-1"
	DATE_FORMAT = "%d.%m.%Y"
	AMOUNT_INDEX = 4
	DATE_INDEX = 1
	DELIMITER = ";"
	STRIP = '"'
	def __init__(self, filename):
		super(DKBVisa, self).__init__(filename)
	
	def check(self):
# 1 "Kreditkarte:";"4998************ Kreditkarte";
# 2
# 3 "Von:";"27.12.2012";
# 4 "Bis:";"04.01.2013";
# 5 "Saldo:";"11266.89 EUR";
# 6 "Datum:";"04.01.2013";
# 7 
# 8 "Umsatz abgerechnet";"Wertstellung";"Belegdatum";"Umsatzbeschreibung";"Betrag (EUR)";"Ursprünglicher Betrag";
# 9 "Nein";"04.01.2013";"03.01.2013";"Amazon EUAMAZON.DE";"-27,77";"";
		def get_data(line, assert_type=None, convert=lambda x:x):
			csv_type, value = list(map(lambda x:x.strip('"'), line.strip(";\n").split(";")))
			if assert_type:
				assert csv_type == assert_type
			return convert(value) 
		try:
			firstline = self.fh.readline()
			# print(firstline)
			assert firstline.startswith('"Kreditkarte:"')
			assert self.fh.readline() == '\n'
			von = get_data(self.fh.readline(), assert_type="Von:", convert=self.to_date)
			bis = get_data(self.fh.readline(), assert_type="Bis:", convert=self.to_date)
			saldo = get_data(self.fh.readline(), assert_type="Saldo:")
			datum = get_data(self.fh.readline(), assert_type="Datum:")
			assert self.fh.readline() == '\n'
			visa_desc = self.fh.readline()
			assert visa_desc == VISA_DESC, "\n%r\n%r" % ( visa_desc, VISA_DESC)
		except Exception as e:
			self.fh.close()
			print(e)
			raise
			return False
		return True
