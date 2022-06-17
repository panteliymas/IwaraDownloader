from copyreg import constructor
from unittest import skip
from attr import s
import requests
import sys
import os
import re
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime

import config


def log(who, message):
	logLine = "[{}][{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), who.upper(), message)
	print(logLine)
	with open("IwaraDownloader.log", 'w') as logFile:
		logFile.write(logLine)


class Iwara:
	saveDir = config.IWARA_SAVE_DIR_DEFAULT
	timeOut = config.TIMEOUT
	lang = config.DEFAULT_LANG
	commonUrl = config.MAIN_DOMAIN_IWARA

	def __init__(self, timeOut=0, lang="", saveDir=""):
		# Creating new webdriver for Firefox
		options = webdriver.FirefoxOptions()
		options.add_argument("--headless")
		self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

		# Other configs
		if saveDir:
			log("log", "Chanching default saves directory to: " + saveDir)
			self.changeSaveDir(saveDir)
		if timeOut > 0:
			self.timeOut = timeOut
		if lang:
			self.lang = lang


	def skipR18Restrict(self, url=""):
		""" Passing the 18+ restriction popup """
		if url == "":
			url = self.commonUrl
		self.driver.get(url)
		if not self.driver.find_element(By.ID, 'r18-warning').get_attribute("style").find("display: none"):
			self.driver.find_element(By.CLASS_NAME, 'r18-continue').click()
			self.driver.refresh()


	def changeSaveDir(self, saveDir=""):
		""" --saveDir """
		if not os.path.isdir(saveDir):
			log("SYSTEM", "Path you provided doesn't exist. Would you like to create it? (yes/no) ")
			createDir = input()
			while createDir not in ["yes", "no"]:
				createDir = input("[LOG] Please, type 'yes' or 'no': ")
			if createDir == 'no':
				log("LOG", "Default saves directory will be used:" + self.saveDir + ".\n")
				return
			os.makedirs(saveDir)
		self.saveDir = saveDir
		if not self.saveDir.endswith(os.path.sep):
			self.saveDir = self.saveDir + os.path.sep


	def getFromUrl(self, url):
		""" Downloads a video by url provided with --url arg """
		# Skipping age restriction if any appears
		self.skipR18Restrict(url)

		self.driver.get(url)

		# Waiting for page loading
		WebDriverWait(self.driver, self.timeOut).until(lambda d: d.find_element(By.CSS_SELECTOR, '#download-options .list-unstyled a'))
		downloadLink = self.driver.find_element(By.CSS_SELECTOR, '#download-options .list-unstyled a')
		print(downloadLink.get_attribute('href'))


	def getAll(self):
		url = self.commonUrl + '?sort=date&page={}&language={}'
		self.driver.get(url.format('0', self.lang))
		lastPage = int(re.search(r'(?<=page=)\d+', self.driver.find_element(By.CLASS_NAME, 'pager-last').find_element(By.TAG_NAME, 'a').get_attribute('href')).group(0))

		#Getting last uid saved last time (if any)
		self.getLastSavedUID()
		
		#Following to vids pages
		for pageNum in range(lastPage+1):
			iwaraVids = self.driver.find_elements(By.CSS_SELECTOR, '.content .node .title a')
			for vid in iwaraVids:
				print(vid.get_attribute('href').split('/')[-1].split('?')[0])
			break


	def getLastSavedUID(self):
		""" Get uid last saved last time (if any) otherwise create a file to save it in future """
		if os.path.isfile('last_uid'):
			with open('last_uid', 'rb') as lastUidFile:
				self.lastUID = lastUidFile.read()
		else:
			self.lastUID = -1


	def setLastUID(self, uid):
		""" Get uid last saved last time (if any) otherwise create a file to save it in future """
		if os.path.isfile('last_uid'):
			with open('last_uid', 'w') as lastUidFile:
				lastUidFile.write(uid)


	def getFromUID(self, UID):
		""" Downloads a video by UID provided with --uid arg """
		pass


	def help(self):
		""" Show information about this script and its arguments """
		pass


	def __del__(self):
		self.driver.quit()



def main(args):
	sd = ""
	lang = ""
	timeout = 30
	if "--saveDir" in sys.argv:
		sd = sys.argv[sys.argv.index('--saveDir')+1]
	if "--lang" in sys.argv:
		lang = sys.argv[sys.argv.index('--lang')+1]
	if "--timeOut" in sys.argv:
		timeout = sys.argv[sys.argv.index('--timeOut')+1]
	iwara = Iwara(saveDir=sd, lang=lang, timeOut=timeout)
	if "--url" in sys.argv:
		iwara.getFromUrl(sys.argv[sys.argv.index('--url')+1])
	else:
		iwara.getAll()

# Start main program
if __name__ == '__main__':
	main(sys.argv)
