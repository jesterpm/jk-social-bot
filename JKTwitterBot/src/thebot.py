'''
Created on May 9, 2011

Based on the_shrink.py, by Vivek Halder:
using a cheezy little Eliza knock-off by Joe Strout <joe@strout.net>
http://blog.vivekhaldar.com/post/2830035130/how-to-write-a-twitter-bot-in-python

Modified by: Karl, Jesse
'''

from datetime import datetime
import random
from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, read_token_file
from optparse import OptionParser
import pickle
import os
import time
import json
import urllib2
import eliza

CONSUMER_KEY='uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET='MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

# Setting this to true causes tweets to be printed to the screen
# instead of tweeted.
TEST_MODE = True

DEFAULT_USERNAME = 'morejennifer' 
DEFAULT_AUTH_FILENAME = '.twitter_oauth'
DEFAULT_LASTID_FILENAME = '.twitter_lastid'
Response_File = 'Response.txt'
public_Status_update_File = 'Status_update.txt'
questions_status_update_File = 'question_status.txt'
make_Friends_File = 'friends.txt'
count = 33 
response_count = 0 
question_count = 32
lastid = ''

def status_update(outgoing_text):  
    if not TEST_MODE:
        print '====> Resp =', outgoing_text
        try:
            poster.statuses.update(status=outgoing_text)
        except TwitterError as e:
            print '*** Twitter returned an error:\n***%s' % e
            
    else:
        print '====> (TEST MODE) Resp =', outgoing_text
           
def follow_user(user): 
    if not TEST_MODE:
        try:
            poster.friendships.create(id=user) 
        except TwitterError as e:
            print e
            poster.friendships.destroy(id=user)
            poster.friendships.create(id=user)
    
    else:
        print '====> (TEST MODE) Following =', user 
     
def reply_to_tweets():
    global lastid
    global response_count
    results = reader.search(q=username, since_id=lastid)['results']
    for result in reversed(results):
        asker = result['from_user']
        msgid = str(result['id'])
        incoming_text = result['text']
        
        print " <<< " + asker + ": " + incoming_text
        
        if incoming_text.lower().find(username) != 0:
            print '====> No response (not directed to %s)' % (username,)
        elif (lastid != '') and (long(msgid) <= long(lastid)):
            print '====> No response (%s < %s)' % (msgid, lastid)
        else:
            # Found a tweet directed to us.
            # Should we use Eliza? 
            usedoctor = random.random() > 0.33
            
            if usedoctor:
                doctor_response = doctor.respond(incoming_text.strip())
                outgoing_text = "@%s %s" % (str(asker), doctor_response)
            
            else:
                outgoing_text = '@%s %s' % (str(asker), str(response[response_count]))
                response_count = (response_count + 1) % len(response); 
                
            print '====> Resp = %s' % outgoing_text
            try:
                #print outgoing_text
                status_update(outgoing_text)
                
            except TwitterError as e:
                print '*** Twitter returned an error:\n***%s' % e
                
            else:
                lastid = msgid
                print 'Last id replied = ', lastid
                with open(lastid_filename, 'w') as f:
                    f.write(lastid)
                    
        # Sleep for a second
        oursleep(30)
        

def pose_question(question):
    # may want to add ask questions to friends too
    # Ask questions specific to followers
    following = urllib2.urlopen('http://api.twitter.com/1/statuses/friends.json?screen_name=' + username)
    friend_str = following.read()
    friend_obj = json.loads(friend_str)
    friend_list = []
    for x in range(len(friend_obj)):
        supfriend = friend_obj[x]
        friend_list.append(supfriend[u'screen_name'])
    
    victim = random.choice(friend_list)

    tweet = '@%s %s' % (victim, question)

    status_update(tweet)

            
def oursleep(amt):
    if TEST_MODE:
        time.sleep(5)

    else:
        time.sleep(amt)
            
def follow_more():
    if len(friends) > 0:
        for i in range(100):
            if len(friends) > 0:
                follow_user(friends.pop())


#########################
# Execution starts here #
#########################
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-u', '--username', dest='username')
    parser.add_option('-o', '--oauthfile', dest='oauthfile')
    parser.add_option('-l', '--lastid', dest='lastid')
    (options, args) = parser.parse_args()
    
    home_dir = os.environ.get('HOME', '')
    
    if options.username:
        username = options.username
    else:
        username = DEFAULT_USERNAME

    if username[0] != '@':
        username = '@' + username
    
    if options.oauthfile:
        oauth_filename = options.oauthfile
    else:
        oauth_filename = home_dir + os.sep + DEFAULT_AUTH_FILENAME
    oauth_token, oauth_token_secret = read_token_file(oauth_filename)
    
    if options.lastid:
        lastid = options.lastid
    else:
        lastid_filename = home_dir + os.sep + DEFAULT_LASTID_FILENAME
        try:
            with open(lastid_filename, 'r') as f:
                lastid = f.readline()
        except IOError:
            lastid = ''
            
    reader = Twitter(domain='search.twitter.com')
    reader.uriparts=()
    
    poster = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=True,
        api_version='1',
        domain='api.twitter.com')
    
    # Open files of tweets and friends
    with open(public_Status_update_File, 'rb') as f:
        tweet = pickle.load(f)
    with open(questions_status_update_File, 'rb') as f:
        question = pickle.load(f)
    with open(Response_File, 'rb') as f:
        response = pickle.load(f)
    with open(make_Friends_File, 'rb') as f:
        friends = pickle.load(f) 
         
    # Prepare Eliza (code from the_shrink.py)
    doctor = eliza.eliza()

    while True:
        # We sleep between midnight at 6 am.
        hour = datetime.now().hour
        if hour < 6:
            # Sleep until 6 am.
            oursleep((6 - hour) * 3600)
        
        # Follow 100 more users
        follow_more()
    
        # Reply to tweets directed to us
        reply_to_tweets()
        
        # Send out a generic tweet
        print count 
        status_update(tweet[count]) # post a status update
        count = (count + 1) % len(tweet);
        
        # Sleep for a bit to add some realism.
        print 'Now sleeping... \n'
        oursleep(5 * 60)
        
        # Pose a question
        try:
            pose_question(question[question_count])
        except urllib2.HTTPError as e:
            print '*** Twitter returned an error:\n***%s' % e
        question_count = (question_count + 1) % len(question);

        # Sleep for a bit to add some realism.
        print 'Now sleeping... \n' 
        oursleep(25*60)
        
