from django.shortcuts import render

import sys
import datetime
import time
import requests
import json

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

consumer_key = 'GvuJG3OcyAofQefYr96Hcz9od'
consumer_secret = '7gx0oksFNoMt2Ul7oAZAW5tWSGmsAYBMhhP7oolqMwF61YLzQx'
access_token = '370005978-f2vUKEv0PIWAUJcHZ27q997MIeumWhM28OTAeV0W'
access_secret = 'thtMjZRM9xc9xOo9ckT4Wqm0ZLLnCyUZDkC33EOQYNh1o'
auth = None
api = None

tweets = []
review = []
confidence = []

positive=[]
negative=[]

satisfaction = None

def index(request):
    return render(request,'index.html')

def results(request):
    global tweets,review,confidence,positive,negative
    tweets = []
    review = []
    confidence = []
    positive = []
    negative = []
    global auth,api
    auth = OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_secret)
    api = tweepy.API(auth)

    ky = 'purplestem'
    dys = 1

    if 'kywrd' in request.GET and request.GET['kywrd']:
        ky = request.GET['kywrd']

    if 'days' in request.GET and request.GET['days']:
        dys = request.GET['days']

    past(ky,dys)
    compute()

    return render(request,'final.html',{'satisfaction':satisfaction,'pos':positive,'neg':negative})

def past(name,d):
	st = time.time()
	d = eval(d)
	u=datetime.date.today()
	for tweet in tweepy.Cursor(api.search,q=name,since=u-datetime.timedelta(d),until=u,lang='en').items():
		s = tweet.text
		tweets.append(s)
		r = requests.post('http://sentiment.vivekn.com/api/text/',{'txt':s})
		js = json.loads(r.text[:])
		review.append(js['result']['sentiment'])
		confidence.append(eval(js['result']['confidence']))
		if time.time()-st>60:
			break

def compute():
    global satisfaction
    pw = 0
    nw = 0
    l = len(tweets)
    for i in range(l):
        if review[i]=='Positive':
            positive.append(tweets[i])
            pw+=(confidence[i]-0.5)
        elif review[i]=='Negative':
            negative.append(tweets[i])
            nw+=(confidence[i]-0.5)
    if pw+nw>0:
        satisfaction=(pw/(pw+nw))*100
