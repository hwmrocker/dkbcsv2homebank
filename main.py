from plugins import DKBVisa, PersonalExpense, DKBKonto

if __name__ == "__main__":
	cvo = DKBKonto("inout/konto.csv")
	cvo.convert_to("inout/new.csv")
	