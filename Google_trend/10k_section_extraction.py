import re
import os
from bs4 import BeautifulSoup
import string

import pandas as pd
import pdb
import datetime


def get_buz_sec(report_file_path):
	report = open(report_file_path).read()

	# Extract only 10k from the whole report
	doc = report[report.lower().index('<document>')+len('<document>'):report.lower().index('</document>')]


	# Clean file
	cleantext = BeautifulSoup(doc, "lxml").getText(separator=u'\n')

	cleantext = cleantext.replace('item', '\nitem')
	cleantext = cleantext.replace('Item', '\nItem')
	cleantext = cleantext.replace('ITEM', '\nITEM')

	cleantext = cleantext.replace('business', 'business\n')
	cleantext = cleantext.replace('Business', 'Business\n')
	cleantext = cleantext.replace('BUSINESS', 'BUSINESS\n')

	cleantext = cleantext.replace('properties', 'properties\n')
	cleantext = cleantext.replace('Properties', 'Properties\n')
	cleantext = cleantext.replace('PROPERTIES', 'PROPERTIES\n')


	# Getting business section from cleaned file
	s,s1,s2 = 0,0,0
	e,e1,e2 = 0,0,0

	text = ""
	flag_business_toc = 0

	lines = cleantext.splitlines()

	for i,line in enumerate(lines):
		line = re.sub("\.", "", line)
		temp_split_line = line.lower().split()
		#print(i, temp_split_line)

		if "item" in temp_split_line and "1" in temp_split_line and "business" in temp_split_line and len(temp_split_line) < 5:
			# found item business once before
			if flag_business_toc == 1:
				print("\t\ts2:", i, line[:80])
				s2 = i
				flag_business_toc += 1

			else:
				print("\t\ts1:", i, line[:80])
				s1 = i
				flag_business_toc += 1


		if "item" in temp_split_line and "2" in temp_split_line and "properties" in temp_split_line and len(temp_split_line) < 5:
			if flag_business_toc == 2:
				e2 = i
				print("\t\te2:", i, line[:80])
				break

			else:
				print("\t\te1:", i, line[:80])
				e1 = i

	# fetched some text
	if e2-s2>20:
		s,e = s2,e2
		text = "".join(line for line in lines[s2:e2+1] if "table of content" not in line.lower())

	# fetched some text
	elif e1-s1>20:
		s,e = s1,e1
		text = "".join(line for line in lines[s1:e1+1] if "table of content" not in line.lower())

	return text



def get_mdna_sec(report_file_path):
	report = open(report_file_path).read()

	if '<html>' in report:
		is_html = True
	else:
		is_html = False

	# Extract only 10k from the whole report
	# doc = report[report.lower().index('<document>')+len('<document>'):report.lower().index('</document>')]
	doc = report

	if not is_html:
		doc = doc.replace('\n', '\n<new line>')


	# Clean file
	cleantext = BeautifulSoup(doc, "lxml").getText(separator=u' ')

	cleantext = cleantext.replace('item', '\nitem')
	cleantext = cleantext.replace('Item', '\nItem')
	cleantext = cleantext.replace('ITEM', '\nITEM')

	# cleantext = cleantext.replace('management', '\nitem')
	# cleantext = cleantext.replace('Item', '\nItem')
	# cleantext = cleantext.replace('ITEM', '\nITEM')




	# with open('./clean.txt', 'w') as f:
	# 	f.write(cleantext)


	# Getting business section from cleaned file
	s,s1,s2 = 0,0,0
	e,e1,e2 = 0,0,0

	text = ""
	flag_business_toc = 0

	lines = cleantext.splitlines()

	for i,line in enumerate(lines):
		line = re.sub("\.", "", line)
		temp_split_line = line.lower().split()
		#print(i, temp_split_line)

		if "item" in temp_split_line and "7" in temp_split_line and "management" in line.lower() \
		and "discussion and analysis" in line.lower() and len(temp_split_line) <= 15:
			# found item business once before
			if flag_business_toc == 1:
				# print("\t\ts2:", i, line[:200])
				s2 = i
				flag_business_toc += 1

			else:
				# print("\t\ts1:", i, line[:200])
				s1 = i
				flag_business_toc += 1


		if "item" in temp_split_line and "8" in temp_split_line and "financial" in temp_split_line \
		and "statements" in temp_split_line and len(temp_split_line) <= 15:
			if flag_business_toc == 2:
				e2 = i
				# print("\t\te2:", i, line[:200])
				break

			else:
				# print("\t\te1:", i, line[:200])
				e1 = i

	# If we couldnt find anythin
	if s1 == 0 and s2 == 0:
		return ''

	# fetched some text	
	if e2-s2>20:
		s,e = s2,e2
		text = "".join(line for line in lines[s2:e2+1] if "table of content" not in line.lower())

	# fetched some text
	elif e1-s1>20:
		s,e = s1,e1
		text = "".join(line for line in lines[s1:e1+1] if "table of content" not in line.lower())

	if not text:
		if s1-e1<10:
			md_title = lines[s1].strip().rstrip(string.digits)[15:]
			fs_title = lines[e1].strip().rstrip(string.digits)[15:]

			cleantext = cleantext.replace(md_title, md_title + '\n')
			cleantext = cleantext.replace(fs_title, fs_title + '\n')

			# Getting business section from cleaned file
			s,s1,s2 = 0,0,0
			e,e1,e2 = 0,0,0

			text = ""
			flag_business_toc = 0

			lines = cleantext.splitlines()

			for i,line in enumerate(lines):
				line = re.sub("\.", "", line)
				temp_split_line = line.lower().split()
				#print(i, temp_split_line)

				if "item" in temp_split_line and "7" in temp_split_line and "management" in line.lower() \
				and "discussion and analysis" in line.lower() and len(temp_split_line) <= 15:
					# found item business once before
					if flag_business_toc == 1:
						# print("\t\ts2:", i, line[:200])
						s2 = i
						flag_business_toc += 1

					else:
						# print("\t\ts1:", i, line[:200])
						s1 = i
						flag_business_toc += 1


				if "item" in temp_split_line and "8" in temp_split_line and "financial" in temp_split_line \
				and "statements" in temp_split_line and len(temp_split_line) <= 15:
					if flag_business_toc == 2:
						e2 = i
						# print("\t\te2:", i, line[:200])
						break

					else:
						# print("\t\te1:", i, line[:200])
						e1 = i

			# fetched some text
			if e2-s2>20:
				s,e = s2,e2
				text = "".join(line for line in lines[s2:e2+1] if "table of content" not in line.lower())

			# fetched some text
			elif e1-s1>20:
				s,e = s1,e1
				text = "".join(line for line in lines[s1:e1+1] if "table of content" not in line.lower())

			text = text.replace(md_title, md_title + '\n', 1)

	if not is_html:
		text = text.replace('\n<new line>', ' ')


	return text



