from copyreg import constructor
from itertools import groupby
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


def log(message, who="log", isInput=False):
	logLine = "[{}][{}] - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), who.upper(), message.upper())
	
	with open("IwaraDownloader.log", 'a') as logFile:
		logFile.write(logLine)
	if isInput:
		return input(logLine+"\n")
	print(logLine)


class Iwara:
	saveDir = config.IWARA_SAVE_DIR_DEFAULT
	timeOut = 30
	lang = 'en'
	commonUrl = config.MAIN_DOMAIN_IWARA
	groupByOptions = ["day", "author"]
	groupBy = None
	lastUID = None

	def __init__(self, timeOut=0, lang=""):
		log("downloader launched")
		self.oldPath = os.environ["PATH"]
		os.environ["PATH"] += ":" + os.path.abspath('./')

		# Creating new webdriver for Firefox
		options = webdriver.FirefoxOptions()
		options.add_argument("--headless")
		# self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
		self.driver = webdriver.Firefox(options=options)

		# Other configs
		if timeOut > 0:
			self.timeOut = timeOut


	def setGrouping(self, groupBy):
		""" If you want to group by some option in different optins you can provide --groupBy arg """
		if groupBy in self.groupByOptions:
			self.groupBy = groupBy
		else:
			log("not supported grouping option, will not be grouped")


	def skipR18Restrict(self, url=""):
		""" Passing the 18+ restriction popup """
		if url == "":
			url = self.commonUrl
		self.driver.get(url)
		if not self.driver.find_element(By.ID, 'r18-warning').get_attribute("style").find("display: none"):
			self.driver.find_element(By.CLASS_NAME, 'r18-continue').click()
			self.driver.refresh()


	def changeSaveDir(self, saveDir="", force=False):
		""" --saveDir """
		if not force:
			log("Changing default saves directory to: " + saveDir)
		if not os.path.isdir(saveDir):
			createDir = "yes" if force else log("Path you provided doesn't exist. Would you like to create it? (yes/no) ", isInput=True)
			while createDir not in ["yes", "no"]:
				createDir = log("Please, type 'yes' or 'no': ", isInput=True)
			if createDir == 'no':
				log("You typed 'no'. Default saves directory will be used:" + self.saveDir + ".\n")
				return
			if not force:
				log("creating directory you provided")
			os.makedirs(saveDir)
		self.saveDir = saveDir
		if not self.saveDir.endswith(os.path.sep):
			self.saveDir = self.saveDir + os.path.sep


	def getFromUrl(self, url):
		""" Downloads a video by url provided with --url arg """
		# Skipping age restriction if any appears
		self.skipR18Restrict(url)

		self.driver.get(url.split('?')[0] + "?language=" + self.lang)

		# Waiting for page loading
		WebDriverWait(self.driver, self.timeOut).until(lambda d: d.find_element(By.CSS_SELECTOR, '#download-options .list-unstyled a'))
		downloadLink = self.driver.find_element(By.CSS_SELECTOR, '#download-options .list-unstyled a')
		author = self.driver.find_element(By.CSS_SELECTOR, '.submitted a.username').get_attribute('innerHTML')
		name = self.driver.find_element(By.CSS_SELECTOR, '.submitted h1').get_attribute('innerHTML')
		date = re.search(r'(?<=on )[\d\-\s\:]+', self.driver.find_element(By.CSS_SELECTOR, '.submitted').get_attribute('innerHTML')).group(0).replace(' ', '_').replace(':', '-')
		# datetime.strptime("2022-06-16 16:02", "%Y-%m-%d %H:%M")
		log("downloading from {} to {}.mp4".format(url, name))
		self.save(author, date, name, requests.get(downloadLink.get_attribute('href')).content)


	def getFromUID(self, UID):
		""" Downloads a video by UID provided with --uid arg """
		log("getting from uid " + UID)
		url = self.commonUrl + UID
		self.getFromUrl(url)


	def getAll(self):
		""" Just downloads all videos up to last saved if any or if --all don't provided """
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


	def dontLookAtLast(self):
		self.lastUID = None


	def setLastUID(self, uid):
		""" Get uid last saved last time (if any) otherwise create a file to save it in future """
		if os.path.isfile('last_uid'):
			with open('last_uid', 'w') as lastUidFile:
				lastUidFile.write(uid)

	def save(self, videoAuthor, videoDate, videoName, videoContent):
		saveDir = self.saveDir
		if self.groupBy == "author":
			self.saveDir += videoAuthor
		elif self.groupBy == "day":
			self.saveDir += videoDate.split('_')[0]
		elif self.groupBy == "FullDate":
			self.saveDir += videoDate.split('_')[0].split('-')[0] + "/" + videoDate.split('_')[0].split('-')[1] + "/" + videoDate.split('_')[0].split('-')[2]
		
		self.changeSaveDir(self.saveDir, force=True)
		name = self.saveDir + videoName + ".mp4"

		if os.path.isfile(name):
			return log("{} file already exist, passed".format(os.path.abspath(name)))
		with open(name, "wb") as video:
			video.write(videoContent)
		log("created file: {}".format(name), "system")
		self.saveDir = saveDir
		

	def help(self):
		""" Show information about this script and its arguments """
		pass


	def __del__(self):
		self.driver.quit()
		os.environ["PATH"] = self.oldPath
		log("downloader closed\n")



def main(args):

	iwara = Iwara()
	if "--saveDir" in sys.argv:
		iwara.changeSaveDir(sys.argv[sys.argv.index('--saveDir')+1])
	if "--save-dir-force" in sys.argv:
		iwara.changeSaveDir(sys.argv[sys.argv.index('--saveDir')+1], True)
	if "--groupBy" in sys.argv:
		groupBy = sys.argv[sys.argv.index('--groupBy')+1].lower()
		iwara.setGrouping(groupBy)
	if "--all" in sys.argv:
		iwara.dontLookAtLast()
	
	if "--url" in sys.argv:
		iwara.getFromUrl(sys.argv[sys.argv.index('--url')+1])
	elif "--uid" in sys.argv:
		iwara.getFromUID(sys.argv[sys.argv.index('--uid')+1])
	else:
		iwara.getAll()

# Start main program
if __name__ == '__main__':
	main(sys.argv)
