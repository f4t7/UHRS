from google_trans_new import google_translator#############################################
from bs4 import BeautifulSoup##############################################################
import mysql.connector#####################################################################
import urllib.request#####██╗####██╗██╗####██╗███████╗███████╗#############################
import requests###########██║####██║██║####██║██║##██║██╔════╝#############################
import winsound###########██║####██║█████████║███████║███████╗#############################
import time###############██║####██║██╔════██║██║██══╝╚════██║#############################
import json###############╚███████╔╝██║####██║██║╚███╗███████║#############################
import sys################ ╚══════╝ ╚═╝####╚═╝╚═╝ ╚══╝╚══════╝#############################
import re##################################################################################
import os##################################################################################



##########################################[ERROR]##########################################

class Error:
	def __init__(self, code, function):
		self.code = code
		self.function = function

	@staticmethod
	def eCode(code, function):
		DisplayOutput.printer(code+" Occured in ["+function+"] function")
		os._exit(0)

##########################################[INPUT]##########################################
class Input:
	def diseaseInput():
		try:
			os.system('cls')
			DisplayOutput.printBanner()
			DisplayOutput.printer("Write search term for Input")
			inputDisease = input(">> ").lower()
			os.system('cls')
			DisplayOutput.printBanner()
			DisplayOutput.printer("Input was " + inputDisease)
			verify = VerifyDiseaseName.ifexists(inputDisease)
			if verify[0] is False:
				Input.tryagain(verify[1])
			else:
				DisplayOutput.printer("MAY ALLAH GIVE YOU MORE SHIFA!")

		except:
			Error.eCode("InputError","diseaseInput")
	def tryagain(inputDisease):
		try:
			os.system('cls')
			DisplayOutput.printBanner()
			DisplayOutput.printer("Could not find data for\n["+inputDisease+"]\nWould you like to Try Again? (Y/N)")
			tryagain = input("[ (Y)es/(N)o ]>> ").lower()			
			if tryagain in ('n','no'):
				os.system('cls')
				DisplayOutput.printBanner()
				DisplayOutput.printer("Thank you for using my APP")
			elif tryagain in ('y','yes'):
				Input.diseaseInput()
			else:
				winsound.Beep(500,400)
				Input.tryagain(inputDisease)	
		except:
			Error.eCode("InputError","tryagain")	
##########################################[VERIFY DISEASENAME]##########################################
class VerifyDiseaseName:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue
	
	def ifexists(inputvalue):
		try:
			diseasename = InternetSources.verifysrc(inputvalue)
			if diseasename is False:
				winsound.Beep(500,400)
				return [False,inputvalue]
			confirm = MySQL.ifexistsindb(diseasename[0])
			if confirm is True:
				diseasename[1] = True
			CollectData.collect(diseasename)
			return [True]
		except:
			Error.eCode("VerifyError","ifexists")

