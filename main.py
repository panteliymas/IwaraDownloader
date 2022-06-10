import requests
import sys
import os
import re
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def main(args, driver, lang='en'):
	url = 'https://ecchi.iwara.tv/videos?sort=date&page={}&language={}'
	if '--url' in args:
		getFromUrl(sys.argv[sys.argv.find('--url')+1])
		url = sys.argv[sys.argv.find('--url')+1]
		vidUrl = BeautifulSoup(requests.get(url).content)
	else:
		#Getting last page
		driver.get(url.format('0', lang))
		lastPage = int(re.search(r'(?<=page=)\d+', driver.find_element(By.CLASS_NAME, 'pager-last').find_element(By.TAG_NAME, 'a').get_attribute('href')).group(0))

		#Getting last uid saved last time (if any)
		lastUID = getLastSavedUID()
		
		#Following to vids pages
		for pageNum in range(lastPage+1):
			iwaraVids = driver.find_elements(By.CSS_SELECTOR, '.content .node .title a')
			for vid in iwaraVids:
				print(vid.get_attribute('href').split('/')[-1].split('?')[0])
			
			# if (lastUID):
			# 	if (lastUID):
			# 		break
			break

def getLastSavedUID():
	""" Get uid last saved last time (if any) otherwise create a file to save it in future """
	if os.path.isfile('last_uid'):
		with open('last_uid', 'rb') as lastUidFile:
			return lastUidFile.read()
	else:
		lastUIDFile = open('last_uid', 'w')
		lastUIDFile.close()
		return -1

def getAll(saveLast=True):
	""" Downloads all videos from Iwara if --all arg is provided """
	pass

def getFromUrl(url):
	""" Downloads a video by url provided with --url arg """
	pass

def getFromUID(UID):
	""" Downloads a video by UID provided with --uid arg """
	pass

def save(saveDir=''):
	""" Saves a video into daefault directory (or a directory provided with --saveDir arg) """
	pass

def help():
	""" Show information about this script and its arguments """
	pass

if __name__ == '__main__':
	# Creating new webdriver for Firefox
	options = webdriver.FirefoxOptions()
	options.add_argument("--headless")
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

	# Passing the 18+ restriction popup
	driver.get('https://ecchi.iwara.tv/')
	driver.find_element(By.CLASS_NAME, 'r18-continue').click()
	driver.refresh()

	# Start main program
	main(sys.argv, driver)
	driver.quit()
