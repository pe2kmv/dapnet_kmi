import feedparser
import requests
import configparser
import time
import sys
from datetime import datetime
from txmapping import txmap as txmap
from txmapping import rubricmap as rubricmap
from kmimysql import *
from sendmsg import *
from kmilogger import *

DBInit()

feedurl = 'https://feeds.meteoalarm.org/api/v1/warnings/feeds-belgium'

def GetData():
	try:
		resp = requests.get(feedurl)
		binary = resp.content
		output = json.loads(binary)
		return(output['warnings'])
	except:
		kmi_err.error('kmi2dapnet.py - GetData() - Exit on except')
		sys.exit(0)

# create current timestamp
def GetTimeStamp():
	ts = time.time()
	timestamp = datetime.fromtimestamp(ts).strptime('%Y-%m-%d %H:%M:%S')
	return(timestamp)


def DecodeTimeStamp(TimeStamp):
	UTC_Direction = TimeStamp[-6:-5]
	UTC_Offset = TimeStamp[-5:].split(':')
	UTC_OffsetHours = int(UTC_Direction + UTC_Offset[0])
	UTC_OffsetMinutes = int(UTC_Direction + UTC_Offset[1])
	timestamp = datetime.strptime(TimeStamp[:-6],'%Y-%m-%dT%H:%M:%S') + timedelta(hours = UTC_OffsetHours, minutes = UTC_OffsetMinutes)
	return(timestamp)

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
	try:
		for msg in dbmessages:
			if keyword in msg:
				return(msg[1])
	except:
		main_logger.debug('kmi2dapnet.py - SearchCode - Except reached')
		return()
# main function
try:
	CurrentTime = datetime.now()
	warnings = GetData()
	main_logger.debug('Main routine - start loop warnings')
	for warning in warnings:
		dataset = warning['alert']['info'][2]
		StartTime = DecodeTimeStamp(dataset['effective'])
		EndTime = DecodeTimeStamp(dataset['expires'])
		main_logger.debug('Main routine - check timeframe of warning')
		if CurrentTime >= StartTime and CurrentTime < EndTime:
			main_logger.debug('Main routine - warning within timeframe')
			Area = dataset['area'][0]['areaDesc']
			rubrics = rubricmap[Area].split(',')
			HeadLine = dataset['headline']
			ColourCode = HeadLine.split()[0].upper()
			main_logger.debug('Main routine - check for ColourCode of specific area')
			if ColourCode != SearchCode(Area):
				main_logger.debug('Main routine - ColourCode of area has changed: send rubric')
				for rb in rubrics:
					msg_logger.info(Area + ' - ' + ColourCode + ' - ' + HeadLine + ' - ' + rb)
#					send_rubric(HeadLine,rb)
			AddWarningMessage(ColourCode,Area,HeadLine)
			main_logger.info(Area + ' - ' + ColourCode + ' - ' + HeadLine) 
	CleanDB()
except:
	print('Error in main function')
	sys.exit(0)

