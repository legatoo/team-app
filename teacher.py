__author__ = 'Steven_yang'

import os
from datetime import  datetime

import  webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dataTable import Assignment
from dataTable import query_students
from dataTable import delete_student
from dataTable import query_tags
from dataTable import ifAssignmentNameOK
from dataTable import createAssignment
from dataTable import query_assigments
from dataTable import updateAssignment
from dataTable import query_teams
from dataTable import lockTeam


def tagDigest(tags):
    tagList = tags.split(';')
    return tagList

class teacherHanlder(webapp2.RequestHandler):
    def render_page(self,editMessage = ''):
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        students = query_students()
        assignments = query_assigments()
        teams = query_teams()
        if students:
            templateValues['students'] = students
        else:
            templateValues['error'] = 'No available student'
        if assignments:
            templateValues['assignments'] = assignments
        if teams:
            templateValues['teams'] = teams
        templateValues['editMessage'] = editMessage
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
            #addUser = self.request.get('addUser')
            #if addUser == 'yes':
                #messge = 'Add A New Student'
                #self.redirect('/signup?message='+messge)
            self.redirect('/addstudent')
        if submit == 'releaseAssignment':
            username = self.request.get('username')
            self.redirect('/releaseassignment?username='+username)
        if submit == 'editAssignment':
            assignmentName = self.request.get('editTarget')
            now = datetime.now()
            deadLine = Assignment.all().filter('assignmentName = ',assignmentName).get().deadLine
            if now < deadLine:
                self.redirect('/editassignment?assignmentName='+assignmentName)
            else:
                self.render_page(editMessage='You can not edit a expired assignment')
        if submit == 'reviewAssignment':
            assignmentName = self.request.get('reviewTarget')
            username = self.request.get('username')
            self.redirect('/teacher/review?assignmentName='+assignmentName+'&username='+username)
        if submit == 'lock':
            lockTarget = self.request.get('lockTarget')
            lockTeam(lockTarget)
            self.render_page(message = 'team locked!')



class releaseAssignmentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self, assignmentName='',
                    assignmentNameError='',
                    tagName='',
                    assignmentContent='',
                    contentError='',
                    deadLineError=''):
        form = os.path.join(os.path.dirname(__file__),'templates/releaseassignment.html')
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        templateValues['tags'] = query_tags()
        templateValues['assignmentName'] = assignmentName
        templateValues['assignmentNameError'] = assignmentNameError
        templateValues['tagName'] = tagName
        templateValues['assignmentContent'] = assignmentContent
        templateValues['contentError'] = contentError
        templateValues['deadLineError'] = deadLineError
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        """
        release an assignment
        """
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        tagName = str(self.request.get('tagNames'))
        assignmentContent = self.request.get('assignmentContent')
        receiver = self.request.get('receiver')
        dueTime = self.request.get('deadLine')
        deadlineDMY = dueTime.split('/')
        deadline = datetime(
            int(deadlineDMY[2]),
            int(deadlineDMY[0]),
            int(deadlineDMY[1]),
        )

        now = datetime.now()
        if now > deadline:
            self.render_page(
                assignmentName=assignmentName,
                tagName=tagName,
                assignmentContent=assignmentContent,
                deadLineError='DeadLine is invalid!'
            )
        elif not assignmentContent:
            self.render_page(
                assignmentName=assignmentName,
                tagName=tagName,
                contentError='Content can not be empty!'
            )

        elif ifAssignmentNameOK(assignmentName):
            self.render_page(
                assignmentName = assignmentName,
                assignmentNameError='Duplicate assignment name!',
                assignmentContent=assignmentContent,
                tagName=tagName
            )
        else:
            tagNames = tagDigest(tagName)
            paraDictionary = {
                'username':username,
                'assignmentName':assignmentName,
                'tagNames':tagNames,
                #'tagNames':checkboxTagNames,
                'receiver':receiver,
                'deadline':deadline,
                'assignmentContent':assignmentContent,
                }
            createAssignment(paraDictionary)

            self.redirect('/teacher?username='+username)

class editAssignmentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self,error = ''):
        form = os.path.join(os.path.dirname(__file__),'templates/editassignment.html')
        templateValues = {}
        assignmentName = self.request.get('assignmentName')
        assignment = Assignment.all().filter('assignmentName = ',assignmentName).get()
        templateValues['assignment'] = assignment
        templateValues['error'] = error
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        deadLine = datetime( int(self.request.get('year')),
            int(self.request.get('month')),
            int(self.request.get('day')))
        now = datetime.now()
        if deadLine < now:
            self.render_page(error='Due time invalid!')
        else:
            assignmentName = self.request.get('assignmentName')
            assignmentContent = self.request.get('assignmentContent')
            updateAssignment(assignmentName,deadLine,assignmentContent)
            self.redirect('/teacher')




app = webapp2.WSGIApplication([('/teacher',teacherHanlder),
                               ('/releaseassignment',releaseAssignmentHandler),
                               ('/editassignment',editAssignmentHandler)],debug=True)
