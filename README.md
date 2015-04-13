# C_stats
Python script which analyzes C code and searches for specified words.

###Usage: python ./cst.py (-h|--help) --input=fileordir --output=file --nosubdir (-k|-o|-i|-w|-c) [ -p ]
	--help: Prints this text
	--input=fileordir: input file (or dir) to analyze
	--output=file: output file
	--nosubdir: not process subdirectories
	-k: process with keywords
	-o: process with operators
	-i: process with identifiers
	-w=pattern: searches for pattern and counts number of occurence
	-c: counts chars of comments
	-p: no file paths in results
