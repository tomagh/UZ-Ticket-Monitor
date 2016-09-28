# -*- coding: utf-8 -*-

# search parameters!
departure_date = "13.10.2016"

station_from = "Київ"
station_id_from = "2200001"

station_till = "Івано-Франківськ"
station_id_till = "2218200"

# Known stations IDs:
#
# Київ: 2200001
# Івано-Франківськ: 2218200

# other parameters
successURLToOpen = "http://booking.uz.gov.ua" # URL that will be opened in browser on success
requestDelayTime = 30 #seconds between requests
direction = "" + station_from + " -> " + station_till + " (" + departure_date + "): "

import webbrowser, datetime
import urllib, urllib2, requests
import time, sys, os

GVToken = ""
gv_sessid = ""
success = 0

while success == 0:
	searchURL = "http://booking.uz.gov.ua/purchase/search/"
	data = {"station_id_from": station_id_from,
			"station_id_till": station_id_till,
			"station_from": station_from,
			"station_till":	station_till,
			"date_dep":	departure_date,
			"time_dep":	"00:00",
			"time_dep_till": "",
			"another_ec": "0",
			"search": ""}
	encodedData = urllib.urlencode(data)

	try:
		if (GVToken == "" or gv_sessid == ""):
			print "Requesting new GV-Token..."

			encodingMap = {"$$_.___+": "0",
						   "$$_.__$+": "1",
						   "$$_._$_+": "2",
						   "$$_._$$+": "3",
						   "$$_.$__+": "4",
						   "$$_.$_$+": "5",
						   "$$_.$$_+": "6",
						   "$$_.$$$+": "7",
						   "$$_.$___+": "8",
						   "$$_.$__$+": "9",
						   "$$_.$_$_+": "a",
						   "$$_.$_$$+": "b",
						   "$$_.$$__+": "c",
						   "$$_.$$_$+": "d",
						   "$$_.$$$_+": "e",
						   "$$_.$$$$+": "f"}

			# response = urllib2.urlopen('http://booking.uz.gov.ua')
			session = requests.Session()
			response = session.get('http://booking.uz.gov.ua', stream=True)
			
			session.cookies.get_dict()
			gv_sessid = session.cookies.get_dict().get("_gv_sessid")
			
			startStr = "$$_.$__+$$_.___+\"\\\\\\\"\"+";
			endStr = "\"\\\\\\\");\"";
			rangeStart = response.content.find(startStr)
			rangeEnd = response.content.find(endStr)

			if (rangeStart > 0 and rangeEnd > 0):
				encodedToken = response.content[rangeStart + len(startStr): rangeEnd]
				for key in encodingMap:
					encodedToken = encodedToken.replace(key, encodingMap[key])

				GVToken = encodedToken

			else:
				"Pring range not found!"
				break

			print "GV-Token = " + GVToken + "; sessionId = " + gv_sessid
			continue

		else:
			headers = {"Host": "booking.uz.gov.ua",
					   "Accept": "*/*",
					   "GV-Token": GVToken,
					   "Accept-Language": "en-us",
					   "Accept-Encoding": "gzip, deflate",
					   "GV-Ajax": "1",
					   "Content-Type": "application/x-www-form-urlencoded",
					   "Origin": "http://booking.uz.gov.ua",
					   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
					   "Referer": "http://booking.uz.gov.ua/",
					   "GV-Screen": "1440x900",
					   "GV-Referer": "http://booking.uz.gov.ua/",
					   "Content-Length":	str(len(encodedData)),
					   "Cookie": "__utma=31515437.824785525.1400615457.1475030279.1475033734.49; __utmb=31515437.1.10.1475033734; __utmc=31515437; __utmt=1; __utmz=31515437.1429630767.11.4.utmcsr=uz.gov.ua|utmccn=(referral)|utmcmd=referral|utmcct=/passengers/timetables/; HTTPSERVERID=server2; _uz_cart_personal_email=test%40gmail.com; _gv_lang=uk; _gv_sessid=" + gv_sessid,
					   "Connection": "keep-alive"}

			response = requests.post(searchURL, encodedData, headers = headers, timeout=5)
			if response.json()["error"]:
				print "" + time.strftime("%H:%M:%S", time.localtime()) + "> " + direction + response.json()["value"].encode('utf-8') + "; response code = " + str(response.status_code);
			else:
				print "Ticket found! Open prowser and exit!"
				success = 1
				break

		time.sleep(requestDelayTime)

	except urllib2.HTTPError as e:
		print "Unexpected error!"
		print "HTTP response error: " + str(e.code)
		if GVToken == "" or gv_sessid == "":
			break
		else:
			GVToken = ""
			gv_sessid = ""

	except Exception as e:
		print e
		break

if success:
	webbrowser.open_new(successURLToOpen)
