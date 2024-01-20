import scrapy

"""
pageNum: integer signifying the page number of the desired table in the mirTar database
returns: url of the webpage containing the table
"""
def getTableUrl(pageNum):
	tableUrl = "http://mirtarbase.mbc.nctu.edu.tw/php/search.php?q=search_exact&searchword=hsa-let-7a-5p&sort=id&order=asc&page="
	return tableUrl + str(pageNum)

"""
mirID: unique ID of the miRNA sequence
returns: url of the webpage containing information of the miRNA
"""
def getMirUrl(mirID):
	mirUrl = "http://mirtarbase.mbc.nctu.edu.tw/php/detail.php?mirtid="
	return mirUrl + mirID + "#target"

"""
Sub-class of a class scrapy.Spider that has been predefined in the scrapy module
"""
class MirTarBaseSpider(scrapy.Spider):
	name = "mirtarbase" # name of database to parse
	'''
	Function that is first called when this python file is run with the command "scrapy runspider"
	'''
	def start_requests(self):
		self.tablePageNum = int(input("Which page would you like to start from? ")) # page number to start parsing
		self.startAcc = raw_input("Last miRNA accession# parsed (or enter 0): ")
		self.humanMirAccList = [] # list of Accession# of all homo sapien miRNA
		self.humanMirIdList = [] # list of ID
		self.humanMirTarList = [] # list of targets
		tablePageUrl = getTableUrl(self.tablePageNum) # url of the first table page to visit
		return [scrapy.Request(url = tablePageUrl, callback = self.tableParse)] # go to the first table page and tableParse called back
			
	'''
	Function as a callback for requests of webpages with a table
	'''
	def tableParse(self, response):
		rowSelectorList = response.css('tr') # list of row selectors in the table by identifying <tr>...</tr> tags
		rowSelectorList = rowSelectorList[3: ] # first 3 rows are redundant
		for rowSelector in rowSelectorList:
			mirAcc = str(rowSelector.css('a::text').extract()[0]) # extract miRNA accession from the row
			rowData = rowSelector.css('td::text').extract() # extract data from row
			species = str(rowData[0]) 
			mirId = str(rowData[2])
			mirTar = str(rowData[3])
			if species.lower() == "homo sapiens":
				self.humanMirAccList.append(mirAcc) # append Acc of miRNA
				self.humanMirIdList.append(mirId) # append ID
				self.humanMirTarList.append(mirTar) # append target name
		
		if self.startAcc != "0": # acc number given
			if self.startAcc.upper() in self.humanMirAccList: # remove all acc numbers before given acc number, including itself
				ind = self.humanMirAccList.index(self.startAcc.upper())
				if ind == len(self.humanMirAccList) - 1:
					self.humanMirAccList = []
					self.humanMirIdList = []
					self.humanMirTarList = []
				else:
					self.humanMirAccList = self.humanMirAccList[ind + 1: ]
					self.humanMirIdList = self.humanMirIdList[ind + 1: ]
					self.humanMirTarList = self.humanMirTarList[ind + 1: ]
			else:
				print ("\nEntered accession# not found on page# " + str(self.tablePageNum))
				print ("Restart program and try again.\n")
				return None
			self.startAcc = "0"
		
		if self.humanMirAccList == []:
			print("\nNo human miRNA found on page# " + str(self.tablePageNum) + "\n")
			self.tablePageNum += 1
			tablePageUrl = getTableUrl(self.tablePageNum)
			return [scrapy.Request(url = tablePageUrl, callback = self.tableParse)]

		firstMirUrl = getMirUrl(self.humanMirAccList[0]) # url of page with info of the very first human miRNA sequence
		return [scrapy.Request(url = firstMirUrl, callback = self.mirTarParse)] # go to the miRNA page and mirTarParse called

	'''
	Function as a callback for requests of webpages containing miRNA and target information
	'''
	def mirTarParse(self, response):
		duplexSelectorList = response.css('pre') # list of selectors by identifying <pre>...</pre> tags
		duplexSelectorList = duplexSelectorList[1: ] # the first selector does not contain duplex structure info
		duplexStructureList = duplexSelectorList.css('::text').extract() # extracting unicode text giving the duplex structure
		duplexStructureList = [str(structure) for structure in duplexStructureList] # convert all structures into strings
		with open("mirTarBase.txt", 'a') as file: # append mode
			file.write("ACCESSION: " + self.humanMirAccList[0] + "\nID: " + self.humanMirIdList[0] + "\nTARGET GENE: " + self.humanMirTarList[0] + "\n")
			file.write("-"*44 + "\n")
			for structure in duplexStructureList: # write all the extracted duplex structure strings in the file
				file.write(structure + "\n\n")
			file.write(('=' * 44 + '\n') * 2 + "\n")
			file.close()

		print ("\nParsed Acc# " + self.humanMirAccList[0] + " --> at page# " + str(self.tablePageNum) + "\n") # print on terminal when the miRNA is parsed
		self.humanMirAccList.pop(0) # remove the first miRNA info from lists
		self.humanMirIdList.pop(0)
		self.humanMirTarList.pop(0)
		if self.humanMirAccList != []: # if more IDs left
			mirUrl = getMirUrl(self.humanMirAccList[0])
			return [scrapy.Request(url = mirUrl, callback = self.mirTarParse)] # go to next miRNA in list and call mirTarParse again
		elif self.tablePageNum < 12285: # if list is empty now, go to next page
			print ("PARSED PAGE# : " + str(self.tablePageNum) + "\n") # message on terminal
			self.tablePageNum += 1 # increment page
			tablePageUrl = getTableUrl(self.tablePageNum)
			return [scrapy.Request(url = tablePageUrl, callback = self.tableParse)] # go to next table page
		else: # all table pages read and parsed in file
			print ("PARSED PAGE# : " + str(self.tablePageNum) + "\n\n") # message on terminal
			print("DONE! :)\n\n") # message on terminal
			return None