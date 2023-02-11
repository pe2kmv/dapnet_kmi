import MySQLdb
import configparser
import sys
import os
import time
from datetime import datetime, timedelta
from txmapping import txmap as txmap

#assign configuration file
cfg = configparser.RawConfigParser()
try:
	#attempt to read the config file config.cfg
	config_file = os.path.join(os.path.dirname(__file__),'config.cfg')
	cfg.read(config_file)
except:
	#no luck reading the config file, write error and bail out
	sys.exit(0)

#read settings to access masking database
db_server = cfg.get('database','server')
db_user = cfg.get('database','username')
db_passwd = cfg.get('database','passwd')
db_database = cfg.get('database','database')
db_table = cfg.get('database','tablename')
db_retention = cfg.get('database','retentiontime')

#open database connection
try:
	db = MySQLdb.connect(host=db_server,user=db_user,passwd=db_passwd,db=db_database)
except:
	#can't connect to database, bail out
#	logger.error('No connection to database')
	sys.exit()

# create timestamp
def GetTimeStamp():
	ts = time.time()
	timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return(timestamp)

# add weather warning to DB
def AddWarningMessage(tempcode,tempprovincie,tempmsg):
	temptimestamp = GetTimeStamp()
	sqltext = 'INSERT INTO '+ db_table  +' (`knmi_timestamp`,`knmi_provincie`,`knmi_code`,`knmi_bericht`) VALUES ("' + temptimestamp + '","' + tempprovincie + '","' + tempcode + '","' + tempmsg + '")'
	cur = db.cursor()
	cur.execute(sqltext)
	db.commit()
	cur.close()


def GetMsgList():
	tempprovincie = ','.join(f'"{it}"' for it in list(txmap.keys()))
	sqltext = 'SELECT knmi_provincie,knmi_code, knmi_timestamp FROM '+ db_table +' WHERE knmi_timestamp in (SELECT MAX(knmi_timestamp) FROM '+ db_table +' GROUP BY knmi_provincie)'
	cur = db.cursor()
	cur.execute(sqltext)
	msglist = cur.fetchall()
	cur.close()
	return(msglist)

def DBInit():
	# cursor
	dbcursor = db.cursor()
	checkstring = 'SHOW TABLES LIKE "' + db_table + '"'
	result = dbcursor.execute(checkstring)
	if result == 1:
		dbcursor.close()
		return()
	if result == 0:
		createstring = "CREATE TABLE IF NOT EXISTS " + db_table + " (knmi_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,knmi_timestamp DATETIME NOT NULL, knmi_provincie VARCHAR(25) NOT NULL, knmi_code VARCHAR(10) NOT NULL,knmi_bericht VARCHAR(254) NOT NULL)"
		dbcursor.execute(createstring)
		dbcursor.close()
		return()

def CleanDB():
	curtime = datetime.strptime(GetTimeStamp(), '%Y-%m-%d %H:%M:%S')
	timethreshold = curtime - timedelta(hours=int(db_retention),minutes=0)
	sqltext = 'DELETE FROM ' + db_table + ' WHERE knmi_timestamp < "' + str(timethreshold)+'"'
	try:
		cur = db.cursor()
		cur.execute(sqltext)
		db.commit()
		cur.close()
	except:
		pass
