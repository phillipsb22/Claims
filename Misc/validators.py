import json
from httplib2 import Http

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def validate_token(access_token):
    h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+access_token)

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        data = json.loads(cont.decode())

    if int(data['expires_in']) <= 0:
        return None

    return data['email']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
