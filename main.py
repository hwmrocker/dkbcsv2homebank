from plugins import DKBVisa, PersonalExpense

if __name__ == "__main__":
	cvo = DKBVisa("inout/visa.csv")
	cvo.convert_to("inout/new.csv")
	