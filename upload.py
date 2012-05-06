__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template
from dataTable import createUploadWork


class uploadHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/upload.html')
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)


    def post(self):
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        title = self.request.get('uploadTitle')
        version = self.request.get('uploadVersion')
        description = self.request.get('uploadDescription')
        paraDic = {
            'username': username,
            'assignmentName':assignmentName,
            'title':title,
            'version':version,
            'description':description
        }
        createUploadWork(paraDic)
        self.redirect('/student?username='+username)

app = webapp2.WSGIApplication([('/upload',uploadHandler)],debug=True)