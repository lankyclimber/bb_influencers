from instagram.client import InstagramAPI
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'local':
    try:
        from test_settings import *

        InstagramAPI.host = test_host
        InstagramAPI.base_path = test_base_path
        InstagramAPI.access_token_field = "access_token"
        InstagramAPI.authorize_url = test_authorize_url
        InstagramAPI.access_token_url = test_access_token_url
        InstagramAPI.protocol = test_protocol
    except Exception:
        pass

# Fix Python 2.x.
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass

#client_id = input("Client ID: ").strip()
#client_secret = input("Client Secret: ").strip()
#redirect_uri = input("Redirect URI: ").strip()
#raw_scope = input("Requested scope (separated by spaces, blank for just basic read): ").strip()
raw_scope="basic"
scope = raw_scope.split(' ')
# For basic, API seems to need to be set explicitly
if not scope or scope == [""]:
    scope = ["basic"]
client_id="a8e82948f0474c9ea1e0092d89abb365"
client_secret="fe6d681592664311ab5ef24d19c984a7"
redirect_uri="http://www.backbonemedia.net"


api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
redirect_uri = api.get_authorize_login_url(scope = scope)

print ("Visit this page and authorize access in your browser: "+ redirect_uri)

code = (str(input("Paste in code in query string after redirect: ").strip()))

access_token = api.exchange_code_for_access_token(code)
print (access_token)
print ("access token: " )
print (access_token)

api = InstagramAPI(access_token=access_token)
#import ipdb; ipdb.set_trace()
recent_media, next_ = api.user_recent_media(user_id="2118157933", count=10)
print(len(recent_media))

