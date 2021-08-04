# This code is by Dmitri Turevski. The point of this code was to check a list of author names on YACPDB to detect duplicates. Right now I'd like to reformat it to work with YACPDB keywords (list is `YACPDB Keywords List.txt`), but I'll have to figure out how to do this.



#!/usr/bin/env python

import re, difflib, sys

"""
f = open('download/yacpdb-20090326.yaml')
symbols = {}
for line in f:
	for char in unicode(line.strip(), 'utf-8'):
		if not char in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM ":;!@#$%^&*()_+-=,./<>?\\|':
			symbols[char] = True
for k, v in symbols.iteritems():
	print k.encode('utf-8')
"""

class trans_table:
	def __init__(self):
		self.table, self.ucase, self.lcase = {}, {}, {}
		self.ws_remover = re.compile('\s+')
		self.unchanged = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM -.,\''

	def load(self, filename):
		f = open(filename)
		for line in f:
			t1, t2, t3 = (line.strip()).partition(' ')
			k, v = unicode(t1, 'utf-8'), t3
			self.table[k] = v
			if v.isupper():
				self.ucase[k] = v
			else:
				self.lcase[k] = v
		f.close()
		
	def translate(self, string):
		#print "Translating '%s'" % string
		retval = u''
		i = 0
#		for i in xrange(len(string)):
		for char in string:
			char = string[i]
			if i + 1 < len(string):
				nextchar = string[i + 1]
			else:
				nextchar = ''
			
			i = i + 1
		
			#print "'" + char + "'"
			if char in self.unchanged:
				retval = retval + char
			elif self.table.has_key(char):
				if (len(self.table[char]) == 1) or not self.table[char].isupper():
					retval = retval + self.table[char]
				else:
					# if next char is not translatable - leave just 1 char of the abbreviation
					if (nextchar == '') or not self.table.has_key(nextchar):
						retval = retval + self.table[char][0]
					# if the next char translated is uppercase - translate uppercase
					elif self.table[nextchar].isupper():
						retval = retval + self.table[char]
					# else leave only the first ascii char uppercased
					else:
						retval = retval + self.table[char].title()
			else:
				#print char.encode('utf-8')
				retval = retval + u' '
		return self.ws_remover.sub(' ', retval.strip())
		



class name2:
	h1re = re.compile('^(?P<LN>[A-Za-z \'\-]+), ?(?P<FN>[A-Za-z \'\-\.]+)$')
	h2re = re.compile('^(?P<LN>([A-Z][A-Z\'\-]+ )+)(?P<FN>.*)$')
	h3re = re.compile('^(?P<FN>([A-Z][\. ]+)+)(?P<LN>.*)$')
	h3re2 = re.compile('^(?P<LN>([A-Z][A-Za-z\'\-]+ ?)+) (?P<FN>([A-Z][\. ]+)*[A-Z]\.?)$')
	h4re = re.compile('^(?P<FN>[A-Z][a-z]+ [A-Z]\.) (?P<LN>[A-Z][a-z]+)$')

	ln_aux = [(re.compile('ev$', re.IGNORECASE), 'ew'), (re.compile('ov$', re.IGNORECASE), 'ow'), (re.compile('ki[yj]$', re.IGNORECASE), 'ki'), \
		(re.compile('ky$', re.IGNORECASE), 'ki'), ]

	def __init__(self, raw):
