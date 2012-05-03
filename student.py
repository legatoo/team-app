__author__ = 'Steven_yang'

import os

import webapp2
from google.appengine.ext.webapp import template

class studentHandler(webapp2.RequestHandler):

    def render_page(self):
        form  = os.path.join(os.path.dirname(__file__),'templates/student.html')
        username = self.request.get('username')
        templateValues = {}
        templateValues['username'] = username
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        pass


app = webapp2.WSGIApplication([('/student',studentHandler)], debug=True)
