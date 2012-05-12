__author__ = 'Steven_yang'

import os
import webapp2

from google.appengine.ext.webapp import template

from dataTable import query_students
from dataTable import ifUsernameOK
from dataTable import addStudent

class addStudentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self,error=''):
        form = os.path.join(os.path.dirname(__file__),'templates/addstudent.html')
        templateValues = {}
        students = query_students()
        if students:
            templateValues['students'] = students
        templateValues['error'] = error
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        username = self.request.get('name')
        studentID = self.request.get('studentID')
        email = self.request.get('email')
        password = self.request.get('password')
        if not ifUsernameOK(username):
            paraTuple = (username,password,int(studentID),email,'student')
            addStudent(paraTuple)
            self.render_page()
        else:
            self.render_page(error='Student has already exited!')

app = webapp2.WSGIApplication([('/addstudent',addStudentHandler)],debug=True)