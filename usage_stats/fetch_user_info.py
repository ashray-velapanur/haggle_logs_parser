import sys, os

sys.path.append(os.path.expanduser('~') + '/Desktop/projects/haggle_server/src')
sys.path.append('/usr/local/google_appengine/')
sys.path.append('/usr/local/google_appengine/lib/yaml/lib/')
sys.path.append('/usr/local/google_appengine/lib/fancy_urllib/')
sys.path.append('/usr/local/google_appengine/lib/webapp2-2.5.2')
sys.path.append('/usr/local/google_appengine/lib/fancy_urllib/')
sys.path.append('/usr/local/google_appengine/lib/webob-1.1.1/')
sys.path.append('/usr/local/google_appengine/lib/django-1.4')

from google.appengine.ext.remote_api import remote_api_stub

def auth_func():
    return ('ashray@b-eagles.com', 'ashray4455')

remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func, 'haggle-prod.appspot.com')

from google.appengine.ext import db

from model.third_party_user_data import ThirdPartyUserData
from model.user import User

user_info_file = open('users_info.csv', 'w')

def get_user_fb_ids():
    user_q = User.all()
    for user in user_q.fetch(1000):
        k = db.Key.from_path('User', user.email, 'ThirdPartyUserData', 'FB')
        q = ThirdPartyUserData.all().filter('__key__ =', k)
        for tpud in q.fetch(1000):
            print user.name.encode('utf-8'), ',', user.email.encode('utf-8'), ',', tpud.id_.encode('utf-8')
            print >> user_info_file, user.name.encode('utf-8'), ',', user.email.encode('utf-8'), ',', tpud.id_.encode('utf-8')

get_user_fb_ids()
