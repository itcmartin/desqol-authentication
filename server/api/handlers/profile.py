import datetime
import time
import tornado.gen

from .base import BaseHandler

class AuthHandler(BaseHandler):

    @tornado.gen.coroutine
    def prepare(self):
        super(AuthHandler, self).prepare()

        token = self.request.headers.get('X-Token')
        if token is None:
          self.current_user = None
          self.send_error(400, message='You must provide a token!')
          return

        user = yield self.db.users.find_one({
          'token': token
        }, {
          'username': 1,
          'expires_in': 1
        })

        if user is None:
            self.current_user = None
            self.send_error(403, message='Invalid token!')
            return

        now = time.mktime(datetime.datetime.now().utctimetuple())
        if now > user['expires_in']:
            self.current_user = None
            self.send_error(403, message='Expired token!')
            return

        self.current_user = {
            'username': user['username']
        }

class ProfileHandler(AuthHandler):

    @tornado.web.authenticated
    def get(self):
        self.set_status(200)
        self.response['username'] = self.current_user['username']
        self.write_json()
