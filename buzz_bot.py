#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Could use Natural Language Processing with Python
# NLTK
# Could Search #Contests and search the posts for keywords like follow and retweet and win
# May build bot that not only enters contests but follows people and posts tweets

# For OAuth
# Can only make 180 requests in 15 minutes
# 18,000 Tweets in 15 minutes

# For App Only Auth 
# Can make 450 requests in a second
# 45,000 Tweets in 15 minutes

import nltk
import tweepy
import time
import re
import sys
import random
import simplejson as json
import stream_listener
from twitter_user import *
from termcolor import colored
from credentials import *

# Plus and Minus Text
PLUS  = colored('[+]', 'green')
MINUS = colored('[-]', 'red')
ERROR = colored('[Error]', 'red')
EXCLAM = colored('[!]', 'red')

# Set Up The API
print( PLUS + " Setting Up The Twitter API")
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Attempt to use app only auth versus OAuth
#auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True) 

# Global Constants
retweeted_and_following = [twitter_user]
bot_name 	 	 = api.me().screen_name
contest_handle   = "RT and Follow to enter"
what_to_track = [ 
				"Retweet and Follow to Enter", 	
				"RT & Follow to Enter", 
				"RT and Follow to Enter",
				"Follow/RT to enter",
				"RT/Follow to enter",
				"Follow & Retweet to Enter", 
				"Follow & RT to Enter",
				"Follow and Retweet to Enter"]


def main():
	# Check to see who I am following in order to not retweet same thing twice
	#get_all_tweets(bot_name)
	
	# Check Rate Limit Status
	#get_rate_limit_status()
	
	# Search for Contests
	#search(contest_handle)
	
	# Create Stream and Search for Contests
	try:
		create_stream()
	except Error as e:
		print(MINUS + " Error %s" % e.getMessage())
		# Restart The Program if it fails here
		time.sleep(20)
		main()
	
	#print(EXCLAM + " Script Finished")
	

def create_stream():
	print(PLUS + " Creating Stream Listener")
	myStreamListener = stream_listener.stream_listener()
	myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
	myStream.filter(track=what_to_track)
	
# This method was written by yanofsky on Github 
def get_all_tweets(screen_name):
	print(PLUS + " Downloading all %s's tweets" % screen_name)
	# Twitter only allows access to a users most recent 3240 tweets with this method
	# This might be due to rate limiting
	# initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	# make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name, count=200)
	
	# save most recent tweets
	alltweets.extend(new_tweets)
	
	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	
	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		#print(PLUS + " getting tweets before %s" % (oldest))
		
		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		
		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		print(PLUS + " %s tweets downloaded so far" % (len(alltweets)) )
	
	# Loop through all the tweets and store them in our list	
	following = 0
	not_following = 0
	try:
		for my_retweet in alltweets:
			user = my_retweet.user
			tweet = my_retweet.text
			tweet_id = my_retweet.id
			who_id = user.id
			who = get_who_to_retweet(tweet)
			
			# If I am not following someone that I have retweeted then follow them.
			# Rate limits when trying to make api calls in for loops
			# The below code is backwards
			"""
			new_who = who.replace("@", "")
			friendship = api.show_friendship(source_screen_name=screen_name, target_screen_name=new_who)
			print(friendship[1])
			
			if friendship[1].following:
				print(PLUS + " I am following %s" % new_who)
				following += 1
			else:
				print(MINUS + " I am not following %s" % new_who)
				not_following += 1
			
			print(PLUS + " I am following %d people" % following)
			print(MINUS + " I am not following %d people" % not_following)
			"""
			
			# Create a twitter user and add them to the list of people we have followed and retweeted
			twitter_usr = twitter_user(who, who_id, tweet, tweet_id)
			#print(PLUS + " Twitter usr: %s" % twitter_usr)
			retweeted_and_following.append(twitter_usr)
			
	except tweepy.TweepError as e:
		print(ERROR + str(e.message[0]['message']))
		pass
		
		
# Get the person we are supposed to retweet
# This could be expanded with regular expressions
# The RE would match @user_name: or @user_name or user_name 
def get_who_to_retweet(tweet):
	at_pos = tweet.find("@")
	end_pos = tweet.find(":")
	who = tweet[at_pos : end_pos]
	return who
	
		
# Search for a specific set of strings using Twitter's REST API
def search(handle):
	print(PLUS + " Printing Search Results")
	
	for page in tweepy.Cursor(api.search, q=handle, rpp=100, show_user=True).pages(5):
		for t in page:
			user     = t.user
			tweet    = t.text
			tweet_id = t.id
			who_id   = user.id	
			who = get_who_to_retweet(tweet)
			follow_and_retweet(who, who_id, tweet, tweet_id)
			
def get_rate_limit_status():
	rate_status = api.rate_limit_status()
	print(json.dumps(rate_status, indent=4, sort_keys=True))
	#print(json.dumps(rate_status["followers"], indent=4, sort_keys=True))
	#print(json.dumps(rate_status["friends"], indent=4, sort_keys=True))
	#print(json.dumps(rate_status["statuses"], indent=4, sort_keys=True))
	
				
# Follow and Retweet
def follow_and_retweet(who, who_id, tweet, tweet_id):
	# Set an upper and lower limit for the amount of time to wait between API calls
	# This should help prevent being rate limited
	# Currently the lower limit is 1 minute and the upper limit is 3 minutes
	lower_limit = 60 * 0.5
	upper_limit = 60 * 1
	num_seconds = random.randint(lower_limit, upper_limit)
	twitter_usr = twitter_user(who, who_id, tweet, tweet_id)
	
	if who == "":
		print(MINUS + " Unable to find user: %s \n" % who + MINUS + " In tweet: %s" % tweet)
		
	elif twitter_usr not in retweeted_and_following:
		try:
			# If the number of following and retweeting users is more than 1000 then stop
			if len(retweeted_and_following) > 1000:
				print(EXCLAM + " Finished Asynchrously Following users in contest stream")
				sys.exit(1)
						
			# if the tweet contains the word like then like the tweet
			if "like" in tweet or "Like" in tweet:
				api.create_favorite(tweet_id)
				print()
			
			# Create Friendship with user AKA follow them
			api.create_friendship(who)
			api.retweet(tweet_id)
		
			# Add the user to retweeted and following list
			retweeted_and_following.append(twitter_usr)
			print(PLUS + " Following and Retweeting: %s" % who)
			print(PLUS + " Retweet the following:    %s" % tweet)
			print(PLUS + " Now Following %d users" % len(retweeted_and_following))
			
			# Sleep for a random number of seconds between 1 and 3 minutes
			print(PLUS + " Sleeping for %d Seconds" % (num_seconds))
			time.sleep(num_seconds)
			
		except tweepy.TweepError as e:
			print(ERROR + str(e.message[0]['message']))
		# except ProtocolError as proc:
# 			print(ERROR + "Protocol Error")
		
	else:
		print(MINUS + " Already following user:   %s" % who)
	

# Run the Main Program
if __name__ == "__main__":
	main()
