import ushlex as shlex
import time
import yaml
import re
import sys
from slackclient import SlackClient
from fogbugz import FogBugz


class Bugz(object):

    def __init__(self):
        config = yaml.load(file('bugzbot.conf', 'r'))
        self.fb = FogBugz(config['FOGBUGZ_URL'], config['FOGBUGZ_TOKEN'])

    def returnUser(self, _semail):
        user = self.fb.viewPerson(semail=_semail)

        try:
            fb_user = [user.people.person.sfullname.string, user.people.person.ixperson.string]
            name = user.people.person.sfullname.string
            return fb_user
        except AttributeError:
            return "User not found"

    def assignTicket(self, ticket_num, user, orig_user, ):

        touser = self.returnUser(user[2])
        fromuser = self.returnUser(orig_user[2])

        if touser and fromuser != "User not found":
            event = "This ticket was assigned to you by slack user " + orig_user[1] + " courtesy of bugzbot!"
            #fb.edit(ixBug=ticket_num, sPersonAssignedTo=touser, sEvent=event)

    def returnTicket(self, option, ticket_num):
        if option:

            retrieve_ticket = self.fb.search(q=ticket_num, cols='ixBug,sTitle,sProject')

            if retrieve_ticket.cases['count'] == str(1):

                ticket_title = retrieve_ticket.cases.case.stitle.string
                ticket_project = retrieve_ticket.cases.case.sproject.string
                ticket_URL = "https://tenthwave.fogbugz.com/f/cases/" + ticket_num

                ticket = "Ticket: " + ticket_num + "  |  " + ticket_title + "\n\n" + ticket_URL
                print ticket
                return ticket
            else:
                msg = "Something went wrong! Either Fogbugz is down, you're a magician calling a number " \
                    "that does not exist yet, or it somehow returned more than one ticket."
                print msg
                return msg
        else:
            retrieve_ticket = self.fb.search(
                q=ticket_num,
                cols="ixBug,sTitle,sLatestTextSummary,sArea,sProject"
            )

            if retrieve_ticket.cases['count'] == str(1):

                ticket_title = retrieve_ticket.cases.case.stitle.string
                ticket_area = retrieve_ticket.cases.case.sarea.string
                ticket_project = retrieve_ticket.cases.case.sproject.string
                ticket_URL = "https://tenthwave.fogbugz.com/f/cases/" + ticket_num
                ticket_last_update = retrieve_ticket.cases.case.slatesttextsummary.string

                ticket = ticket_URL + "\n\nTicket: " + ticket_num + "\n" + ticket_project + " : " + \
                    ticket_area + "\n*" + ticket_title + "*\n\n" + ticket_last_update
                print ticket
                return ticket
            else:
                msg = "Something went wrong! Either Fogbugz is down, you're a magician calling a number " \
                    "that does not exist yet, or it somehow returned more than one ticket."
                print msg
                return msg


class MessageProcessor(object):

    def __init__(self):
        self.split_message = []
        self.touser = None

    def processMessage(self, message, ticket_num, orig_user, channel):
        self.split_message = shlex.split(message)
        self.options = self.processOptions(self.split_message)

        print self.split_message
        print self.options
        print ticket_num

        if self.options[1] or self.options[2]:
            for msg in self.split_message:
                if re.match(r'(?:<@\w.*?>)', msg):
                    self.touser = re.search(r'((?<=\<@)\w*)', msg).group(0)
                    print self.touser
        #if self.options[2]: #assignto
            #do later

        if self.options[1]:  # sendto

            if self.options[0]:  # sendto short
                self.ticket = Bugz().returnTicket(True, ticket_num)
            else:
                self.ticket = Bugz().returnTicket(False, ticket_num)

            try:
                fromuser = find_user(orig_user)

                if self.ticket.startswith("Something"):
                    sc.client.api_call('chat.postMessage', channel=from_user[0], as_user=True, text=self.ticket)
                else:
                    self.msg = "This ticket was sent to you by:  " + fromuser[1] + "\n\n" + self.ticket
                    sc.client.api_call('chat.postMessage', channel=self.touser, as_user=True, text=self.msg)

            except AttributeError:
                msg = "Gosh darnit! You screwed it up again.\n\n Make sure you mention a user so I know " \
                    "where to send this thing."
                sc.api_call(
                    'chat.postMessage',
                    channel=channel,
                    as_user=True,
                    text=msg
                )

        elif self.options[0]:  # short
            self.ticket = Bugz().returnTicket(True, ticket_num)
            channel_reply = find_channel(channel)

            if channel_reply:
                channel_reply.send_message(self.ticket)

        else:  # regular
            self.ticket = Bugz().returnTicket(False, ticket_num)
            channel_reply = find_channel(channel)

            if channel_reply:
                channel_reply.send_message(self.ticket)

    def processOptions(self, message):

        self._short = False
        self._sendto = False
        self._assignto = False

        for msg in message:

            if re.match(r'(-short)', msg):
                self._short = True
            elif re.match(r'(-sendto)', msg):
                self._sendto = True
            elif re.match(r'(-assignto)', msg):
                self._assignto = True

        return [self._short, self._sendto, self._assignto]


class Slack(object):

    def __init__(self):
        self.config = yaml.load(file('bugzbot.conf', 'r'))

    def start(self):
        self.client = SlackClient(self.config['SLACK_TOKEN'])

        if not self.client.rtm_connect():
            exit('failed to connect')

        return self.client


def find_channel(channel):
    return sc.client.server.channels.find(channel)


def find_user(users):
    user = sc.client.api_call('users.info', user=users)
    return [user['user']['id'], user['user']['real_name'], user['user']['profile']['email']]

sc = Slack()
sc.start()

try:
    while True:

        messages = sc.client.rtm_read()
        for new_reply in messages:

            if 'type' in new_reply:

                if new_reply['type'] == 'message' and 'text' in new_reply:
                    message = new_reply['text']
                    orig_user = new_reply['user']
                    channel = new_reply['channel']

                    if len(re.findall(r'!((bugz|bugzid|case|ticket|ticekt).*?(\d{4,6}))', message)) > 0:
                        tickets = re.findall(r'!((bugz|bugzid|case|ticket|ticekt).*?(\d{4,6}))', message)
                        for ticket in tickets:

                            ticket_num = ticket[2]

                            msg = MessageProcessor()
                            msg.processMessage(message, ticket_num, orig_user, channel)

        time.sleep(0.25)

except KeyboardInterrupt:
    sys.exit(0)
