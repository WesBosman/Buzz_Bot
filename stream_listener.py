#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import time
import re
import math
import buzz_bot as bot

# Stream Listener for streaming tweets in real time
class stream_listener(tweepy.StreamListener):
	# Rate limits
	four_twenty_limits = 0
	tcp_ip_limits      = 0
	http_limits        = 0

	# Multiply the limits by the amount of time
	one_minute   	   = 60
	five_seconds       = 5
	two_fifty_milli    = 0.25

	# Max times for rate limits
	MAX_HTTP_TIME      = 320
	MAX_TCP_IP_TIME    = 16
	
	def on_status(self, status):
		tweet 	 = status.text
		user     = status.user
		tweet_id = status.id
		who_id   = user.id	
		who = bot.get_who_to_retweet(tweet)
		
		# If following more than 1500 people then stop
		if len(bot.retweeted_and_following) > 1000:
			self.disconnect
		# Otherwise follow and retweet more users
		else:
			bot.follow_and_retweet(who, who_id, tweet, tweet_id)
	
	def on_error(self, status_code):
		# Successful Connection
		if status_code == 200:
			print(bot.PLUS + " A Successfull Connection has been made. Streaming now.")
		
		# Unauthorized Connection
		# Invalid Auth Credentials or Out Of Sync Timestamp or Too Many Incorrect Passwords
		elif status_code == 401:
			print(bot.ERROR + " Unauthorized Error")
		
		# Forbidden Connection
		# Connecting Account is not able to connect to this end point
		elif status_code == 403:
			print(bot.ERROR + " Forbidden Connection")
			
		# Unknown Connection
		elif status_code == 404:
			print(bot.ERROR + " Unknown Connection. The URL does not exist.")
		
		# Not Acceptable Connection
		# At least one request parameter is invalid
		# The track keyword is too long or too short
		# Invalid bounding box specified
		# Neither the track nor the follow parameter is specified
		# The Follow User ID is invalid
		elif status_code == 406:
			print(bot.ERROR + " Not Acceptable Connection")
		
		# Too Long Connection
		# Parameter List is too long
		# More Track Values are sent than the user is allowed to use
		# More bounding boxes are sent than the user is allowed to use
		# More follow user ID's are sent than the user is allowed to use
		elif status_code == 413:
			print(bot.ERROR + " Too Long Connection")
		
		# Range Unacceptable Connection
		# A count parameter is specified but the user is not allowed to use count param
		# A count parameter is specified that is outside the accepted range of values
		elif status_code == 416:
			print(bot.ERROR + " Range Unacceptable Connection")
		
		# Rate Limiting Connection
		elif status_code == 420:
			# Returning False will disconnect the stream
			# Returning True  will reconnect  the stream
			# Start with a 1 minute wait and double the time after each attempt
			exponential_limit = math.pow(2, self.four_twenty_limits)
			new_time = exponential_limit * self.one_minute
			self.four_twenty_limits += 1
			
			print(bot.ERROR + " We Have Been Rate Limited")
			
			# If the new time is more than or equal to 16 minutes terminate connection
			if new_time >= 960:
				print(bot.PLUS + " Terminating Stream")
				return False
			# Otherwise wait and attempt to reconnect
			else:
				print(bot.PLUS + " Attempting to wait for %s Seconds" % new_time)
				time.sleep(new_time)
				return True
		
		# Service Unavailable
		# A streaming server is unavailable because it is temporarily overloaded
		# Attempt to make another connection keeping in mind rate limiting and DNS caching
		elif status_code == 503:
			new_time = self.five_seconds
			five_seconds = self.five_seconds * 2
			print(bot.ERROR + " Service Unavaliable")
			
			# If the new time is not greater than 320 seconds then try reconnecting
			if new_time >= MAX_HTTP_TIME:
				print(bot.PLUS + " Terminating Stream")
				return False
			else:
				print(bot.PLUS + " Attempting to reconnect in %s Seconds" % new_time)
				time.sleep(new_time)
				return True
		
		else:
			print("[Error] An Unencountered Error Occured With Status Code: %s" %status_code)
			
			
			
			
			
			
			