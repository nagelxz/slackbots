import time
import yaml
import sys
from tinydb import TinyDB, where, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from slackclient import SlackClient


class Voting(object):

    def __init__(self):
        self.db = TinyDB('tw_bot.json', storage=CachingMiddleware(JSONStorage))
        #self.db.WRITE_CACHE_SIZE = 3
        self.tw = self.db.table('tenthwave')
        self.votes = Query()

    def process_votes(self, message, channel):
        self.sign = ''

        if message.endswith('++'):
            self.sign = '+'
        elif message.endswith:
            self.sign = '-'

        print "got sign?"

        self.vote = message[:-2].strip()
        self.tally = self.update_votes(self.vote, self.sign, channel)
        return self.tally

    def update_votes(self, message, plusminus, channel):
        self.tw = self.db.table(channel)
        self.exists = self.tw.contains(self.votes['name'] == message)
        print "do i exist?" + str(self.exists)
        self.tally = 0
        self.resp = ''

        if plusminus == '+':
            self.tally = 1
        else:
            self.tally = -1

        print "which sign?" + str(self.tally)

        if not self.exists:
            print "do i reach this?"
            self.tw.insert({'name': message, 'tally': self.tally})
            print self.tw.all()
            if self.tally > 0:
                print "how about here"
                self.resp = message + "++ [woot! now at " + str(self.tally) + "]"
            else:
                print "what about now"
                self.resp = message + "-- [ouch! now at " + str(self.tally) + "]"
        else:
            self.old = self.tw.get(self.votes.name == message)
            self.tw.update({'tally': (self.old['tally'] + self.tally)}, where('name') == message)

            if self.tally > 0:
                self.resp = message + "++ [woot! now at " + str(self.old['tally'] + self.tally) + "]"
            else:
                self.resp = message + "-- [ouch! now at " + str(self.old['tally'] + self.tally) + "]"

        return self.resp


def find_channel(channel):
    return sc.server.channels.find(channel)


config = yaml.load(file('votebot.conf', 'r'))

token = config['SLACK_TOKEN']
sc = SlackClient(token)

sc = SlackClient(token)
if not sc.rtm_connect():
    exit("Failed to connect.")

vote = Voting()

try:
    while True:

        messages = sc.rtm_read()

        for new_reply in messages:
            print(new_reply)

            if 'type' in new_reply:

                if new_reply['type'] == 'message' and 'text' in new_reply:
                    message = new_reply['text']
                    #user = new_reply['user']
                    channel = new_reply['channel']

                    if message.endswith('++') or message.endswith('--'):
                        channel_reply = find_channel(channel)
                        if channel_reply:
                            resp = vote.process_votes(message, channel)
                            channel_reply.send_message(resp)

        time.sleep(0.1)
except KeyboardInterrupt:
    sys.exit(0)
