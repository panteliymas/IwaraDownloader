from unittest import skip
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

import config

def main(args, lang='en'):
	# --saveDir
	if '--saveDir' in sys.argv:
		if not os.path.isdir(sys.argv[sys.argv.index('--saveDir')+1]):
			print("Path you provided doesn't exist. Would you like to create it? (yes/no)")
			while input() not in ["yes", "no"]:
				print("Please, type 'yes' or 'no': ")
			os.makedirs(sys.argv[sys.argv.index('--saveDir')+1])
		saveDir = sys.argv[sys.argv.index('--saveDir')+1]
		if not saveDir.endswith(os.path.sep):
			saveDir = saveDir + os.path.sep

	# Creating new webdriver for Firefox
	options = webdriver.FirefoxOptions()
	options.add_argument("--headless")
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

	# --url
	url = commonUrl + '?sort=date&page={}&language={}'
	skipR18Restrict(driver, url.format(0, 'en'))
	if '--url' in args:
		print(sys.argv[sys.argv.index('--url')+1])
		getFromUrl(driver, sys.argv[sys.argv.index('--url')+1])
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
			
			if (lastUID != -1):
			# 	if (lastUID):
			# 		break
				pass
			break
	driver.quit()

def skipR18Restrict(driver, url):
	""" Passing the 18+ restriction popup """
	driver.get(url)
	if not driver.find_element(By.ID, 'r18-warning').get_attribute("style").find("display: none"):
		driver.find_element(By.CLASS_NAME, 'r18-continue').click()
		driver.refresh()

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

def getFromUrl(driver, url):
	""" Downloads a video by url provided with --url arg """
	skipR18Restrict(driver, url)
	print(driver.get(url))
	downloadLink = driver.get(url).find_element(By.CSS_SELECTOR, '#download-options .list-unstyled a')
	print(downloadLink.get_attribute('href'))


def getFromUID(UID):
	""" Downloads a video by UID provided with --uid arg """
	pass

def save(saveDir=''):
	""" Saves a video into daefault directory (or a directory provided with --saveDir arg) """
	pass

def help():
	""" Show information about this script and its arguments """
	pass

saveDir = config.IWARA_SAVE_DIR_DEFAULT
commonUrl = config.MAIN_DOMAIN_IWARA

if __name__ == '__main__':
	# Start main program
	main(sys.argv)