##########################################[INTERNET SOURCES]##########################################
class InternetSources:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue
	
	def verifysrc(inputvalue):
		name = []
		names = []
		number = []
		listed = []
		linking = []
		accuratelinks = []

		searchstr = inputvalue.split()
		avoid = ["top","should","what","when","where","who","how","why","is","can","at","are","am","do","does"]
		try:
			datas = [requests.get('https://www.rxlist.com/diseases-conditions-medical-tests/alpha_'+str(char[0])+'.htm').text for char in searchstr]
			linksdic = [str(BeautifulSoup(data, features="lxml").find('div', {'class':'AZ_results'})).split('\n') for data in datas] 
			links = [link for linked in linksdic for link in linked]
			for link in links:
				try: 
					for string in searchstr:
						if string in re.sub(r"[^A-Za-z]+", ",", link.lower()).split(","):
							linked = re.search(r'href="([^"]+)', link).group().replace('href="','')
							if re.sub(r'.*\.com/|_.*$','',linked).strip().lower() not in avoid:
								linking.append(linked)
				except:
					pass
			if not linking:
				return False
			
			linking = list(dict.fromkeys(linking))

			for i in range(len(linking)):
				dName = InternetSources.getdiseasename(linking[i])
				if re.sub(r' .*',"",dName).strip().lower() in avoid:
					continue
				if InternetSources.getdiseaseinfo(dName, 'consult') is not False:
					n = 0
					for string in searchstr:
						if string.lower() in dName.lower():
							n+=1
					if n > 0:
						listed.append((n,linking[i],dName))
						number.append(n)
			if not listed:
				return False		
			
			position = [i for i, x in enumerate(number) if x == max(number)]
			
			for i in position:
				j = listed[i]
				accuratelinks.append(j[1])
				names.append(j[2])			
			if len(names) == 1:
				choice = 0
			else:
				choice = len(names)+1
				while choice not in range(len(names)):
					os.system('cls')
					DisplayOutput.printBanner()
					DisplayOutput.printer("I have found "+str(len(names))+" matches from [Internet Sources]:\nPlease choose one to proceed")		
					DisplayOutput.ask(names)
					n = re.sub(r'[^0-9]+','',input(">> "))
					if n:
						choice = int(n)-1
					if choice not in range(len(names)):
						winsound.Beep(500,400)

							
			return [names[choice],accuratelinks[choice]]
		except:
			Error.eCode("SourcesError", "verifysrc")

	def collectdata(inputvalue):
		diseasename = inputvalue[0]		
		target = inputvalue[1]
		try:
			types = ['what']
			symptoms = ['symptom']
			precautions = ['prevent']
			advices = ['advice','diagnose', 'should']
			consultants = ['consult']

			trylist = [types, symptoms, precautions, advices, consultants]
			
			diseaseinfo = [diseasename]
			
			for info in trylist:
				if info == consultants:
					consults = InternetSources.getdiseaseinfo(diseaseinfo[0], consultants[0])
					if consults is False:
						diseaseinfo.append("no consultant found")
						diseaseinfo.append(None)
						break
					else:
						consult = ', '.join([str(consultant) for consultant in consults])
						diseaseinfo.append(consult)
						doctors = InternetSources.getdoctor(consults)
						diseaseinfo.append(doctors)
						break
				else:
					for argument in info:
						data = InternetSources.getdiseaseinfo(target, argument)
						if data is not False:
							diseaseinfo.append(data.strip())
							break
					if data is False:
						diseaseinfo.append("sorry could not find")
			return diseaseinfo		
		except:
			Error.eCode("SourcesError", "collectdata")

	def getdoctor(type):
		typeArr = type
		locations = ['karachi', 'lahore', 'rawalpindi', 'faisalabad', 'islamabad', 'peshawar', 'multan', 'quetta', 'gujranwala', 'sargodha', 'abbottabad', 'alipur', 'attock', 'bahawalpur', 'buner', 'burewala', 'chakwal', 'chichawatni', 'dera-ghazi-khan', 'dina', 'gojra', 'gujar-khan', 'gujrat', 'hafizabad', 'haripur', 'hyderabad', 'jampur', 'jamshoro', 'jauharabad', 'jhelum', 'kasur', 'khanewal', 'khanpur', 'khushab', 'kot-addu', 'larkana', 'layyah', 'lodhran', 'mansehra', 'mardan', 'mirpur-khas', 'mithi', 'muzaffar-garh', 'nawabshah', 'okara', 'pattoki', 'rahim-yar-khan', 'sadiqabad', 'sahiwal', 'samundri', 'shahkot', 'sheikhupura', 'sialkot', 'sawabi', 'sawat', 'talagang', 'taxila', 'toba-tek-singh', 'topi', 'wah-cantt']
		doctors = []
		filtering = {"oral and maxillofacial surgeon":"Maxillofacial Surgeon", "internal medicine specialist":"Internal Medicine", "laparoscopic surgeon":"Laproscopic Surgeon", "orthotist and prosthetist":"Orthotist-Prosthetist", "pediatric oncologist and hematologist":"Pediatric Oncologist Hematologist", "bariatric / weight loss surgeon":"Bariatric Surgeon", "neurologist":"Neuro Physician"} 					
		avoidit = ["specialist","dietitian"]
		
		try:			
			for spec in typeArr:
				verifySpec = MySQL.checkSpecialist(spec)
				if verifySpec is False:
					spec_ = re.sub(r' ','-',spec)

					for location in locations:
						try:
							data = requests.get("https://www.marham.pk/doctors/"+ location + "/" + spec_.lower())
						except:
							continue
						soup = BeautifulSoup(data.content, "html.parser")
						script = soup.find_all('script' , {"type" : "application/ld+json"})
						for i in script:
							data = json.loads(i.text.strip())
							try:
								if data['medicalSpecialty']['name']:
									dis_name = data['medicalSpecialty']['name']
								if "/" in dis_name:
									j = dis_name.split("/")
									for l in avoidit:
										if l in j[0].lower():
											dis_name = j[1].strip()
											break
										if l in j[1].lower():
											dis_name = j[0].strip()
											break
								
								for i in filtering:
									if i.lower() == dis_name.lower():
										dis_name = filtering[dis_name.lower()]		
								if dis_name.lower() == spec.lower():
									name = data['name']
									addr = data['location']['address']['name']
									price = data['hospitalAffiliation']['priceRange']
									spec = dis_name
									avlb = data['openingHours']
									hspt = data['hospitalAffiliation']['name']

									doctors.append([location,spec,price,avlb,name,spec,addr,hspt])
									wait = "[ Finding " + spec +" in "+ location +" ]" 
									print(" "+"═"*int((168-len(wait))/2) + wait + "═"*int((168-len(wait))/2), end='\r')
							except KeyError:
								pass
				else:
					continue
			return doctors	
		except:
			Error.eCode("SourcesError", "getdoctor")		
	def getdiseasename(linkToName):	
		extra = ["what is ","what are ", "?"]
			
		try:	
			data = requests.get(linkToName).text
			soup = BeautifulSoup(data, features="lxml")
			if soup.find('div',{'class':'hero'}):
				hero = soup.find('div',{'class':'hero'})
			elif soup.find('div',{'id':'headline'}):
				hero = soup.find('div',{'id':'headline'})
			children = hero.findChildren("h1" , recursive=False)
			
			for child in children:
				diseasename = child.get_text()	
			for i in range(len(extra)):
				if extra[i] in diseasename.lower():	
					diseasename = diseasename.lower().replace(extra[i],'')	
			return diseasename.capitalize()
		except:
			Error.eCode("SourcesError", "getdiseasename")
	def getdiseaseinfo(linktoType, keyword):
		avoidit = ["specialist","dietitian"]
		filtering = {"oral and maxillofacial surgeon":"Maxillofacial Surgeon", "internal medicine specialist":"Internal Medicine", "laparoscopic surgeon":"Laproscopic Surgeon", "orthotist and prosthetist":"Orthotist-Prosthetist", "pediatric oncologist and hematologist":"Pediatric Oncologist Hematologist", "bariatric / weight loss surgeon":"Bariatric Surgeon", "neurologist":"Neuro Physician"} 				
		avoid = ["different","forms","of","and","about","type","types", "in", "the", "or", "eg","to","due","from","a", "issues", "men","may","result","be","growth","poor","high","later","related"]
						
		try:
			if keyword != "consult":
				data = requests.get(linktoType).text
				soup = BeautifulSoup(data, features="lxml")
				wrapper = soup.find_all('div',{'class':'wrapper'})
				typetext = ""
				for wrap in wrapper:
					div = wrap.findChildren("div" , recursive=False)
					if not typetext:
						for dave in div:
							h3 = dave.get_text()
							if keyword in h3.lower():
								dave.decompose()
								typetext = wrap.get_text()
								break					
				if typetext:
					return typetext
				else:
					for wrap in wrapper:
						div = wrap.findChildren("div" , recursive=False)
						for dave in div:
							dave.decompose()
						if keyword in wrap.get_text():
							return wrap.get_text()
					return False				
			else:
				diseasename = re.sub(r'[^A-Za-z ]+', '', linktoType)
				words = diseasename.lower().split()
				data = requests.get("https://www.marham.pk/all-diseases")
				soup = BeautifulSoup(data.content, features="html.parser")
				columns = soup.find_all('div',{'class':'col-12 p-3'})
				results = []
				disease_consult = []
				consulted = []
				for column in columns:
					h3 = column.find_all('h3')
					if h3:
						divs = column.find_all('div')
						for div in divs:
							consulted.append(div.get_text().split("\n"))	
					if not h3:
						consulted.append(column.get_text().split("\n"))
				
				for i in consulted:
					consulting = [x for x in i if x]
					if "/" in consulting[0]:
						j = consulting[0].split("/")
						for l in avoidit:
							if l in j[0].lower():
								consulting[0] = j[1].strip()
								break
							if l in j[1].lower():
								consulting[0] = j[0].strip()
								break
					for i in filtering:
						if i.lower() == consulting[0].lower():
							consulting[0] = filtering[consulting[0].lower()]
					for m in range(len(consulting)-1):
						disease_consult.append((consulting[0],consulting[m+1]))
				
				accuracy = []	
				number = []
				trimthem = ['']
				for i in disease_consult:
					n=0
					compare = re.sub("/|'s+|-", " ", i[1])
					compare = re.sub('[^A-Za-z ]+', '', compare)
					for word in words:
						for j in compare.split():
							if j.lower() in avoid:
								continue
							j = re.sub("s$", "", j)
							if j.lower() == word.lower():
								n+=1
								continue
							if j.lower()+"s" == word.lower():
								n+=1
								continue	

					if n > 0:
						accuracy.append((n,i[0],i[1]))
						number.append(n)

				if not number:
					return False
				position = [i for i, x in enumerate(number) if x == max(number)]
				
				consultants = []
				for i in position:
					j = accuracy[i]
					consultants.append(j[1])
				consultants = list(dict.fromkeys(consultants))
				
				if len(consultants) > 1:
					return consultants[:2]

				return consultants
		except:
			Error.eCode("SourcesError", "getdiseaseinfo")

