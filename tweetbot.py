import tweepy,time,sys

print("fishybot is here!")

CONSUMER_KEY = 'HmSpsXAzVRRWTBzlam5rU7dvD'
CONSUMER_SECRET = 'wsR9sIgSzgKuwEbLpUsnrjuytFOWWdnrkUAL9bgujNg5PRiUvv' 
ACCESS_KEY = '822900504862683136-gmfpt0D7VvpKSda0CDpd3UYPObVXqGX'
ACCESS_SECRET = 'VZsgzkPuYgrLPZjcDC1hake9RgIJdycQ0llWf1NOy5avu'

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
user = tweepy.API(auth)

i = 10
while(True):
    user.update_status(str(i) + " minutes have passed! Tweet!")
    i += 1
    time.sleep(60)
    