#		self.raw = {'utf':raw, 'ascii':tr.translate(raw).replace('x', 'ks').replace('X', 'KS')}
		self.raw = {'utf':raw, 'ascii':tr.translate(raw).replace('x', 'ks').replace('X', 'KS').replace('-', ' ')}

		self.is_parsed = False
		self.lastnames = self.firstnames = []
		if not self.heu1():
			if not self.heu2():
				if not self.heu3():
					pass
					if not self.heu4():
						pass
		self.lastnames = [x.strip() for x in self.lastnames]
		self.lastnames = filter(lambda x: x<>'', self.lastnames)

		#tmp = []
		#for ln in self.lastnames:
		#	for needle, repl in name2.ln_aux:
		#		ln = needle.sub(repl, ln)
		#	tmp.append(ln)
		#self.lastnames = tmp

		self.firstnames = [x.strip().replace('.', '') for x in self.firstnames]
		self.firstnames = filter(lambda x: x<>'', self.firstnames)

	def __str__(self):
		#return str(self.lastnames)
		s = self.raw['utf'] + ' (' + " ".join(self.lastnames) \
			+ ', ' + " ".join(self.firstnames) +')'
		return s.encode('utf-8')

	# comma separated
	def heu1(self):
		match = name2.h1re.match(self.raw['ascii'])
		if not match:
			return False
		self.lastnames = match.group('LN').strip().partition(' ')
		self.firstnames = match.group('FN').strip().replace('.', ' ').partition(' ')
		self.is_parsed = True
		return True

	# lastname uppercased
	def heu2(self):
		reverse = False
		match = name2.h2re.match(self.raw['ascii'])
		if not match:
			match = name2.h2re.match(self.raw['ascii'][::-1])
			if not match:
				return False
			reverse = True
		if reverse:
			self.lastnames = match.group('LN')[::-1].strip().partition(' ')
			self.firstnames = match.group('FN')[::-1].strip().replace('.', ' ').partition(' ')
		else:
			self.lastnames = match.group('LN').strip().partition(' ')
			self.firstnames = match.group('FN').strip().replace('.', ' ').partition(' ')
		self.is_parsed = True
		return True

	# one word and initials
	def heu3(self):
		match = name2.h3re.match(self.raw['ascii'])
		if not match:
			match = name2.h3re2.match(self.raw['ascii'])
			if not match:
				return False
		self.lastnames = match.group('LN').strip().partition(' ')
		self.firstnames = match.group('FN').strip().replace('.', ' ').partition(' ')
		self.is_parsed = True
		return True

	# Firstame I. Lastname
	def heu4(self):
		match = name2.h4re.match(self.raw['ascii'])
		if not match:
			return False
		self.lastnames = match.group('LN').strip().partition(' ')
		self.firstnames = match.group('FN').strip().replace('.', ' ').partition(' ')
		self.is_parsed = True
		return True

	def find_matches(self, haystack):
		retval = []
		for candidate in haystack:
			outcome, rt = self.compare_more(candidate)
			if outcome in ['exact match']:
				retval.append((candidate, rt))
			if outcome in ['less']:
				retval.append((candidate, rt))
			if outcome in ['more']:
				retval.append((candidate, rt))
		retval = filter(lambda x: x[1] >= 0.7, retval)
		return sorted(retval, lambda x, y:  [-1, 1][y[1] - x[1] > 0])

	def compare_more(self, that):
		if self.is_parsed:
			return self.compare(that)
		words = self.raw['ascii'].split()
		for i in xrange(1, len(words)):
			for s in [" ".join(words[:i]) + ', ' + " ".join(words[i:]), \
				" ".join(words[i:]) + ', ' + " ".join(words[:i])]:
				newname = name2(s)
				if newname.is_parsed:
					o, rt = newname.compare(that)
					if o != 'diff':
						return o, rt
		return 'diff', 0

	def compare(self, that):
		o, rt = cmp_strings_fuzzy(" ".join(self.lastnames), " ".join(that.lastnames), False)
		if o in ['diff', 'abbreviation']:
			return 'diff', 0
		r = [len(self.firstnames), len(that.firstnames)][len(self.firstnames) > len(that.firstnames)]
		more_case, less_case = False, False
		rt2 = 1
		for i in xrange(r):
			outcome, rttemp = cmp_strings_fuzzy(self.firstnames[i], that.firstnames[i], True)
			rttemp = rttemp**0.5 # errors in first names weight less
			rt2 = rt2*rttemp			
			if 'diff' == outcome:
				return 'diff', 0
			if 'abbreviation' == outcome:
				if (len(self.firstnames[i]) == 1) and (len(that.firstnames[i]) != 1):
					more_case = True
				if (len(self.firstnames[i]) != 1) and (len(that.firstnames[i]) == 1):
					less_case = True
		if more_case and (not less_case) and (len(that.firstnames) >= len(self.firstnames)):
			return 'more', rt*rt2
		if less_case and (not more_case) and (len(self.firstnames) >= len(that.firstnames)):
			return 'less', rt*rt2
		if (not less_case) and (not more_case):
			if len(self.firstnames) == len(that.firstnames):
				return 'exact match', rt*rt2
			if len(self.firstnames) < len(that.firstnames):
				return 'more', rt*rt2
			if len(self.firstnames) > len(that.firstnames):
				return 'less', rt*rt2
		return 'match', rt*rt2


