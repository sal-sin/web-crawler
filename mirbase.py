import scrapy

"""
mirAcc: accession of miRNA
returns: url of the webpage in www.mirbase.org containing info of the miRNA
"""
def getMirUrl(mirAcc):
	mirUrl = "http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc="
	return mirUrl + mirAcc

"""
mirAcc: accession of miRNA
returns: url of the webpage in www.mirbase.org containing miRNA sequence
"""
def getMirSeqUrl(mirAcc):
	mirSeqUrl = "http://www.mirbase.org/cgi-bin/get_seq.pl?acc="
	return mirSeqUrl + mirAcc

"""
Sub-class of a class scrapy.Spider that has been predefined in the scrapy module
"""
class MirBaseSpider(scrapy.Spider):
	name = "mirbase"
	'''
	Function that is first called when this python file is run with the command "scrapy runspider"
	'''
	def start_requests(self):
		self.startAcc = raw_input("Last miRNA accession# parsed (or enter 0): ")
		self.tableMirIdList = [] # list of miRNA IDs in the table
		self.tableMirAccList = [] # list of miRNA accession in the table
		tablePageUrl = "http://www.mirbase.org/cgi-bin/mirna_summary.pl?org=hsa" # main webpage
		return [scrapy.Request(url = tablePageUrl, callback = self.tableParse)] # return webpage request then tableParse called back
			
	'''
	Function as a callback for request of the webpage with table
	'''
	def tableParse(self, response):
		rowSelectorList = response.css('tr') # list of row selectors in the table by identifying <tr>...</tr> tags
		rowSelectorList = rowSelectorList[3:-2] # first 3 rows and last 2 rows are redundant
		for rowSelector in rowSelectorList:
			mirIdnAcc = rowSelector.css('a::text').extract()[ :2] # extract miRNA ID and accession from each row
			self.tableMirIdList.append(str(mirIdnAcc[0])) # append ID in the list
			self.tableMirAccList.append(str(mirIdnAcc[1])) # append acc in the list
		
		if self.startAcc != "0":
			if self.startAcc.upper() in self.tableMirAccList:
				ind = self.tableMirAccList.index(self.startAcc.upper())
				if ind == len(self.tableMirAccList) - 1:
					print ("\nEntered accession# is last on the page.\n")
					return None
				self.tableMirAccList = self.tableMirAccList[ind + 1: ]
				self.tableMirIdList = self.tableMirIdList[ind + 1: ]
			else:
				print ("\nEntered accession# not found on page.")
				print ("Restart the program & try again...\n")
				return None

		print ("\nmiRNA ID and Accession list generated from table.\n\n") # message displayed on terminal
		firstMirUrl = getMirUrl(self.tableMirAccList[0]) # url of the first miRNA in the main table
		return [scrapy.Request(url = firstMirUrl, callback = self.mirParse)] # return request of miRNA webpage, mirParse called back

	'''
	Function as a callback for request of an miRNA webpage
	'''
	def mirParse(self, response):
		stemLoopSelector = response.css('pre')[0] # first selector identifying <pre>...</pre> tags
		stemLoop = stemLoopSelector.css('::text').extract() # extract stem-loop structure, returns a list
		stemLoop = str(''.join(stemLoop)) # join list elements to form a string
		with open("mirBase.txt", 'a') as file:
			file.write("ID: " + self.tableMirIdList[0] + "\nACCESSION: " + self.tableMirAccList[0])
			file.write("\n" + "-" * 21 +"\n")
			file.write(stemLoop + "\n\n") # write loop structure in file
			file.close()

		mirSeqUrl = getMirSeqUrl(self.tableMirAccList[0]) # url of webpage containing sequence of miRNA
		return [scrapy.Request(url = mirSeqUrl, callback = self.mirSeqParse)] # return request of webpage, then mirSeqParse called back

	'''
	Function as a callback for request of an miRNA sequence webpage
	'''
	def mirSeqParse(self, response):
		sequence = str(response.css('pre::text')[0].extract()) # extract miRNA sequence string
		sequence = sequence[1: ] # ignore first character
		sequence = sequence[sequence.index('\n'): ] # actual sequence extracted
		with open("mirBase.txt", 'a') as file:
			file.write(sequence + "\n") # write sequence in file
			file.write(('=' * 107 + "\n")*2 + "\n")
			file.close()

		print ("\nParsed Acc# " + self.tableMirAccList[0] + "\n") # message on terminal
		self.tableMirIdList.pop(0) # remove the first miRNA from the lists
		self.tableMirAccList.pop(0)
		if self.tableMirAccList != []: # if more left in list
			mirUrl = getMirUrl(self.tableMirAccList[0]) # url of webpage containing miRNA info
			return [scrapy.Request(url = mirUrl, callback = self.mirParse)] # return request of the webpage, mirParse called back
		else: # if list is empty => all miRNA sequences parsed
			print("DONE! :)\n\n")
			return None