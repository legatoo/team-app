__author__ = 'Steven_yang'

import os

import webapp2
from google.appengine.ext.webapp import template

from dataTable import cookieUsername

class introDuctionHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/introduction.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        templateValues['user'] = user
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)
    def post(self):
        pass



app = webapp2.WSGIApplication([('/introduction',introDuctionHandler)],debug=True)