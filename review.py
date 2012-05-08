__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template

from dataTable import queryStudentWorks

class reviewHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/review.html')
        templateValues = {}
        assignmentName = self.request.get('assignmentName')
        username = self.request.get('username')
        (teams,assignment) = queryStudentWorks(assignmentName)
        templateValues['teams'] = teams
        templateValues['assignment'] = assignment
        templateValues['username'] = username
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)


app = webapp2.WSGIApplication([('/teacher/review',reviewHandler)],debug=True)