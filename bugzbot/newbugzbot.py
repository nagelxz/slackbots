# -*- coding: utf-8 -*-

import ushlex as shlex
import time
import yaml
import re
import sys
from slackclient import SlackClient
from fogbugz import FogBugz


class Bugz(object):

    def __init__(self):
        self.config = yaml.load(file('bugzbot.conf', 'r'))
        self.fb = FogBugz(self.config['FOGBUGZ_URL'],
            self.config['FOGBUGZ_TOKEN'])

    def returnUser(self, _semail):
        self.user = self.fb.viewPerson(semail=_semail)
        try:
            self.fb_user = self.user.people.person.sfullname.string
            return self.fb_user
        except AttributeError:
            return "User not found"

    def assignTicket(self, ticket_num, user, orig_user):
        self.touser = self.returnUser(user)
        print user
        print self.touser
        if self.touser != "User not found":
            self.event = "This ticket was assigned to you by slack user " + \
                orig_user[1] + " courtesy of bugzbot!"
            self.fb.edit(ixBug=ticket_num,
                sPersonAssignedTo=self.touser,
                sEvent=self.event)

            self.checker = self.fb.search(q=ticket_num, cols="ixPersonAssignedTo")
            print self.checker

            if self.checker.cases.case.ixpersonassignedto.string != "93":
                return "success"
            else:
                return "One of us screwed up. I got stuck with the ticket somehow." \
                    "Please follow up and manually assign the ticket so it does not get lost in the shuffle!"
        else:
            return "Fogbugz user was not found. Please try again."

    def returnTicket(self, option, ticket_num):
        if option:
            self.retrieve_ticket = self.fb.search(q=ticket_num,
                cols='ixBug,sTitle,sProject')

            if self.retrieve_ticket.cases['count'] == str(1):

                self.ticket_title = self.retrieve_ticket.cases.case.stitle.string
                self.ticket_project = self.retrieve_ticket.cases.case.sproject.string
                self.ticket_URL = "https://tenthwave.fogbugz.com/f/cases/" + ticket_num

                self.ticket = "Ticket: " + ticket_num + "  |  " + self.ticket_title + \
                    "\n\n" + self.ticket_URL
                print self.ticket
                return self.ticket
            else:
                msg = "Something went wrong! Either Fogbugz is down, you're a magician calling a number " \
                    "that does not exist yet, or it somehow returned more than one ticket."
                print msg
                return msg
        else:
            self.retrieve_ticket = self.fb.search(
                q=ticket_num,
                cols="ixBug,sTitle,sLatestTextSummary,sArea,sProject")

            if self.retrieve_ticket.cases['count'] == str(1):

                self.ticket_title = self.retrieve_ticket.cases.case.stitle.string
                self.ticket_area = self.retrieve_ticket.cases.case.sarea.string
                self.ticket_project = self.retrieve_ticket.cases.case.sproject.string
                self.ticket_URL = "https://tenthwave.fogbugz.com/f/cases/" + ticket_num
                self.ticket_last_update = self.retrieve_ticket.cases.case.slatesttextsummary.string.encode('utf-8')

                self.ticket = self.ticket_URL + "\n\nTicket: " + ticket_num + "\n" + self.ticket_project + \
                    " : " + self.ticket_area + "\n*" + self.ticket_title + "*\n\n" + self.ticket_last_update
                print self.ticket.encode('utf-8')
                return self.ticket.encode('utf-8')
            else:
                msg = "Something went wrong! Either Fogbugz is down, you're a magician calling a number " \
                    "that does not exist yet, or it somehow returned more than one ticket."
                print msg
                return msg


