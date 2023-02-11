import configparser
import requests
import json
import sys
import os

# set variables
#assign configuration file
cfg = configparser.RawConfigParser()
try:
        #attempt to read the config file config.cfg
	config_file = os.path.join(os.path.dirname(__file__),'config.cfg')
	cfg.read(config_file)
	dapnet_user = cfg.get('user','username')
	dapnet_pw = cfg.get('user','password')
	dapnet_uri = cfg.get('dapnet','baseurl')+cfg.get('dapnet','coreurl')
	dapnet_rubric = cfg.get('dapnet','baseurl')+cfg.get('dapnet','newsurl')

except:
	#no luck reading the config file, write error and bail out
	sys.exit(0)


def send_page(msg_ric,func,trx,emr,msgtxt):
	req = requests.post(dapnet_uri,auth=(dapnet_user,dapnet_pw),json={'text':msgtxt,'callSignNames':[msg_ric],'transmitterGroupNames':trx,'emergency':emr})

def send_rubric(msgtxt,rbname):
	print('start sending')
	if len(msgtxt) > 80:
		print('length cut')
		msgtxt = msgtxt[0:77] + '...'
	print('start http')
	req = requests.post(dapnet_rubric,auth=(dapnet_user,dapnet_pw),json={'text':msgtxt,'rubricName':rbname,'number':1})
	print(req)
