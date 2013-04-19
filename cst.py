

#CST:xskriv01
########################################################################
#	CST.py
#	autor: Barbora Skrivankova, xskriv01@stud.fit.vutbr.cz
#	datum: 18.4.2012
#	popis: projekt do IPP
#		pocita statistiky nad C soubory
########################################################################

#potrebne systemove knihovny
import getopt, sys, re, os, string

#trida zastupujici strukturu s parametry
class parameters:
	#konstruktor 
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
errors = enum(EOK=0, EPAR=1, EIFILE=2, EOFILE=3, ESPEC=10)

#vycet pro reprezentaci stavu konecneho automatu
states = enum(S_IDLE=1, S_ID=2, S_PLUS=3, S_MINUS=4, S_TIMES=5, S_SLASH=6,
S_BAND=7, S_BOR=8, S_NOT=9, S_ASSIG=10, S_LT=11, S_GT=12)

#globalni promenna pro rekurzi
result = []

########################################################################
# Funkce pro tisk helpmsg na stdout
# vola se pri zadani parametru -h / --help
########################################################################
def usage():
	print ("Program C Stats v pythonu\n")
	print ("Barbora Skrivankova, xskriv01@stud.fit.vutbr.cz\n")
	print ("Pouziti: python ./cst.py (-h|--help) --input=fileordir --output=file [--nosubdir] (-k|-o|-i|-w|-c) [-p]\n\n")
	print ("\t\t-h, --help: vypise tuto napovedu a skonci program\n")
	print ("\t\t--input=fileordir: specifikace vstupniho souboru nebo adresare k analyze\n")
	print ("\t\t--output=file: specifikace vystupniho souboru\n")
	print ("\t\t--nosubdir: zakazani rekurzivniho prohledavani adresaru\n")
	print ("\t\t\t nelze kombinovat s input=file\n")
	print ("\t\t-k: probehne vypocet pro klicova slova\n")
	print ("\t\t-o: probehne vypocet pro jednoduche operatory\n")
	print ("\t\t-i: probehne vypocet pro identifikatory\n")
	print ("\t\t-w=pattern: vyhleda textovy retezec pattern a vypise pocet vyskytu\n")
	print ("\t\t-c: probehne vypocet pro znaky komentaru\n")
	print ("\t\t\tPrave jeden z -k, -o, -i, -w -c musi byt zadan\n")
	print ("\t\t-p: ve vypisech zrusi absolutni cesty k souborum\n")


# Pole s chybovymi vypisy pro jednotlive chyby
ePrints = {errors.EOK: "",
			errors.EPAR: "Chybne zadane parametry.\n",
			errors.EIFILE: "Chyba pri otevreni vstupniho souboru.\n",
			errors.EOFILE: "Chyba pri pristupu do vystupniho souboru.\n",
			errors.ESPEC: "Jina specificka chyba...\n",}

########################################################################
# Funkce printErrExit
# Funkce, ktera vytiskne na stderr chybove hlaseni a potom skript
# ukonci s pozadovanym error kodem, ktery ji je predavan jako parametr 
# vyctoveho typu.
########################################################################
def printErrExit(eCode):
	sys.stderr.write (ePrints[eCode])
	sys.exit(eCode)

########################################################################
# Funkce getParams
# Funkce, ktera vytvori strukturu params a naplni ji parametry
# predanymi na prikazove radce. Tuto strukturu po provedeni
# zakladnich kontrol vrati.
########################################################################
def getParams():
	params=parameters()
	#prochazime vektorem argumentu prikazove radky
	for p in sys.argv[1:]:
		if p in ("-h", "--help"):
			#help se nesmi spoustet s jinymi parametry
			if params.h or params.inputf or params.outputf or params.noSubDir or params.k or params.o or params.i or params.w or params.pattern or params.c or params.p or params.s:
				printErrExit(errors.EPAR)
			usage()
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
			if params.outputf or params.h:
				printErrExit(errors.EPAR)
			params.outputf = p[9:]
		elif p == "-k":
			if params.h or params.o or params.i or params.w or params.c:
				printErrExit(errors.EPAR)
			params.k = True
		elif p == "-o":
			if params.h or params.k or params.i or params.w or params.c:
				printErrExit(errors.EPAR)
			params.o = True
		elif p == "-i":
			if params.h or params.k or params.o or params.w or params.c:
				printErrExit(errors.EPAR)
			params.i = True
		elif re.match(r'-w=\S+', p):
			if params.h or params.k or params.o or params.i or params.c:
				printErrExit(errors.EPAR)
			params.w = True
			params.pattern = p[3:]
		elif p == "-c":
			if params.h or params.k or params.o or params.i or params.w:
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
	
