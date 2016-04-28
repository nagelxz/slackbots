import time
import yaml
import sys
import re
# import ushlex as shlex
from tinydb import TinyDB, where, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from slackclient import SlackClient


class Voting(object):

    def __init__(self):
        self.db = TinyDB('tw_bot.json', storage=CachingMiddleware(JSONStorage))
        self.db.WRITE_CACHE_SIZE = 1
        # self.tw = self.db.table('tenthwave')
        self.votes = Query()

    def closeDB(self):
        self.db.close()

    def process_votes(self, message, channel):
        self.sign = ''

        if message.endswith('++'):
            self.sign = '+'
        elif message.endswith:
            self.sign = '-'

        # print "got sign?"

        self.vote = message[:-2].strip().encode('ascii', 'ignore')
        self.tally = self.update_votes(self.vote, self.sign, channel)
        return self.tally

    def get_scores(self, channel, top_num):
        self.score = self.db.table(channel)
        self.table_dump = self.score.all()
        
        self.table_dump = sorted(self.table_dump, key=lambda v: v['tally'], reverse=True)

        self.scores = "Listing the top " + str(top_num) + " votes: \n\n"

        for vote in self.table_dump:
            self.scores = self.scores + vote['name'].encode('ascii', 'ignore') + \
                " : score  " + str(vote['tally']) + "\n"

        return self.scores

    def update_votes(self, message, plusminus, channel):
        self.tw = self.db.table(channel)
        self.exists = self.tw.contains(self.votes['name'] == message)

        self.tally = 0
        self.resp = ''

        if plusminus == '+':
            self.tally = 1
        else:
            self.tally = -1

        # print "which sign?" + str(self.tally)

        if not self.exists:
            self.tw.insert({'name': message, 'tally': self.tally})
            # print self.tw.all()
            if self.tally > 0:
                # print "how about here"
                self.resp = message + "++ [woot! now at " + str(self.tally) + "]"
            else:
                # print "what about now"
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
            if 'type' in new_reply:

                if new_reply['type'] == 'message' and 'text' in new_reply:
                    message = new_reply['text']
                    # print message
                    # user = new_reply['user']
                    channel = new_reply['channel']

                    if message.endswith('++') or message.endswith('--'):
                        channel_reply = find_channel(channel)
                        if channel_reply:
                            resp = vote.process_votes(message, channel)
                            channel_reply.send_message(resp)
                    elif len(re.findall(r'!(score)', message)) > 0:
                        channel_reply = find_channel(channel)
                        if channel_reply:
                            msg = re.search(r'!((score) top \d)', message).group()
                            # print msg
                            top_num = re.search(r'(\d)', msg).group()
                            resp = vote.get_scores(channel, top_num)
                            channel_reply.send_message(resp)

        time.sleep(0.25)
except KeyboardInterrupt:
    vote.closeDB()
    sys.exit(0)
