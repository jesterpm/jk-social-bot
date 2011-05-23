'''
Created on May 9, 2011

Based on the_shrink.py, by Vivek Halder:
http://blog.vivekhaldar.com/post/2830035130/how-to-write-a-twitter-bot-in-python

Modified by: Karl, Jesse
'''

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

DEFAULT_USERNAME = 'ziggster00' # "this will need to be changed"
DEFAULT_AUTH_FILENAME = '.twitter_oauth'
DEFAULT_LASTID_FILENAME = '.twitter_lastid'
Response_File = 'Response.txt'
public_Status_update_File = 'Status_update.txt'
questions_status_update_File = 'question_status.txt'
make_Friends_File = 'friends.txt'
count = 0 
response_count = 0 

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
            usedoctor = True
            
            if usedoctor:
                doctor_response = doctor.respond(incoming_text.strip())
                outgoing_text = "@%s %s" % (str(asker), doctor_response)
            
            else:
                outgoing_text = '@%s %s' % (str(asker), str(response[response_count]))
                response_count = (response_count + 1) % len(response); 
                
            print '====> Resp = %s' % outgoing_text
            try:
                status_update(outgoing_text)
                
            except TwitterError as e:
                print '*** Twitter returned an error:\n***%s' % e
                
            else:
                lastid = msgid
                print 'Last id replied = ', lastid
                with open(lastid_filename, 'w') as f:
                    f.write(lastid)
                    
        # Sleep for a second
        time.sleep(1)
        
        
def ask_questions():
    # may want to add ask questions to friends too
    # Ask questions specific to followers
    connection = urllib2.urlopen('http://api.twitter.com/1/statuses/followers.json?screen_name=' + username)
    friendship = urllib2.urlopen('http://api.twitter.com/1/statuses/friends.json?screen_name=' + username)
    following_str = connection.read()
    following_obj = json.loads(following_str)        
    friend_str = friendship.read()
    friend_obj = json.loads(friend_str)
    following_list = []
    friend_list = []
    for i in range(len(following_obj)):
        followers = following_obj[i]
        following_list.append(followers[u'screen_name'])
    for x in range(len(friend_obj)):
        supfriend = friend_obj[x]
        friend_list.append(supfriend[u'screen_name'])
    if count == len(question):
            postnumber = 0 
    else: postnumber = count
    
    for follow_me in friend_list:
        if not (follow_me in following_list):
            post = follow_me + ' ' + question[postnumber]     
            #status_update(post) #May want to ask everyone questions regardless of friendship 
            time.sleep(1)
            postnumber = postnumber + 1
        if (follow_me in following_list):#Left open if we want to make specific questions to friends
            print follow_me 
        if postnumber == len(question):
            postnumber = 0
            
            
            
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
    
    "All files need to be the same length as public_Status_update_File"
    with open(public_Status_update_File, 'r') as f:
        tweet = pickle.load(f)
    with open(questions_status_update_File, 'r') as f:
        question = pickle.load(f)
    with open(Response_File, 'r') as f:
        response = pickle.load(f)
    with open(make_Friends_File, 'r') as f:
        friends = pickle.load(f) 
         
    # Prepare Eliza (code from the_shrink.py)
    doctor = eliza.eliza()
    
    # commented out so all friends are not added 
    #for friend in friends: # adds all friends from friends.txt
     #   follow_user(friend)
       
    while True:
        # Reply to tweets directed to us
        reply_to_tweets()
        
        # Send out a generic tweet
        print count 
        status_update(tweet[count]) # post a status update
        count = (count + 1) % len(tweet);
        
        # Sleep for a bit to add some realism.
        print 'Now sleeping... \n'
        time.sleep(1) # set at 5min but is at 2min
        
        # Pose a question
        status_update(question[count])
        
        # Sleep for a bit to add some realism.
        print 'Now sleeping... \n' 
        time.sleep(1) # set for 2min.
        
        ask_questions()     
        
        
   