##########################################[MY SQL]##########################################
class MySQL:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue

	def checkSpecialist(spec):
		try:
			MySQL.dbverify()
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			match_q = 'SELECT SPECIALTYENG FROM CONSULTANTS WHERE SPECIALTYENG = %s'
			cur.execute(match_q, (spec.lower(),))
			match_v = cur.fetchone()
			if match_v:
				return True
			else:
				return False
		except:
			Error.eCode("MySQLError", "ifexistsindb")

	def ifexistsindb(diseasename):
		try:
			MySQL.dbverify()
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			match_q = 'SELECT NAMEENG FROM DISEASES where NAMEENG = %s'
			cur.execute(match_q, (diseasename.lower(),))
			match_v = cur.fetchone()
			if match_v:
				return True
			else:
				return False
		except:
			Error.eCode("MySQLError", "ifexistsindb")		

	def fetchlocations(specialist):
		try:
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			match_q = 'SELECT LOCATION FROM CONSULTANTS WHERE SPECIALTYENG = %s'
			cur.execute(match_q, (specialist.lower(),))
			match_v = cur.fetchall()
			match_v = list(dict.fromkeys(match_v))
			data = [row[0] for row in match_v]
			return data
		except:
			Error.eCode("MySQLError", "fetchdata")

	def fetchdata(inputvalue):
		try:
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			match_q = 'SELECT CONSULTANTENG, NAME, TYPE, SYMPTOM, PRECAUTION, DOCTORADVICE, CONSULTANT FROM DISEASES WHERE NAMEENG = %s'
			cur.execute(match_q, (inputvalue.lower(),))
			match_v = cur.fetchone()
			
			if match_v:
				data = [i for i in match_v]
				return data
			else:
				return False
		except:
			Error.eCode("MySQLError", "fetchdata")


	def fetchdoctor(specialist, location):
		try:
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			match_q = 'SELECT * FROM CONSULTANTS WHERE SPECIALTYENG = %s AND LOCATION = %s'
			match = (specialist.strip().lower(), location.strip().lower(),)
			cur.execute(match_q, match)
			match_v = cur.fetchall()
			data = [i for i in match_v]
			if not data:
				data = ['NotFound', specialist, location]
			return data
		except:
			Error.eCode("MySQLError", "fetchdata")
		
	def dbverify():
		try:
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass)
			cur = db.cursor()
			cur.execute("CREATE DATABASE IF NOT EXISTS UHRS")
			cur.execute("USE UHRS")
			cur.execute("CREATE TABLE IF NOT EXISTS DISEASES(SN int, NAMEENG LONGTEXT, CONSULTANTENG LONGTEXT, NAME LONGTEXT, TYPE LONGTEXT, SYMPTOM LONGTEXT, PRECAUTION LONGTEXT, DOCTORADVICE LONGTEXT, CONSULTANT LONGTEXT CHARSET ucs2)")
			cur.execute("CREATE TABLE IF NOT EXISTS CONSULTANTS(SN int, LOCATION varchar(500), SPECIALTYENG varchar(500), FEES varchar(500), AVAILABLE varchar(500), NAME varchar(500), SPECIALTY varchar(500), ADDRESS varchar(500), SERVICE varchar(500) CHARSET ucs2)")
			db.commit()
		except:
			Error.eCode("MySQLError", "dbverify")

	def updatedb(inputvalue):
		try:
			MySQL.dbverify()
			db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
			cur = db.cursor()
			count = 'SELECT COUNT(*) FROM DISEASES'
			cur.execute(count)
			nextrow = cur.fetchone()
			s = 'INSERT INTO DISEASES VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
			diseaseinfo = (nextrow[0],inputvalue[1],inputvalue[2],inputvalue[3],inputvalue[4],inputvalue[5],inputvalue[6],inputvalue[7],inputvalue[8])
			cur.execute(s,diseaseinfo)
			db.commit()
		except:
			Error.eCode("MySQLError", "updatedb")

		if inputvalue[0] is not None:
			try:
				MySQL.dbverify()
				db = mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass, database='uhrs')
				cur = db.cursor()
				doctors = inputvalue[0]
				for num in range(len(doctors)):
					count = 'SELECT COUNT(*) FROM CONSULTANTS'
					cur.execute(count)
					nextrow = cur.fetchone()
					s = 'INSERT INTO CONSULTANTS VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
					doctor = (nextrow[0],doctors[num][0],doctors[num][1],doctors[num][2],doctors[num][3],doctors[num][4],doctors[num][5],doctors[num][6],doctors[num][7])
					cur.execute(s,doctor)
				db.commit()
			except:
				Error.eCode("MySQLError", "updatedb")