# match, exact match, abbreviation, diff
def cmp_strings_fuzzy(a, b, docut):
	a, b = a.upper(), b.upper()
	if len(b) == 1:
		a, b = b, a
	if len(a) == 1:
		b1 = b[0]
		if (a == b1) and (len(b) == 1):
			return 'exact match', 1
		if a == b1:
			return 'abbreviation', 1
		# transliteration
		trans = ['YJ', 'HG', 'VW']
		for t in trans:
			if (a in t) and (b1 in t):
				if len(b) == 1:
					return 'match', 1
				else:
					return 'abbreviation', 1
		return 'diff', 0
	else:
		if a == b:
			return 'exact match', 1
		if docut:
			if len(a) < len(b):
				a, b = b, a
			b = b[:len(a)]
 
		#s = difflib.SequenceMatcher(None, a, b)

		#print s.ratio(), soundex(a), soundex(b), soundex(a[::-1]), soundex(b[::-1])

		#rt = s.ratio()
		rt = stats.ratio(a, b)

		if rt > 0.65:
			return 'match', rt
			
		"""
		if soundex(a) == soundex(b):
			return 'match'
		if soundex(a[::-1]) == soundex(b[::-1]):
			return 'match'
		"""
		return 'diff', 0

class diffstats:
	def __init__(self):
		self.data = {'post':{}, 'pre':{}}
	def dump(self, full):
		for postpre in ['post', 'pre']:
			i = 0
			for k, v in sorted(self.data[postpre].iteritems(), lambda x, y:  [-1, 1][y[1] - x[1] > 0]):
				print "%s\t%d" % (k, v)
				i = i+1
				if(i > 10) and not full:
					break
			print "-------------------------"
	def load(self):
		self.maxv = {}
		for postpre in ['post', 'pre']:
			self.maxv[postpre] = 0
			for line in file(postpre):
				parts = line.strip().partition("\t")
				opcode, freq = parts[0], int(parts[2])
				if freq > self.maxv[postpre]:
					self.maxv[postpre] = freq
				self.data[postpre][opcode] = freq
	def ratio(self, a, b):
		s = difflib.SequenceMatcher(None, a, b)
		rt = s.ratio()

		opweight = 1.0/(len(a) + len(b))
		correction = 0
		for opcode in s.get_opcodes():
			w = 0
			for postpre in ['post', 'pre']:
				pretty = opcode_to_stats(opcode, a, b, postpre)
				if not pretty is None:
					if stats.data[postpre].has_key(pretty):
#						print self.data[postpre][pretty]/(0.0+self.maxv[postpre]), pretty
#						w = w + sshape(self.data[postpre][pretty]/(self.maxv[postpre]+0.0), 5)
#						print self.data[postpre][pretty]/(self.maxv[postpre]+0.0)
						tmp = sshape(self.data[postpre][pretty]/(self.maxv[postpre]+0.0), 5)
						if(tmp > w):
							w = tmp
			correction = correction + opweight*w
#			print w, opweight, correction, rt
		return rt + correction

def sshape(x, t):
	if(x > 0.5):
		return 0.5 + (x - 0.5)**(1/t)/(2*(0.5)**(1/t))
	else:
		return 0.5 - (0.5 - x)**(1/t)/(2*(0.5)**(1/t))


def save_name_stats(n1, n2, stats):
	if not n1.is_parsed or not n2.is_parsed:
		return
	a, b = " ".join(n1.lastnames).upper(), " ".join(n2.lastnames).upper().upper()
	s = difflib.SequenceMatcher(None, a , b)
	for opcode in s.get_opcodes():
		for postpre in ['post', 'pre']:
			pretty = opcode_to_stats(opcode, a, b, postpre)
			if not pretty is None:
				if stats.data[postpre].has_key(pretty):
					stats.data[postpre][pretty] = stats.data[postpre][pretty] + 1
				else:
					stats.data[postpre][pretty] = 1

def opcode_to_stats(opcode, a, b, postpre):
	tag, i1, i2, j1, j2 = opcode
	if tag == 'equal':
		return None
	if tag == 'delete':
		if i2-i1 != 1:
			return None
		char_before, char_after = char_pair_delrepl(i1, a)
		if postpre == 'pre':
			return a[i1] + ' ' + char_after
		else:
			return char_before + a[i1]

	if tag == 'insert':
		if j2-j1 != 1:
			return None
		char_before, char_after = char_pair_insert(i1, a)
		if postpre == 'pre':
			return b[j1] + ' ' + char_after
		else:
			return char_before + b[j1] + ' '

	if tag == 'replace':
		if (i2-i1 != 1) or (j2-j1 != 1):
			return None
		char_before, char_after = char_pair_delrepl(i1, a)
		if postpre == 'pre':
			if a[i1] < b[j1]:
				return a[i1] + b[j1] + char_after
			else:
				return b[j1] + a[i1] + char_after
		else:
			if a[i1] < b[j1]:
				return char_before + a[i1] + b[j1]
			else:
				return char_before + b[j1] + a[i1]
		

