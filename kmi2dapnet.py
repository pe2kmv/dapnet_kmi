import feedparser
import requests
import configparser
import time
import sys
from datetime import datetime
from txmapping import txmap as txmap
from txmapping import rubricmap as rubricmap
from knmimysql import *
from sendmsg import *

DBInit()

feedurl = 'https://feeds.meteoalarm.org/api/v1/warnings/feeds-belgium'

def GetData():
	try:
		resp = requests.get(feedurl)
		binary = resp.content
		output = json.loads(binary)
		return(output['warnings'])
	except:
		exit(0)

# create current timestamp
def GetTimeStamp():
	ts = time.time()
	timestamp = datetime.fromtimestamp(ts).strptime('%Y-%m-%d %H:%M:%S')
	return(timestamp)

#print(output['warnings'][1]['alert'].keys())
#print(output['warnings'][1]['alert']['info'])
#print(output['warnings'][0]['alert']['info'][0]['area'][0]['areaDesc'])
#print(output['warnings'][1]['alert']['info'][0]['area'][0]['areaDesc'])
#print(output['warnings'][0]['alert']['info'][0]['parameter'][0])
#print(output['warnings'][0]['alert']['info'][0]['parameter'][1])

def DecodeTimeStamp(TimeStamp):
	UTC_Direction = TimeStamp[-6:-5]
	UTC_Offset = TimeStamp[-5:].split(':')
	UTC_OffsetHours = int(UTC_Direction + UTC_Offset[0])
	UTC_OffsetMinutes = int(UTC_Direction + UTC_Offset[1])
	timestamp = datetime.strptime(TimeStamp[:-6],'%Y-%m-%dT%H:%M:%S') + timedelta(hours = UTC_OffsetHours, minutes = UTC_OffsetMinutes)
	return(timestamp)



#knmifeed = feedparser.parse(feedurl)

dbmessages = GetMsgList()

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# lookup in dictionary
def SearchCode(keyword):
	for msg in dbmessages:
		if keyword in msg:
			return(msg[1])

# main function
try:
	CurrentTime = datetime.now()
	warnings = GetData()
	for warning in warnings:
		dataset = warning['alert']['info'][2]
		StartTime = DecodeTimeStamp(dataset['effective'])
		EndTime = DecodeTimeStamp(dataset['expires'])
		if CurrentTime >= StartTime and CurrentTime < EndTime:
			Area = dataset['area'][0]['areaDesc']
			rubrics = rubricmap[Area].split(',')
			HeadLine = dataset['headline']
			ColourCode = HeadLine.split()[0].upper()
			print(ColourCode + ' - '+ SearchCode(Area))
			if ColourCode != SearchCode(Area):
				for rb in rubrics:
					send_rubric(HeadLine,rb)
					print(rb)
			AddWarningMessage(ColourCode,Area,HeadLine)
	CleanDB()
except:
	print('Error in main function')
	sys.exit(0)