########################################################################
# Funkce FindKeyword
# Funkce porovnavajici analyzovany retezec s klicovymi slovy jazyka C
#
# Na vstupu dostane retezec.
#
# Na vystupu da 1/0 reprezentujici hodnoty ano,
# retezec je klicovym slovem / ne, neni klicovym slovem.
########################################################################
def FindKeyword(word):
	keywords = ("auto", "break", "case", "char", "const", "continue", "default",
	"do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "int", 
	"inline", "long", "register", "return", "short", "signed", "sizeof", "static", 
	"struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while")
	
	if word in keywords:
		return 1
	else:
		return 0

########################################################################
# Funkce FindType
# Funkce porovnavajici analyzovany retezec s retezci datovych typu.
#
# Na vstupu dostane retezec.
#
# Na vystupu da 1/0 reprezentujici hodnoty ano,
# retezec je typem / ne, neni typem.
########################################################################
def FindType(word):
	keywords = ("char", "double", "float", "int", "long", "short", "signed",
	"struct", "union", "unsigned", "void")
	
	if word in keywords:
		return 1
	else:
		return 0

########################################################################
# Funkce FSMParsing
# Konecny automat pro precteni retezce s obsahem souboru a jeho zpracovani 
# dle parametru ze struktury params.
#
# Na vstupu dostane retezec s obsahem souboru po orezani vsech komentaru,
# retezcu a maker a strukturu params.
#
# Na vystup preda cislo odpovidajici pozadovane sume (dle params).
########################################################################
def FSMParsing(content, params):
	count = 0
	state = states.S_IDLE
	i = 0
	word = ""
	last = ""
	
	while 1:
		############# DETEKCE KONCE SOUBORU ############################
		try:
			c = content[i]
		except IndexError:
			break
		
		################ POCATECNI STAV KA #############################
		if state == states.S_IDLE:
			if c in string.ascii_letters:
				last = word
				word = c
				state = states.S_ID
			elif c in ['^', '~', '%', '.']:
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
				if (not FindType(last)) and (c == '(') and params.o and params.s:
					count += 1
				if FindKeyword(word) and params.k:
					count += 1
				elif (not FindKeyword(word)) and params.i:
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
			if c not in ['-', '=', '>']:
				#preskoci se inkrementace pocitadla
				continue
				
		########################### BYLA NACTENA * #####################
		elif state == states.S_TIMES:
			#pred hvezdickou je keyword -> jedna se o deklaraci
			state = states.S_IDLE	
			if not FindType(word):
				if params.o:
					count += 1
					
			
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

########################################################################
# Funkce ParseFile
# Funkce pro precteni a rozparsovani souboru
# 
# Na vstupu dostane cestu k souboru a pozadovane parametry.
# Soubor otevre, vystrihne z neho nepotrebna data a dle struktury parametru
# budto sam provede vypocet a nebo zavola fukci FSMParsing pro pokrocilejsi
# parsovani souboru.
#
# Na vystup preda cislo urcujici pozadovany pocet.
########################################################################
def ParseFile(path, params):	
	try:
		f = open(path, "r")
	except IOError:
		printErrExit(errors.EIFILE)
		
	#precteni celeho souboru
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
		f.close()
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
			content = content[:pos]
		else:
			content = content[:pos] + content[pos+end_pos:]
		pos = content.find("//")	
	
	
	#odmazani / vypocet pro makra
	content = "\n" + content
	pos = content.find("\n#")
	while pos != -1:
		#posun na zacatek makra - na znak #
		pos += 1 
		#najdu si prvni endline
		end_pos = pos + content[pos:].find("\n")
		next_pos = 0
		#dokud je pred endlinem lomitko, hledam dalsi endline
		while content[end_pos - 1] == "\\":
			end_pos += 1
			next_endl = content[end_pos:].find("\n")
			if next_endl == -1:
				break
			else:
				end_pos += next_endl			
		if end_pos != -1:
			content = content[:pos] + content[end_pos + 1:]
		else:
			content = content[:pos]
		if params.c and params.s:
			count += end_pos - pos
		pos = content.find("\n#")
	
	#odmazani retezcu
	pos = content.find("\"")
	while pos != -1:
		end_pos = content[pos + 1:].find("\"")
		if end_pos == -1:
			break
		content = content[:pos] + content[pos + end_pos + 2:]
		pos = content.find("\"")
	
	#odmazani jednoznakovych retezcu
	pos = content.find("\'")
	while pos != -1:
		end_pos = content[pos + 1:].find("\'")
		if end_pos == -1:
			break
		content = content[:pos] + content[pos + end_pos + 2:]
		pos = content.find("\'")	
	if params.k or params.i or params.o:
		count = FSMParsing(content, params)

	f.close()
	return count
		

