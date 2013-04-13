import getopt, sys, re, os

#trida zastupujici strukturu s parametry
class parameters:
    def __init__(self):
        self.inputf=False
        self.outputf=False
        self.h=False
        self.noSubDir=False
        self.k=False
        self.o=False
        self.i=False
        self.w=False
        self.c=False
        self.p=False
#Funkce pro vytvoreni vyctoveho typu
def enum(**enums):
    return type('Enum', (), enums)

#vycet pro reprezentaci chybovych stavu
errors = enum(EPAR=1, EIFILE=2, EOFILE=3, EWRONGIFILE=4, ESPEC=10)

###############################################
# Funkce pro tisk helpmsg
###############################################
def usage():
	print ("\nProgram C Stats v pythonu")
	print ("Barbora Skrivankova, xskriv01@stud.fit.vutbr.cz")
	print ("Pouziti: python ./cst.py (-h|--help) --input=fileordir --output=file [--nosubdir] (-k|-o|-i|-w|-c) [-p]\n")
	print ("\t\t-h, --help: vypise tuto napovedu a skonci program")
	print ("\t\t--input=fileordir: specifikace vstupniho souboru nebo adresare k analyze")
	print ("\t\t--output=file: specifikace vystupniho souboru")
	print ("\t\t--nosubdir: zakazani rekurzivniho prohledavani adresaru")
	print ("\t\t\t nelze kombinovat s input=file")
	print ("\t\t-k: probehne vypocet pro klicova slova")
	print ("\t\t-o: probehne vypocet pro jednoduche operatory")
	print ("\t\t-i: probehne vypocet pro identifikatory")
	print ("\t\t-w=pattern: vyhleda textovy retezec pattern a vypise pocet vyskytu")
	print ("\t\t-c: probehne vypocet pro znaky komentaru")
	print ("\t\t\tPrave jeden z -k, -o, -i, -w -c musi byt zadan")
	print ("\t\t-p: ve vypisech zrusi absolutni cesty k souborum")

ePrints = {errors.EPAR: "Chybne zadane parametry.",
			errors.EIFILE: "Chyba pri otevreni vstupniho souboru.",
			errors.EOFILE: "Chyba pri pristupu do vystupniho souboru.",
			errors.EWRONGIFILE: "Chybny format vystupniho souboru.",
			errors.ESPEC: "Jina specificka chyba..."}
	
def printErrExit(eCode):
	print (ePrints[eCode])
	usage()
	sys.exit(eCode)

###############################################
# GetParamsFunction
###############################################
def getParams():
	params=parameters()
	for p in sys.argv[1:]:
		if p in ("-h", "--help"):
			if params.h:
				printErrExit(errors.EPAR)
			params.h = True
		elif  re.match(r'--input=\S+', p):
			if params.inputf or params.h:
				printErrExit(errors.EPAR)
			params.inputf = p[8:]
		elif p == "--nosubdir":
			if params.h:
				printErrExit(errors.EPAR)
			params.noSubDir = True
		elif re.match(r'--output=\S+', p):
			if params.output or params.h:
				printErrExit(errors.EPAR)
			params.outputf = p[10:]
		elif p == "-k":
			if params.h or params.o or params.i or params.w or params.c or params.p:
				printErrExit(errors.EPAR)
			params.k = True
		elif p == "-o":
			if params.h or params.k or params.i or params.w or params.c or params.p:
				printErrExit(errors.EPAR)
			params.o = True
		elif p == "-i":
			if params.h or params.k or params.o or params.w or params.c or params.p:
				printErrExit(errors.EPAR)
			params.i = True
		elif p == "-w":
			if params.h or params.k or params.o or params.i or params.c or params.p:
				printErrExit(errors.EPAR)
			params.w = True
		elif p == "-c":
			if params.h or params.k or params.o or params.i or params.w or params.p:
				printErrExit(errors.EPAR)
			params.c = True
		elif p == "-p":
			if params.h or params.k or params.o or params.i or params.w or params.c:
				printErrExit(errors.EPAR)
			params.p = True
		else:
			printErrExit(errors.EPAR)
	return params

###############################################
# Funkce pro praci uvnitr zadane slozky
###############################################
def WorkInDir(path, params):
	#if path is a file
	if re.match(r'.*\.c', path) or re.match(r'.*\.h', path):
		print("Got a file called", path)
		#ParseFile(path)
	elif os.path.isdir(path):
		print("Got a dir called", path)
		for f in os.listdir(path):
			if re.match(r'.*\.c', f) or re.match(r'.*\.h', f):
				print("Got a file called", f)				
				#ParseFile(os.path.join(path, f))
			elif os.path.isdir(os.path.join(path,f)):
				if not params.noSubDir:
					WorkInDir(os.path.join(path,f), params)		
	else:
		return
			 

###############################################
# Main func
###############################################
def main():
	params = parameters()
	params = getParams()
	if not (params.k or params.o or params.i or params.w or params.c):
		printErrExit(errors.EPAR)
	if re.match(r'.*\.c', params.inputf) or re.match(r'.*\.h', params.inputf):
		if params.noSubDir:
			printErrExit(errors.EPAR)
	
	print ("Input: " + str(params.inputf))
	print ("Output: " + str(params.outputf))
	print ("Help: " + str(params.h))
	print ("K: " + str(params.k))
	print ("O: " + str(params.o))
	print ("I: " + str(params.i))
	print ("W: " + str(params.w))
	print ("C: " + str(params.c))
	print ("P: " + str(params.p))
	
	WorkInDir(params.inputf, params)

if __name__ == "__main__":
    main()