class MessageProcessor(object):

    def __init__(self):
        self.split_message = []
        self.touser = None

    def processMessage(self, message, ticket_num, orig_user, _channel):
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

        if self.options[2]:  # assignto
            #  this is going to be fun...
            if not self.options[3]:
                self.touser_email = sc.find_user(self.touser)[2]
                self._orig_user = sc.find_user(orig_user)
                self.ticket = Bugz().assignTicket(ticket_num, self.touser_email, self._orig_user)

                if self.ticket == "User not Found":
                    sc.client.api_call('chat.postMessage', channel=_channel,
                        as_user=True, text="Something went wrong and the ticket could not be assigned" +
                            " to that user for some reason, make sure it did not get stuck in the API user's list.")
                else:
                    self.fromuser_name = sc.find_user(orig_user)[1]

                    sc.client.api_call('chat.postMessage', channel=self.touser,
                        as_user=True, text="Slack user " + self.fromuser_name + " assigned you a ticket on Fogbugz!")
                    sc.client.api_call('chat.postMessage', channel=_channel,
                        as_user=True, text="The ticket you requested has been sent to the Slack user on Fogbugz.")

        if self.options[1]:  # sendto

            if self.options[0]:  # sendto short
                self.ticket = Bugz().returnTicket(True, ticket_num)
            else:
                self.ticket = Bugz().returnTicket(False, ticket_num)

            try:
                self.fromuser = sc.find_user(orig_user)

                if self.ticket.startswith("Something"):
                    sc.client.api_call('chat.postMessage', channel=self.from_user[0],
                        as_user=True, text=self.ticket)
                else:
                    self.msg = "This ticket was sent to you by:  " + self.fromuser[1] + "\n\n" + self.ticket
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
            channel_reply = sc.find_channel(channel)

            if channel_reply:
                channel_reply.send_message(self.ticket)

        else:  # regular
            self.ticket = Bugz().returnTicket(False, ticket_num)
            channel_reply = sc.find_channel(channel)

            if channel_reply:
                channel_reply.send_message(self.ticket)

    def processOptions(self, message):

        self._short = False
        self._sendto = False
        self._assignto = False
        self._fullname = False

        for msg in message:

            if re.match(ur'(—short$|-s$)', msg, re.UNICODE):
                self._short = True
            elif re.match(ur'(—sendto$|-to$|—notify)', msg, re.UNICODE):
                self._sendto = True
            elif re.match(ur'(—assign)', msg, re.UNICODE):
                self._assignto = True
            elif re.match(ur'(—fullname$)', msg, re.UNICODE):
                self._name = True

        return [self._short, self._sendto, self._assignto, self._fullname]


class Slack(object):

    def __init__(self):
        self.config = yaml.load(file('bugzbot.conf', 'r'))

    def start(self):
        self.client = SlackClient(self.config['SLACK_TOKEN'])

        if not self.client.rtm_connect():
            exit('failed to connect')

        return self.client

    def find_channel(self, channel):
        return sc.client.server.channels.find(channel)

    def find_user(self, users):
        user = sc.client.api_call('users.info', user=users)
        return [user['user']['id'], user['user']['real_name'], user['user']['profile']['email']]

sc = Slack()
sc.start()

try:
    while True:

        messages = sc.client.rtm_read()
        for new_reply in messages:

            if 'type' in new_reply:
                print new_reply

                if new_reply['type'] == 'message' and 'text' in new_reply:
                    try:
                        message = new_reply['text']
                        orig_user = new_reply['user']
                        channel = new_reply['channel']

                        if len(re.findall(r'!((bugz|case|ticket|ticekt).*?(\d{4,6}))', message)) > 0:
                            tickets = re.findall(r'!((bugz|case|ticket|ticekt).*?(\d{4,6}))', message)
                            for ticket in tickets:
                                print ticket
                                ticket_num = ticket[2]
                                msg = MessageProcessor()
                                msg.processMessage(message, ticket_num, orig_user, channel)
                    except KeyError:
                        msg = "Crap! Something broke! someone didn't exist or a ghost tried to use me I think." \
                            "Please let @nagel know this message came up"
                        sc.api_call(
                            'chat.postMessage',
                            channel=new_reply['channel'],
                            as_user=True,
                            text=msg)

        time.sleep(0.25)

except KeyboardInterrupt:
    sys.exit(0)
