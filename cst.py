import getopt, sys, re, os, string

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
        self.pattern=False
        self.c=False
        self.p=False
        self.s=False
        
        
#Funkce pro vytvoreni vyctoveho typu
def enum(**enums):
    return type('Enum', (), enums)

#vycet pro reprezentaci chybovych stavu
errors = enum(EPAR=1, EIFILE=2, EOFILE=3, EWRONGIFILE=4, ESPEC=10, EINVALID=11)

#vycet pro reprezentaci stavu konecneho automatu
states = enum(S_IDLE=1, S_ID=2, S_PLUS=3, S_MINUS=4, S_TIMES=5, S_SLASH=6,
S_BAND=7, S_BOR=8, S_NOT=9, S_ASSIG=10, S_LT=11, S_GT=12)

###############################################
# Funkce pro tisk helpmsg
###############################################
def usage():
	sys.stderr.write ("\nProgram C Stats v pythonu\n")
	sys.stderr.write ("Barbora Skrivankova, xskriv01@stud.fit.vutbr.cz\n")
	sys.stderr.write ("Pouziti: python ./cst.py (-h|--help) --input=fileordir --output=file [--nosubdir] (-k|-o|-i|-w|-c) [-p]\n\n")
	sys.stderr.write ("\t\t-h, --help: vypise tuto napovedu a skonci program\n")
	sys.stderr.write ("\t\t--input=fileordir: specifikace vstupniho souboru nebo adresare k analyze\n")
	sys.stderr.write ("\t\t--output=file: specifikace vystupniho souboru\n")
	sys.stderr.write ("\t\t--nosubdir: zakazani rekurzivniho prohledavani adresaru\n")
	sys.stderr.write ("\t\t\t nelze kombinovat s input=file\n")
	sys.stderr.write ("\t\t-k: probehne vypocet pro klicova slova\n")
	sys.stderr.write ("\t\t-o: probehne vypocet pro jednoduche operatory\n")
	sys.stderr.write ("\t\t-i: probehne vypocet pro identifikatory\n")
	sys.stderr.write ("\t\t-w=pattern: vyhleda textovy retezec pattern a vypise pocet vyskytu\n")
	sys.stderr.write ("\t\t-c: probehne vypocet pro znaky komentaru\n")
	sys.stderr.write ("\t\t\tPrave jeden z -k, -o, -i, -w -c musi byt zadan\n")
	sys.stderr.write ("\t\t-p: ve vypisech zrusi absolutni cesty k souborum\n")

ePrints = {errors.EPAR: "Chybne zadane parametry.\n",
			errors.EIFILE: "Chyba pri otevreni vstupniho souboru.\n",
			errors.EOFILE: "Chyba pri pristupu do vystupniho souboru.\n",
			errors.EWRONGIFILE: "Chybny format vystupniho souboru.\n",
			errors.ESPEC: "Jina specificka chyba...\n",
			errors.EINVALID: "V souboru se vyskytla nevalidita",}
	
def printErrExit(eCode):
	sys.stderr.write (ePrints[eCode])
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
		elif re.match(r'-w=\S+', p):
			if params.h or params.k or params.o or params.i or params.c or params.p:
				printErrExit(errors.EPAR)
			params.w = True
			params.pattern = p[3:]
		elif p == "-c":
			if params.h or params.k or params.o or params.i or params.w or params.p:
				printErrExit(errors.EPAR)
			params.c = True
		elif p == "-p":
			if params.p:
				printErrExit(errors.EPAR)
			params.p = True
		elif p == "-s":
			if params.h or params.k or params.i or params.w:
				printErrExit(errors.EPAR)
			params.s = True			
		else:
			printErrExit(errors.EPAR)
	return params
	