##########################################[COLLECT DATA]##########################################		
class CollectData:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue

	def collect(inputvalue):
		try:
			if inputvalue[1] is not True:
				os.system('cls')
				DisplayOutput.printBanner()
				DisplayOutput.printer("["+inputvalue[0]+"]\nDoes not exist in Database.\nFetching from Internet Sources.")
				update = InternetSources.collectdata(inputvalue)
				MySQL.updatedb(TranslateData.translate(update))

			data = MySQL.fetchdata(inputvalue[0])
			printer = True
			while printer:
				doctors = CollectData.collectDoc(data[0])
				try:
					if doctors[0] is False:
						while True:
							os.system('cls')
							DisplayOutput.printBanner()
							DisplayOutput.printer("No [ "+ doctors[1] +" ] available in [ "+doctors[2]+" ]" + "\nWould you like to see other specialist or location?")
							decision = input("[ (Y)es/(N)o ]>> ")
							if decision.lower() not in ("no", "n", "yes", "y"):
								winsound.Beep(500,400)
								continue
							if decision.lower() in ("no", 'n'):
								os.system('cls')
								DisplayOutput.printBanner()
								del data[0]
								DisplayOutput.output(data)
								printer = False
								break
					else:
						os.system('cls')
						DisplayOutput.printBanner()
						del data[0]	
						DisplayOutput.output(data)	
						DisplayOutput.printer("Consultants")
						for doctor in doctors:
							DisplayOutput.doctors(doctor)
						break				
				except:
					break	
		except:
			Error.eCode("CollectError", "collect")

	def collectDoc(data):
		typeArr = []
		if ',' in data:
			typeArr = [ i.strip() for i in data.split(',') if i]
		else:
			typeArr.append(data.strip())
		typeArr = [x for x in typeArr if x]
		if len(typeArr) > 1:
			value = len(typeArr)+1
			while value not in range(len(typeArr)):
				os.system('cls')
				DisplayOutput.printBanner()
				DisplayOutput.printer("Recommended Specialists")
				DisplayOutput.ask(typeArr)
				DisplayOutput.printer("Enter number corresponding to your desired Specialist:")
				n = re.sub("[^0-9]+","",input(">> "))
				if n:
					value = int(n)-1
				if value not in range(len(typeArr)):
					winsound.Beep(500,400)

			specialist = typeArr[value]
		else:
			specialist = typeArr[0]
		locations = MySQL.fetchlocations(specialist)
		if locations:
			value = len(locations)+1
			while value not in range(len(locations)):
				os.system('cls')
				DisplayOutput.printBanner()
				DisplayOutput.printer("[ "+ specialist +" ]\n Available in")
				DisplayOutput.ask(locations)
				DisplayOutput.printer("Enter number corresponding to your location:")
				n = re.sub("[^0-9]+","",input(">> "))
				if n:
					value = int(n)-1
				if value not in range(len(locations)):
					winsound.Beep(500,400)
					
			location = locations[value]
			return MySQL.fetchdoctor(specialist, location)
		else:
			return [False,specialist,"Database"]

