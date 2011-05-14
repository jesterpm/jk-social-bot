'''
Created on May 9, 2011
Modified by: Karl, Jesse
'''

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, read_token_file
from optparse import OptionParser
import pickle
import os
import time
CONSUMER_KEY='uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET='MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

DEFAULT_USERNAME = 'ziggster00' "this will need to be changed"
DEFAULT_AUTH_FILENAME = '.twitter_oauth'
DEFAULT_LASTID_FILENAME = '.twitter_lastid'
Response_File = 'Response.txt'
public_Status_update_File = 'Status_update.txt'
questions_status_update_File = 'question_status.txt'
make_Friends_File = 'friends.txt'
count = 0 
response_count = 0 
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
         
    def status_update(outgoing_text):  
        print '====> Resp =', outgoing_text
        try:
            poster.statuses.update(status=outgoing_text)
        except TwitterError as e:
            print '*** Twitter returned an error:\n***%s' % e     
    def follow_user(user): 
        try:
            poster.friendships.create(id=user) 
        except TwitterError as e:
            print e
            poster.friendships.destroy(id=user)
            poster.friendships.create(id=user)
              
    for friend in friends:
        follow_user(friend)
        
    while True:
        results = reader.search(q=username, since_id=lastid)['results']
        for result in reversed(results):
            if (response_count == len(response)-1):
                response_count = 0
            asker = result['from_user']
            msgid = str(result['id'])
            incoming_text = result['text']
            print " <<< " + asker + ": " + incoming_text
            if incoming_text.lower().find(username) != 0:
                print '====> No response (not directed to %s)' % (username,)
            elif (lastid != '') and (long(msgid) <= long(lastid)):
                print '====> No response (%s < %s)' % (msgid, lastid)
            else:
                outgoing_text = 'RT @' + str(asker)+' '+ str(response[response_count])
                response_count = response_count+1 
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
            time.sleep(30)         
        if (count == len(tweet)-1):
            count = 0
        print count 
        print tweet[count]
        status_update(tweet[count]) # post a status update
        print 'Now sleeping... \n'
        time.sleep(120) # set at 5min but is at 2min
        print question[count] 
        status_update(question[count])
        print 'Now sleeping... \n' 
        time.sleep(120) # set for 2min.
        count = count+1