import time, json, yaml, re, os, sys
from datetime import datetime, timedelta
from slackclient import SlackClient
import returnTicket as bugz

def find_channel(channel):
	return sc.server.channels.find(channel)
	
def find_user(user):
	return sc.server.users.find(user)

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
			
			if 'type' in new_reply:
				
				if new_reply['type'] == 'message' and 'text' in new_reply:
					message = new_reply['text']
					orig_user = new_reply['user']
					channel = new_reply['channel']
					
					if len(re.findall(r'!((bugz|bugzid|case|ticket|ticekt) ?(?:-short|-sendto)? ?(?:-short|-sendto)? ?(?:<@\w.*?>)? (\d{4,6}))', message)) > 0:
						cases = re.findall(r'!((bugz|bugzid|case|ticket|ticekt) ?(?:-short|-sendto)? ?(?:-short|-sendto)? ?(?:<@\w.*?>)? (\d{4,6}))', message)
						for case in cases:
							
							case_num = case[2]
							options = re.findall(r'(-short|-sendto) ?(-short|-sendto)?', case[0])
							if len(options) == 0:
								ticket = bugz.returnTicket(case_num, None, config)
								channel_reply = find_channel(channel)
								if channel_reply:
									channel_reply.send_message(ticket)
							else:
								if options[0][0] == '-short':
								
									ticket = bugz.returnTicket(case_num, 'short', config)
									if options[0][1] == '-sendto':
										try:
											user = re.search(r'((?<=\<@)\w*)',case[0]).group(0)
											to_user = find_user(user)
											print user
											if to_user:
												
												sc.api_call('chat.postMessage', channel=user, as_user=True, text=ticket)
										except AttributeError:
											sc.api_call('chat.postMessage', channel=orig_user, as_user=True, text="Gosh darnit! You screwed it up again.\n\n Make sure you mention a user so I know where to send this thing.")
											
									else:
									
										channel_reply = find_channel(channel)
										if channel_reply:
									
											channel_reply.send_message(ticket)
										
								elif options[0][0] == '-sendto':
								
									if options[0][1] == '-short':
									
										ticket = bugz.returnTicket(case_num, 'short', config)
										try:
											user = re.search(r'((?<=\<@)\w*)',case[0]).group(0)
											to_user = find_user(user)
											print user
											if to_user:
												
												sc.api_call('chat.postMessage', channel=user, as_user=True, text=ticket)
										except AttributeError:
											sc.api_call('chat.postMessage', channel=orig_user, as_user=True, text="Gosh darnit! You screwed it up again.\n\n Make sure you mention a user so I know where to send this thing.")
											
								
									else:
								
										ticket = bugz.returnTicket(case_num, None, config)
										try:
											user = re.search(r'((?<=\<@)\w*)',case[0]).group(0)
											to_user = find_user(user)
											print user
											if to_user:
												
												sc.api_call('chat.postMessage', channel=user, as_user=True, text=ticket)
										except AttributeError:
											sc.api_call('chat.postMessage', channel=orig_user, as_user=True, text="Gosh darnit! You screwed it up again.\n\n Make sure you mention a user so I know where to send this thing.")
											
								
								
		time.sleep(1)
		
except KeyboardInterrupt:
	sys.exit(0)