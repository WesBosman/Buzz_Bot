#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A class for holding the user's screen name, id and their tweet
class twitter_user():
	screen_name = ""
	user_id     = ""
	tweet       = ""
	tweet_id    = ""
	
	def __init__(self, screen_name, user_id, tweet, tweet_id):
		self.screen_name = screen_name
		self.user_id = user_id
		self.tweet = tweet
		self.tweet_id = tweet_id
	
	def __str__(self):
		name = self.screen_name
		id = self.user_id
		tweet = self.tweet
		tweet_id = self.tweet_id
		str = "%s , %s, %s, %s" %(name, id, tweet, tweet_id)
		return str
		
	