##########################################[TRANSLATE DATA]##########################################
class TranslateData:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue

	def translate(inputvalue):
		try:
			days = {'mo':'monday','tu':'tuesday','we':'wednesday','th':'thursday','fr':'friday','sa':'saturday','su':'sunday'}
			doctors = []
			count = 0
			for doc in inputvalue[6]:
				doctor = [doc[0],doc[1],doc[2]]
				del doc[:3]
				for word, initial in days.items():
					doc[0] = doc[0].lower().replace(word.lower(), initial)
				for line in doc:
					try:
						t = google_translator().translate(line, lang_src='en', lang_tgt= 'ur')
					except:
						try:
							reg = re.sub(r'[^A-Za-z0-9.,:! ]', ' ', line)
							reg = re.sub(r'(?<=[.,:!])(?=[^\s])', r' ', reg)
							t = google_translator().translate(reg, lang_src='en', lang_tgt= 'ur')
						except:
							t = line
							pass
					wait = "═"*doc.index(line)+"["+" Translating Consultants ("+str(count)+"/"+str(len(inputvalue[6]))+") "+"]"+"═"*doc.index(line)
					print(" "+" "*int((168-len(wait))/2) + wait + " "*int((168-len(wait))/2), end='\r')		
					doctor.append(t)
				count+=1
				doctors.append(doctor)
			
			output = [doctors ,inputvalue[0], inputvalue[5]]
			del inputvalue[6]
			for para in inputvalue:
				try:
					reg = re.sub(r'[^A-Za-z0-9.,:! ]', ' ', para)
					reg = re.sub(r'(?<=[.,:!])(?=[^\s])', r' ', reg)
					t = google_translator().translate(reg[:4999], lang_src='en', lang_tgt= 'ur')
				except:
					try:
						t = google_translator().translate(para[:4999], lang_src='en', lang_tgt= 'ur')
					except:
						t = para
						pass
				wait = "═"*inputvalue.index(para)+"["+" Translating Disease Data ("+str(inputvalue.index(para))+"/"+str(len(inputvalue))+") "+"]"+"═"*inputvalue.index(para)
				print(" "+" "*int((168-len(wait))/2) + wait + " "*int((168-len(wait))/2), end='\r')		
				output.append(t)				
			return output
		except:
			Error.eCode("TranslateError", "translate")
