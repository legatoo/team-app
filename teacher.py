__author__ = 'Steven_yang'

import os
import  webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dataTable import query_students
from dataTable import delete_student





class teacherHanlder(webapp2.RequestHandler):
    def render_page(self):
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        students = query_students()
        if students:
            templateValues['students'] = students
        else:
            templateValues['error'] = 'No available student'
        form = os.path.join(os.path.dirname(__file__),'templates/teacher.html')
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        submit = self.request.get('submit')
        if submit == 'Delete':
            ifDelete = self.request.get('delete')
            if ifDelete == 'yes':
                deleteTarget = self.request.get('deleteTarget')
                delete_student(deleteTarget)
                self.render_page()
        if submit == 'Add Student':
            addUser = self.request.get('addUser')
            if addUser == 'yes':
                messge = 'Add A New Student'
                self.redirect('/signup?message='+messge)



app = webapp2.WSGIApplication([('/teacher',teacherHanlder)],debug=True)