###############################################
# Funkce porovnavajici analyzovany retezec s klicovymi slovy jazyka C
###############################################
def FindKeyword(word):
	keywords = ("auto", "break", "case", "char", "const", "continue", "default",
	"do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "int", 
	"long", "register", "return", "short", "signed", "sizeof", "static", "struct",
	"switch", "typedef", "union", "unsigned", "void", "volatile", "while")
	
	if word in keywords:
		return 1
	else:
		return 0

###############################################
# Funkce pro precteni a rozparsovani souboru
###############################################
def FSMParsing(content, params):
	count = 0
	state = states.S_IDLE
	i = 0
	
	while 1:
		############# DETEKCE KONCE SOUBORU ############################
		try:
			c = content[i]
		except IndexError:
			break
		
		################ POCATECNI STAV KA #############################
		if state == states.S_IDLE:
			if c in string.ascii_letters:
				word = c
				state = states.S_ID
			elif c in ['^', '~', '%']:
				if params.o:
					count += 1
				state = states.S_IDLE
			elif c == '+':
				state = states.S_PLUS
			elif c == '-':
				state = states.S_MINUS
			elif c == '*':
				state = states.S_TIMES
			elif c == '/':
				state = states.S_SLASH
			elif c == '&':
				state = states.S_BAND
			elif c == '|':
				state = states.S_BOR
			elif c == '!':
				state = states.S_NOT
			elif c == '=':
				state = states.S_ASSIG
			elif c == '<':
				state = states.S_LT
			elif c == '>':
				state = states.S_GT
		
		############# ANALYZUJEME IDENTIFIKATOR/KEYWORD ################
		elif state == states.S_ID:
			if c not in (string.ascii_letters + string.digits + '_'):
				if FindKeyword(word) and params.k:
					count += 1
				elif (not FindKeyword(word)) and params.i:
					print(word)
					count +=1
				state = states.S_IDLE
				# i se neinkrementuje - preskoci se posledni radek cyklu
				continue
			else:
				word += c
				
		########################### BYLO NACTENO + #####################
		elif state == states.S_PLUS:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c not in ['+', '=']:
				#preskoci se inkrementace pocitadla
				continue
				
		########################### BYLO NACTENO - #####################
		elif  state == states.S_MINUS:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c not in ['-', '=']:
				#preskoci se inkrementace pocitadla
				continue
				
		########################### BYLA NACTENA * #####################
		elif state == states.S_TIMES:
			############################################################
			#			TOHLE BUDE JESTE TROSKU SLOZITEJSI...
			############################################################
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
				
		########################### BYLO NACTENO / #####################
		elif state == states.S_SLASH:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
				
		########################### BYLO NACTENO & #####################
		elif state == states.S_BAND:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '&':
				continue
				
		########################### BYLO NACTENO | #####################
		elif state == states.S_BOR:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '|':
				continue
				
		########################### BYL NACTEN ! #######################
		elif state == states.S_NOT:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
				
		########################### BYLO NACTENO = #####################
		elif state == states.S_ASSIG:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
				
		########################### BYLO NACTENO < #####################
		elif state == states.S_LT:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
				
		########################### BYLO NACTENO > #####################
		elif state == states.S_GT:
			if params.o:
				count += 1
			state = states.S_IDLE
			if c != '=':
				continue
		i += 1

	return count

