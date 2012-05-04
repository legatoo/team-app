__author__ = 'Steven_yang'

import os
from datetime import  datetime

import  webapp2

from google.appengine.ext.webapp import template
from dataTable import query_students
from dataTable import delete_student
from dataTable import query_tags
from dataTable import ifAssignmentNameOK
from dataTable import createAssignment
from dataTable import query_assigments

def tagDigest(tags):
    tagList = tags.split(';')
    return tagList

class teacherHanlder(webapp2.RequestHandler):
    def render_page(self):
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        students = query_students()
        assignments = query_assigments()
        if students:
            templateValues['students'] = students
        else:
            templateValues['error'] = 'No available student'
        if assignments:
            templateValues['assignments'] = assignments
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
        if submit == 'releaseAssignment':
            username = self.request.get('username')
            self.redirect('/releaseassignment?username='+username)


class releaseAssignmentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self, assignmentName='',tagName='', assignmentContent=''):
        form = os.path.join(os.path.dirname(__file__),'templates/releaseassignment.html')
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        templateValues['tags'] = query_tags()
        templateValues['assignmentName'] = assignmentName
        templateValues['tagName'] = tagName
        templateValues['assignmentContent'] = assignmentContent
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        """
        release an assignment
        """
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        tagNames = tagDigest(str(self.request.get('tagNames')))
        receiver = self.request.get('receiver')
        deadline = datetime( int(self.request.get('year')),
                             int(self.request.get('month')),
                             int(self.request.get('day')))
        assignmentContent = self.request.get('assignmentContent')

        if not ifAssignmentNameOK(assignmentName):
            paraDictionary = {
                'username':username,
                'assignmentName':assignmentName,
                'tagNames':tagNames,
                'receiver':receiver,
                'deadline':deadline,
                'assignmentContent':assignmentContent
            }
            createAssignment(paraDictionary)
        self.redirect('/teacher?username='+username)




app = webapp2.WSGIApplication([('/teacher',teacherHanlder),
                               ('/releaseassignment',releaseAssignmentHandler)],debug=True)
