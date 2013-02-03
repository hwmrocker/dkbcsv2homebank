#!/usr/bin/env python3

# http://homebank.free.fr/help/06csvformat.html

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

def split_line(line):
	"""returns a list csv elements"""
	# it removes semicolons from the end of the line first
	# print("%r" % line.strip(";").split(";"))
	return list(map(lambda x:x.strip('"'), line.strip(";\n").split(";")))

def get_data(line, assert_type=None, convert=lambda x:x):
	csv_type, value = split_line(line)
	if assert_type:
		assert csv_type == assert_type
	return convert(value) 

def to_string(value):
	return value

def to_decimal(value):
	if " " in value:
		value, _ = value.split(" ", 1)
	return Decimal(value.replace(",", "."))

def to_date(value):
	return datetime.strptime(value, "%d.%m.%Y")

def get_string_until(astr, break_chars=" 123456780,;.-", valid_char=lambda x: True):
	ret = []
	for char in astr:
		if valid_char(char) and char not in break_chars:
			ret.append(char)
		else:
			break
	return "".join(ret)

def guess_paymode(payee, description, default=PAYMODE_NONE):
	if payee in ("HVB", "STADTSPARKASSE", "AUSZAHLUNG"):
		return PAYMODE_INTERNAL_TRANSFER
	if payee == "DKB":
		return PAYMODE_FEE
	return default

def guess_payee(description):
	name = get_string_until(description)
	if name == "":
		return "DKB"

	return name.upper()

def guess_category(payee, description, last_catergory=""):
	if payee == "WEBFACTION":
		return "Homepage:webfaction"
	if payee == "GH":
		return "Homepage:github"
	elif payee == "DB":
		return "Travel:Train"
	elif payee == "GOOGLE":
		if "Music" in description:
			return "Multimedia:Music"
	elif payee == "HabenzinsenZ":
		return "Zins"
	elif payee == "DKB":
		if "für Auslandseinsatz" in description: 
			return last_catergory or "Transaction Fee"
	elif "HUMBLE" in payee:
		return "hobby:games"
	return ""


def convert_csv(csv_filename):
	with open(csv_filename, encoding="latin-1") as csv_fh:
		account_type, account_info = split_line(csv_fh.readline())

		it = get_transactions_visadkb(csv_fh)
		von, bis = next(it)
		fn = "dkbvisa_%s-%s.csv" % (von.strftime("%y%m%d"), bis.strftime("%y%m%d"))
		with open(fn, "w") as fh:
			# fh.write(Transaction.csv_head)
			for transaction in it:
				fh.write(transaction.to_csv())

def convert_awd_csv(csv_filename):
	with open(csv_filename) as csv_fh:
		with open("awd.csv", "w") as fh:
			for transaction in get_transactions_awd(csv_fh):
				fh.write(transaction.to_csv())


def guess_awd_category(category, payee):
	if category in ("grocery", "lunch", "dine out"):
		return "food:%s" % category
	if category == "travel":
		return "%s:%s" % (category, payee)
	return category

def guess_awd_payee(payee=""):
	if payee.lower() == "other":
		return ""
	return payee.upper()

# 1 'lunch,Pepenero,7,2012-12-19\n'
def get_transactions_awd(csv_fh):
	for line in csv_fh:
		major_cat, minor_cat, amount, date_str = line.strip('\n').split(',')
		payee = guess_awd_payee(minor_cat)
		category = guess_awd_category(major_cat, payee)
		date = datetime.strptime(date_str, "%Y-%m-%d")
		amount = -Decimal(amount)  
		if category == "income":
			amount = -amount
		yield Transaction(payee=payee, category=category, date=date, amount=amount, paymode=PAYMODE_CASH)
# 1 "Kreditkarte:";"4998************ Kreditkarte";
# 2
# 3 "Von:";"27.12.2012";
# 4 "Bis:";"04.01.2013";
# 5 "Saldo:";"11266.89 EUR";
# 6 "Datum:";"04.01.2013";
# 7 
# 8 "Umsatz abgerechnet";"Wertstellung";"Belegdatum";"Umsatzbeschreibung";"Betrag (EUR)";"Ursprünglicher Betrag";
# 9 "Nein";"04.01.2013";"03.01.2013";"Amazon EUAMAZON.DE";"-27,77";"";
VISA_DESC = '"Umsatz abgerechnet";"Wertstellung";"Belegdatum";"Umsatzbeschreibung";"Betrag (EUR)";"Ursprünglicher Betrag";\n'
def get_transactions_visadkb(csv_fh):
	assert csv_fh.readline() == '\n'
	von = get_data(csv_fh.readline(), assert_type="Von:", convert=to_date)
	bis = get_data(csv_fh.readline(), assert_type="Bis:", convert=to_date)
	saldo = get_data(csv_fh.readline(), assert_type="Saldo:")
	datum = get_data(csv_fh.readline(), assert_type="Datum:")
	assert csv_fh.readline() == '\n'
	visa_desc = csv_fh.readline()
	assert visa_desc == VISA_DESC, "\n%r\n%r" % ( visa_desc, VISA_DESC)

	yield (von, bis)
	last_catergory = ""
	for line in csv_fh:
		wertstellung, beschreibung, betrag = get_dkbvisa_transaction(line)
		payee = guess_payee(beschreibung)
		category = guess_category(payee, beschreibung, last_catergory=last_catergory)
		paymode = guess_paymode(payee, beschreibung, default=PAYMODE_CREDIT_CARD)
		t = Transaction(date=wertstellung, amount=betrag, description=beschreibung, 
			payee=payee, category=category, paymode=paymode)
		yield t
		#print(t.to_csv())

def get_dkbvisa_transaction(line):
	convert_l = [to_date, to_string, to_decimal]
	_, wertstellung, _, beschreibung, betrag, urspruenglich = split_line(line)
	if urspruenglich:
		beschreibung += " ursprünglich %s" % urspruenglich
	return list(map(lambda x:x[0](x[1]), zip(convert_l, [wertstellung, beschreibung, betrag])))


# 1 "Kontonummer:";"12774055 / Internet-Konto";
# 2
# 3 "Von:";"27.12.2012";
# 4 "Bis:";"04.01.2013";
# 5 "Kontostand vom:";"500,00";
# 6
# 7 "Buchungstag";"Wertstellung";"Buchungstext";"Auftraggeber/Begünstigter";"Verwendungszweck";"Kontonummer";"BLZ";"Betrag (EUR)";
# 8 "04.01.2013";"04.01.2013";"LASTSCHRIFT";"AZ REAL ESTATE GERMANY";"X X 01.01.13-31.01.13-GM WOHNEN 01.01.13-31.01.13-VZ BK 01.01.13-31.01.13-VZ HK X ";"905001200";"60080000";"-1.091,00";


# Column list:
#         date ; paymode ; info ; payee ; description ; amount ; category

#         Values:
#         date     => format should be DD-MM-YY
#         mode     => from 0=none to 10=FI fee
#         info     => a string
#         payee    => a payee name
#         description  => a string
#         amount   => a number with a '.' as decimal separator, ex: -24.12 or 36.75
#         category => a full category name (category, or category:subcategory)

if __name__ == "__main__":
	convert_awd_csv("inout/awd.csv")