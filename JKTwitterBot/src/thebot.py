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

DEFAULT_USERNAME = 'ziggster00'
DEFAULT_AUTH_FILENAME = '.twitter_oauth'
DEFAULT_LASTID_FILENAME = '.twitter_lastid'
Response_File = 'Response.txt'
public_Status_update_File = 'Status_update.txt'
questions_status_update_File = 'question_status.txt'

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

    poster = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=True,
        api_version='1',
        domain='api.twitter.com')
   
    def status_update(outgoing_text):  
        print '====> Resp =', outgoing_text
        try:
            poster.statuses.update(status=outgoing_text)
        except TwitterError as e:
            print '*** Twitter returned an error:\n***%s' % e
    thestring = ['hello?', 'good bye']
    
    "All files need to be the same length as public_Status_update_File"
    with open(public_Status_update_File, 'r') as f:
        tweet = pickle.load(f)
    with open(questions_status_update_File, 'r') as f:
        question = pickle.load(f)
    while True:
        for line in range(len(tweet)):    
            status_update(tweet[line]) # post a status update 
            print tweet[line]
            print 'Now sleeping... \n'
            time.sleep(120) # set at 5min but is at 2min
            print question[line] 
            status_update(question[line])
            print 'Now sleeping... \n' 
            time.sleep(120) # set for 2min.
            
            