###############################################
# Funkce pro precteni a rozparsovani souboru
###############################################
def ParseFile(path, params):
	f = open(path, "r")
	content = f.read()
	count = 0
	makro_ind = 0
	
	#hledani textovych vzoru z parametru -w
	if params.w:
		pos = content.find(params.pattern)
		while pos != -1:
			count += 1
			content = content[pos + len(params.pattern):]
			pos = content.find(params.pattern)
		return count
	
	#odmazani / vypocet pro multiline komentare
	pos = content.find("/*")
	while pos != -1:
		end_pos = content.find("*/")
		end_pos += 2
		if params.c:
			count += (end_pos - pos)
		content = content[:pos] + content[end_pos:]
		pos = content.find("/*")
	
	#odmazani / vypocet pro radkove komentare
	pos = content.find("//")
	while pos != -1:
		end_pos = content[pos:].find("\n")
		if params.c:
			if end_pos == -1:
				count += len(content[pos:])
			else:
				count += end_pos + 1				
		if end_pos == -1:
			content = conten[:pos]
		else:
			content = content[:pos] + content[pos+end_pos:]
		pos = content.find("//")	
	content = "\n" + content
	
	#odmazani / vypocet pro makra
	pos = content.find("\n#")
	while pos != -1:
		pos += 1
		end_pos = content[pos:].find("\n")
		while content[pos + end_pos - 1] == "\\":
			end_pos = content[end_pos:].find("\n")
		if params.c and params.s:
			if end_pos == -1:
				count += len(content[pos:])
			else:
				count += end_pos + 1				
		if end_pos == -1:
			content = conten[:pos]
		else:
			content = content[:pos] + content[pos+end_pos:]
		pos = content.find("\n#")	
		
	#odmazani retezcu
	pos = content.find("\"")
	while pos != -1:
		end_pos = content[pos + 1:].find("\"")
		if end_pos == -1:
			printErrExit(errors.EINVALID)
		content = content[:pos] + content[pos + end_pos + 2:]
		pos = content.find("\"")
	
	#odmazani jednoznakovych retezcu
	pos = content.find("\'")
	while pos != -1:
		end_pos = content[pos + 1:].find("\'")
		if end_pos == -1:
			printErrExit(errors.EINVALID)
		content = content[:pos] + content[pos + end_pos + 2:]
		pos = content.find("\'")	
	if params.k or params.i or params.o:
		count = FSMParsing(content, params)

	return count
		

###############################################
# Funkce pro praci uvnitr zadane slozky
###############################################
def WorkInDir(path, params):
	result = []
	#if path is a file
	if re.match(r'.*\.c', path) or re.match(r'.*\.h', path):
		if params.p:
			result.append(os.path.basename(path))
		else:
			result.append(path)
		result.append(ParseFile(path, params))
	elif os.path.isdir(path):
		print("Got a dir called", path)
		for f in os.listdir(path):
			if re.match(r'.*\.c', f) or re.match(r'.*\.h', f):
				if params.p:
					result.append(f)
				else:
					result.append(os.path.join(path,f))
				print("Got a file called", f)				
				result.append(ParseFile(os.path.join(path, f), params))
			elif os.path.isdir(os.path.join(path,f)):
				if not params.noSubDir:
					WorkInDir(os.path.join(path,f), params)		
	return result
		
###############################################
# Funkce pro vypocet delky vypisovaneho radku
###############################################
def CountLineLen(array):
	i = 0
	num_max = 0
	char_max = 0
	
	for cell in array:
		if i % 2:
			if len(str(cell)) > num_max:
				num_max = len(str(cell))
		else:
			if len(cell) > char_max:
				char_max = len(cell)
		i += 1
	return num_max + char_max + 1

###############################################
# Funkce pro vypis vysledku
###############################################			 
def WriteOutput(maxlen, result):
	lines = (int)(len(result)/2)
	
	for i in range(0, lines):
		spaces = maxlen - len(result[2*i]) - len(str(result[2*i + 1]))
		print(result[2*i], spaces*" ", result[2*i + 1])
	
###############################################
# Main func
###############################################
def main():
	params = parameters()
	params = getParams()
	if not (params.k or params.o or params.i or params.w or params.c):
		printErrExit(errors.EPAR)
	if params.s and not (params.o or params.c):
		printErrExit(errors.EPAR)
	if re.match(r'.*\.c', params.inputf) or re.match(r'.*\.h', params.inputf):
		if params.noSubDir:
			printErrExit(errors.EPAR)
	
	result = WorkInDir(params.inputf, params)
	
	maxlen = CountLineLen(result)
	WriteOutput(maxlen, result)

if __name__ == "__main__":
    main()
