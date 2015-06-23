import hmac
from hashlib import sha256

def generate_sig(endpoint, params, secret):
    sig = endpoint
    for key in sorted(params.keys()):
        sig += '|%s=%s' % (key, params[key])
    return hmac.new(secret, sig, sha256).hexdigest()

endpoint = '/media/657988443280050001_25025320'
params = {
    'access_token': 'fb2e77d.47a0479900504cb3ab4a1f626d174d2d',
    'count': 10,
}
secret = '6dc1787668c64c939929c17683d7cb74'

sig = generate_sig(endpoint, params, secret)
print sig