# # Main
# report_path = './dataset/320193/2011.txt'

# text = get_mdna_sec(report_path)

# # print(text)
# if text:
# 	with open('./bsection.txt', 'w') as f:
# 		f.write(text)

# quit()


filling_path = './only_10k/'
mdna_path = './mdna_dataset'
mdna_stats_path = './mdna_stats.txt'
cik2ticker_path = './cik2ticker.csv'

cik2ticker_list = open(cik2ticker_path).readlines()
cik2ticker_list = [i.strip() for i in cik2ticker_list]
cik2ticker = {}
for i in cik2ticker_list:
	cik = i.split('\t')[0]
	ticker = i.split('\t')[1]
	cik2ticker[cik] = ticker


mdna_stats = open(mdna_stats_path, 'w')
mdna_stats.write('cik\tticker\tyear\n')


cik_folders = os.listdir(filling_path)

for cik in cik_folders:
	ticker = cik2ticker[cik]
	# Create business section folder for cik if not present
	if not os.path.exists(mdna_path + '/' + cik):
		os.makedirs(mdna_path + '/' + cik)

	# For each year of that cik get business section
	years = os.listdir(filling_path + '/' + cik)
	for year in years:
		year_text = year.split('.')[0]
		report_path = filling_path + '/' + cik + '/' + year
		mdna_text = get_mdna_sec(report_path)

		# Line break if more than one consecutive spaces
		# mdna_text = re.sub('\s{2,}', '\n', mdna_text)

		if mdna_text:
			print('Writing: ' + str(cik) + '    ' + str(year))
			with open(mdna_path + '/' + cik + '/' + year, 'w') as f:
				f.write(mdna_text)

			mdna_stats.write(cik + '\t' + ticker + '\t' + year_text + '\n')
		else:
			print('Not Found: ' + str(cik) + '    ' + str(year))
			continue
			# print('MD&A section not found for ' + cik + ' for year ' + year)




# # For getting business section
# filling_path = './dataset/'
# business_path = './business_dataset'

# cik_folders = os.listdir(filling_path)

# for cik in cik_folders:
# 	# Create business section folder for cik if not present
# 	if not os.path.exists(business_path + '/' + cik):
# 		os.makedirs(business_path + '/' + cik)

# 	# For each year of that cik get business section
# 	years = os.listdir(filling_path + '/' + cik)
# 	for year in years:
# 		report_path = filling_path + '/' + cik + '/' + year
# 		business_text = get_buz_sec(report_path)

# 		# Line break if more than one consecutive spaces
# 		business_text = re.sub('\s{2,}', '\n', business_text)

# 		if business_text:
# 			with open(business_path + '/' + cik + '/' + year, 'w') as f:
# 				f.write(business_text)
# 		else:
# 			print('Business section not found for ' + cik + ' for year ' + year)




########################################################################

# findex = open(index_file, 'r').readlines()[1:]

# cik2years = {}
# for l in findex:
# 	cik = l.split()[0]
# 	years = l.split()[-1].split(',')

# 	cik2years[cik] = years

# for cik, years in cik2years.items():
# 	for year in years:
# 		report_path = filling_path + cik + '/' + year + '.txt'
# 		report = open(report_path).read()
# 		print(report_path)
# 		if '<html>' in report:
# 			print('html')
# 		else:
# 			print('text')



# if '<html>' in report.lower():
# 	pass
# else:
# 	# print(report)
# 	# docs = re.findall(r'<DOCUMENT>(.+?)</DOCUMENT>', report,flags=re.IGNORECASE)
# 	doc = report[report.lower().index('<document>')+len('<document>'):report.lower().index('</document>')]
# 	if '<TYPE>10-K\n' in doc.upper():
# 		print('10k extracted')
# 	else:
# 		print('10k is not the first DOCUMENT')