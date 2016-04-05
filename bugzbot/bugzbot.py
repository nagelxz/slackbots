import time, json, yaml, re, os, sys
from datetime import datetime, timedelta
from slackclient import SlackClient
import returnTicket as bugz

def find_channel(channel):
	return sc.server.channels.find(channel)

config = yaml.load(file('bugzbot.conf', 'r'))
 
token = config['SLACK_TOKEN']
sc = SlackClient(token)
 
sc = SlackClient(token)
if not sc.rtm_connect():
	exit("Failed to connect.")

try:
	while True:
	
		messages = sc.rtm_read()
		
		for new_reply in messages:
			print(new_reply)
			
			if 'type' in new_reply:
			
				if new_reply['type'] == 'message' and 'text' in new_reply:
					message = new_reply['text']
					channel = new_reply['channel']
					
					if re.search('!(bugz|bugzid|case|ticket|ticekt) (\d{3,6})', message):
						if re.search('(\d{3,6})', message):
						
							ticket = bugz.returnTicket(re.search('(\d{3,6})', message).group(1), config)
							channel_reply = find_channel(channel)
							
							if channel_reply:
								channel_reply.send_message(ticket)
		time.sleep(1)
		
except KeyboardInterrupt:
	sys.exit(0)