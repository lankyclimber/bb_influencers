from instagram.client import InstagramAPI

access_token = "1b3b33a0db8c45eebfc80109483f3054"
api = InstagramAPI(access_token=access_token)
recent_media, next_ = api.user_recent_media(user_id="arvnd", count=10)
print len(recent_media)