##########################################[DISPLAY OUTPUT]##########################################
class DisplayOutput:
	def __init__(self, inputvalue):
		self.inputvalue = inputvalue

	def ask(inputvalue):
		try:
			print("╔════╗ ╔"+"═"*161+"╗")	
			for n in range(len(inputvalue)):
				if n < 9:
					num = '0'+str(n+1)
				else:
					num = str(n+1)
				print('║ '+num+' ║ ║ '+str(inputvalue[n])+' '*(159-len(inputvalue[n]))+' ║')
			print("╚════╝ ╚"+"═"*161+"╝")
		except:
			Error.eCode("DisplayError", "output")
	
	def output(inputvalue):
		try:
			title = ['Disease Name:', 'Disease Type:', 'Symptoms:', 'Precautions:', 'Doctor Advice:', 'Relevant Consultant/Doctor:']
			for i in range(len(inputvalue)):
				length = 167-len(title[i])
				print("\n╔"+"═"*168+"╗")
				print("║ "+title[i]+" "*length+"║")
				print("╠"+"═"*168+"╣")
				for j in re.sub("(.{,155}[ ])", "\\1\n", inputvalue[i], 0, re.DOTALL).splitlines():
					lines = [ i.strip() for i in j.split('\n') if i]
					for line in lines:
						newline = ' '.join([words for words in list(reversed(re.split(r'([A-Za-z0-9]+)', line)))])
						print("║"+newline.rjust(167, " ")+" ║")
				print("╚"+"═"*168+"╝")
		except:
			Error.eCode("DisplayError", "output")
	
	def printer(text):
		try:
			lines = [line for line in re.split(r'\n', text) if line]
			print("╔"+"═"*168+"╗")	
			for line in lines:
				space = int((168-len(line))/2)
				print("║"+" "*space+line+" "*space + " "*int(len(line)%2) +"║")
			print("╚"+"═"*168+"╝")
		except:
			Error.eCode("DisplayError", "printer")

	def doctors(doctor):
		try:
			data = {'Name':doctor[5], 'Specialty':doctor[6], 'Fees':doctor[3], 'Address':doctor[7], 'Service':doctor[8], 'Available':doctor[4]}
			print("╔"+"═"*154+"╗ ╔═══════════╗")
			for n in data:
				newline = ' '.join([words for words in list(reversed(re.split(r'([A-Za-z0-9]+)', data[n])))])
				print("║ "+newline.rjust(152, " ")+" ║ ║ " + " "*(9-len(n)) + str(n) +" ║")
			print("╚"+"═"*154+"╝ ╚═══════════╝")
		except:
			Error.eCode("DisplayError", "doctors")	

	def printBanner():
		print("""

								██╗    ██╗██╗    ██╗███████╗███████╗
								██║    ██║██║    ██║██║  ██║██╔════╝
								██║    ██║█████████║███████║███████╗
								██║    ██║██╔════██║██║██══╝╚════██║
								╚███████╔╝██║    ██║██║╚███╗███████║
 								 ╚══════╝ ╚═╝    ╚═╝╚═╝ ╚══╝╚══════╝
		""")

try:
	SQLuser = sys.argv[1]
	SQLpass = sys.argv[2]
except:
	os.system('cls')
	DisplayOutput.printBanner()
	DisplayOutput.printer("Incorrect format!")
	DisplayOutput.printer("Try:\npython uhrs.py [MySQL username] [MySQL password]")
	DisplayOutput.printer("For Example:\npython uhrs.py root toor")
	sys.exit()
try:
	mysql.connector.connect(host='localhost', user=SQLuser, password=SQLpass)
	Input.diseaseInput()
except:
	os.system('cls')
	DisplayOutput.printBanner()
	DisplayOutput.printer("MySQL username or password was incorrect!")