########################################################################
# Funkce WorkInDie
# Funkce pro praci uvnitr zadane slozky
# 
# Na vstupu dostane cestu k souboru nebo slozce obsahujici soubor(y) k 
# pozadovane analyze a parametry prikazove radky params, dle kterych
# se analyza provadi.
#
# Na vystup preda heterogenni pole, jehoz obsahem je vzdy na sudem indexu
# nazev nebo cesta k souboru (dle params) a na nasledujicim lichem
# statistika pocitanych prvku v souboru.
########################################################################
def WorkInDir(path, params):
	#if path is a file
	if not (os.path.isdir(path) or os.path.isfile(path)):
		printErrExit(errors.EIFILE)
	
	if re.match(r'.*\.c', path) or re.match(r'.*\.h', path):
		if params.p:
			result.append(os.path.basename(path))
		else:
			result.append(path)
		result.append(ParseFile(path, params))
	elif os.path.isdir(path):
		for f in os.listdir(path):
			if re.match(r'.*\.c', f) or re.match(r'.*\.h', f):
				if params.p:
					result.append(f)
				else:
					result.append(os.path.join(path,f))	
				result.append(ParseFile(os.path.join(path, f), params))
			elif os.path.isdir(os.path.join(path,f)):
				if not params.noSubDir:
					WorkInDir(os.path.join(path,f), params)	
					
	return result
		
########################################################################
# Funkce CountLineLen
# Funkce pro vypocet delky vypisovaneho radku
#
# Na vstupu dostane pole vypocitanych statistik.
#
# Na vystup preda cislo, ktere znazornuje na kolika sloupcich obrazovky 
# bude mozne formatovane vypsat hodnoty z daneho pole.
########################################################################
def CountLineLen(array):
	i = 0
	num_max = 0
	char_max = 0
	
	for cell in array:
		if i % 2:
			if len(str(cell)) > num_max:
				num_max = len(str(cell))
				#print("Maximum : ", num_max)
		else:
			if len(cell) > char_max:
				char_max = len(cell)
				#	print("maximum: ", char_max)
		i += 1
	
	if num_max < len(str(Summary(result))):
		num_max = len(str(Summary(result)))

	return num_max + char_max + 1

########################################################################
# Funkce Summary
# Funkce pro vypocet souctu vsech hodnot jednotlivych souboru
#
# Na vstupu dostane pole vypocitanych statistik.
#
# Na vystupu preda soucet vsech hodnot.
########################################################################
def Summary(result):
	summary = 0
	count = (int)(len(result)/2)
	
	for i in range (0, count):
		summary += result[2*i + 1]
	return summary

########################################################################
# Funkce WriteOutput
# Funkce pro vypis vysledku
#
# Na vstupu dostane maximalni delku radku, pole vysledku a parametry 
# skriptu.
#
# Na standardni chybovy vystup vytiskne v predem definovanem formatu 
# pozadovana data.
########################################################################
def WriteOutput(maxlen, result, params):
	lines = (int)(len(result)/2)
	sortedRes = []
	
	summary = Summary(result)
	if maxlen < (len(str(summary)) + len("CELKEM:") + 1):
		maxlen = len(str(summary)) + len("CELKEM:") + 1
	
	if params.outputf:
		try:
			sys.stdout = open(params.outputf, "w")
		except IOError:
			printErrExit(errors.EOFILE)
	
	for i in range(0, lines):
		spaces = maxlen - len(result[2*i]) - len(str(result[2*i + 1]))
		line = str(result[2*i]).strip()+spaces*" "+str(result[2*i + 1]).strip()
		sortedRes.append(line)
	
	sortedRes.sort()
	spaces = maxlen - len("CELKEM:") - len(str(summary))
	summ = "CELKEM:" +spaces*" "+ str(summary)
	sortedRes.append(summ)
	
	for i in sortedRes:
		print(i)
	
########################################################################
# Main func
########################################################################
def main():
	#nacteni parametru
	params = parameters()
	params = getParams()
	
	if params.h:
		exit(0)
		
	#kontroly kolizi parametru
	if not (params.k or params.o or params.i or params.w or params.c):
		printErrExit(errors.EPAR)
	if params.s and not (params.o or params.c):
		printErrExit(errors.EPAR)
	if not params.inputf:
		params.inputf="./"
	if re.match(r'.*\.c', params.inputf) or re.match(r'.*\.h', params.inputf):
		if params.noSubDir:
			printErrExit(errors.EPAR)
	
	#vlastni prace skriptu
	result = WorkInDir(params.inputf, params)

	#vypis formatovaneho vystupu
	maxlen = CountLineLen(result)
	WriteOutput(maxlen, result, params)

if __name__ == "__main__":
    main()