def char_pair_delrepl(pos, string):
	if pos == 0:
		char_before = '!'
	else:
		char_before = string[pos-1]
	if pos == len(string) - 1:
		char_after = '!'
	else:
		char_after = string[pos+1]

	return char_before, char_after

def char_pair_insert(pos, string):
	if pos == 0:
		char_before = '!'
	else:
		char_before = string[pos-1]
	if pos == len(string):
		char_after = '!'
	else:
		char_after = string[pos]

	return char_before, char_after

def soundex(name, len=4):
	# digits holds the soundex values for the alphabet
	digits = '01230120022455012623010202'
	sndx = ''
	fc = ''
	# translate alpha chars in name to soundex digits
	for c in name.upper():
		if c.isalpha():
		    if not fc: fc = c   # remember first letter
		    d = digits[ord(c)-ord('A')]
		    # duplicate consecutive soundex digits are skipped
		    if not sndx or (d != sndx[-1]):
		        sndx += d

	sndx = fc + sndx[1:]   # replace first digit with first char
	sndx = sndx.replace('0','')       # remove all 0s
	return (sndx + (len * '0'))[:len] # padded to len characters


	
tr = trans_table()
tr.load('chars.txt')

stats = diffstats()
stats.load()


"""
print stats.ratio('ANCIN', 'ANCHIN')
#print stats.ratio('ABRAMENKO', 'RADMIENKO')
sys.exit(0)
"""

canonical = []
f = open('canonical.txt')
#f = open('2.txt')
for line in f:
	n = name2(unicode(line.strip(), 'utf-8'))
	if n.is_parsed:
		canonical.append(n)

unsorted = []
f = open('noncanonical.txt')
#f = open('1.txt')
cp, cd, nm, good = 0, 0, 0, 0
for line in f:
	n = name2(unicode(line.strip(), 'utf-8'))
	matches = n.find_matches(canonical)
	if len(matches) > 0:
		if len(matches) > 1:
			if matches[0][1] - matches[1][1] < 0.05:
				cd = cd + 1
				#print "CANT DECIDE:", matches[0][0], matches[1][0], matches[0][1], matches[1][1]
				#print ' ----> ',
				#for x, i in matches:
				#	print x, i, ';',
			else:
				good = good + 1
				print "%s\t%s\t%f" % (n.raw['utf'].encode('utf-8'), matches[0][0].raw['utf'].encode('utf-8'), matches[0][1])
				#save_name_stats(n, matches[0][0], stats)
				#print cp, cd, nm, good, int(100*good/(cp + cd + nm + good)), len(stats.data), "%\t",
				#print n, "\t",
				#print "\t", matches[0][0], "\t", matches[0][1]
				#if not n.is_parsed:
				#	print "!!!!!!!!!!!!"
				#stats.dump(False)
				sys.stdout.flush()
				continue
		else:
			good = good + 1
			print "%s\t%s\t%f" % (n.raw['utf'].encode('utf-8'), matches[0][0].raw['utf'].encode('utf-8'), matches[0][1])
			#save_name_stats(n, matches[0][0], stats)
			#print cp, cd, nm, good, int(100*good/(cp + cd + nm + good)), len(stats.data), "%\t",
			#print n, "\t",
			#print "\t", matches[0][0], "\t", matches[0][1]
			#if not n.is_parsed:
			#	print "!!!!!!!!!!!!"
			#stats.dump(False)
			sys.stdout.flush()
			continue
	else:
		nm = nm + 1
		#print n,
		#print " ... no match"
	#print n

#stats.dump(True)

"""f = open('authors2.txt')
#f = open('test-authors.txt')
for line in f:
	n = name(unicode(line.strip(), 'utf-8'))
	if n.is_parsed:
		#print n.raw['utf'], n.raw['ascii']
		print n.lastname, ' '.join(n.names)
		#print line,
"""
#print cmp_strings_fuzzy('VUKCEVIC', 'VUKCHEVICH')
