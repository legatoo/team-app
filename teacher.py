__author__ = 'Steven_yang'

import os
from datetime import  datetime

import  webapp2

from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from dataTable import Users
from dataTable import Team
from dataTable import Assignment
from dataTable import query_students
from dataTable import delete_student
from dataTable import query_tags
from dataTable import ifAssignmentNameOK
from dataTable import createAssignment
from dataTable import queryStudentWorks
from dataTable import updateAssignment
from dataTable import lockTeam
from dataTable import cookieUsername
from dataTable import ifUsernameOK
from dataTable import addStudent
from dataTable import UplaodWork
from dataTable import ifScored

editMode =  False

def tagDigest(tags):
    tagList = tags.split(';')
    return tagList

def returnCSV():
    students = Users.all()

    csv = "Name,Team,Role,Assignment,PersonScore,PersonRank,Votes,TeamScore,TeamRank\n"
    for student in students:
        teamName = None
        team = Team.all().filter('teamID = ',student.teamID).get()
        if team:
            teamName = team.teamName
        for score in student.scores:
            if score:
                csv += str(student.name)+','
                csv += str(teamName)+','
                csv += str(student.teamRole)+','
                csv += str(score.assignmentName)+','
                csv += str(score.personScore)+','
                csv += str(score.personRank)+','
                csv += str(score.votes)+','
                csv += str(score.teamScore)+','
                csv += str(score.teamRank)+'\n'
    return csv

class teacherHomeHanlder(webapp2.RequestHandler):
    def render_page(self,editMessage = '',message=''):
        templateValues = {}

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

        user =  Users.all().filter('name = ',username).get()

        form = os.path.join(os.path.dirname(__file__),'teacher/index.html')
        templateValues['user'] = user
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        submit = self.request.get('submit')
        if submit == 'reviewAssignment':
            assignmentName = self.request.get('reviewTarget')
            self.redirect('/teacher/review?assignmentName='+assignmentName)
        if submit == 'lock':
            lockTarget = self.request.get('lockTarget')
            lockTeam(lockTarget)
            self.render_page(message = 'team locked!')

class teacherTeamHandler(webapp2.RequestHandler):
    def render_page(self,message=''):
        templateValues = {}

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

        user =  Users.all().filter('name = ',username).get()
        teams = Team.all().fetch(20)
        form = os.path.join(os.path.dirname(__file__),'teacher/team.html')
        if teams:
            templateValues['teams'] = teams
        templateValues['user'] = user
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()
    def post(self):
        submit = self.request.get('submit')
        if submit == 'lock':
            lockTarget = self.request.get('lockTarget')
            lockTeam(lockTarget)
            self.render_page(message = 'team locked!')

class teacherStuHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self,error=''):
        form = os.path.join(os.path.dirname(__file__),'teacher/student.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        templateValues['user'] = user
        students = query_students()
        if students:
            templateValues['students'] = students
        templateValues['error'] = error
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')
        if submit == 'Delete':
            ifDelete = self.request.get('delete')
            if ifDelete == 'yes':
                deleteTarget = self.request.get('deleteTarget')
                delete_student(deleteTarget)
                self.render_page()
        else:
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

class teacherAssignmentHandler(webapp2.RequestHandler):
    def render_page(self,error='',editMessage=''):
        global editMode
        assignmentName = self.request.get('assignmentName')
        templateValues = {}
        if assignmentName:
            editMode = True
            templateValues['editMode'] = True
            assignment = Assignment.all().filter('assignmentName = ',assignmentName).get()
            templateValues['assignment'] = assignment
            templateValues['error'] = error
        else:
            assignments = Assignment.all().fetch(20)
            if assignments:
                templateValues['assignments'] = assignments

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user =  Users.all().filter('name = ',username).get()

        form = os.path.join(os.path.dirname(__file__),'teacher/assignment.html')
        templateValues['user'] = user

        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)
    def get(self):
        self.render_page()
    def post(self):
        global editMode
        dueTime = self.request.get('deadLine')
        deadlineDMY = dueTime.split('/')
        deadline = datetime(
            int(deadlineDMY[2]),
            int(deadlineDMY[0]),
            int(deadlineDMY[1]),
        )
        now = datetime.now()
        if deadline < now:
            editMode = False
            self.render_page(error='Due time invalid! You can\'t edit this assignment')
        else:
            assignmentName = self.request.get('assignmentName')
            assignmentContent = self.request.get('assignmentContent')
            updateAssignment(assignmentName,deadline,assignmentContent)
            editMode = False
            self.redirect('/teacher/assignment')


class releaseAssignmentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self, assignmentName='',
                    assignmentNameError='',
                    tagName='',
                    assignmentContent='',
                    contentError='',
                    deadLineError=''):
        form = os.path.join(os.path.dirname(__file__),'teacher/releaseassignment.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

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
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

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

            self.redirect('/teacher/assignment')

class teacherReviewHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def render_page(self,message = ''):
        form = os.path.join(os.path.dirname(__file__),'teacher/review.html')
        templateValues = {}

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user = Users.all().filter('name = ',username).get()
        (teams,assignments) = queryStudentWorks()
        templateValues['teams'] = teams
        templateValues['assignments'] = assignments
        templateValues['user'] = user
        templateValues['message'] = message
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def get(self):
        self.render_page()
    def post(self):

        uploadID = int(self.request.get('target'))
        sourceCode_key = UplaodWork.all().filter('uploadID = ',uploadID).get().sourceCode.key()
        self.send_blob(blobstore.BlobInfo.get(sourceCode_key), save_as=True)


class csvHandler(webapp2.RequestHandler):
    def get(self):

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user = Users.all().filter('name = ',username).get()
        if user.role == 'teacher':
            csvFormatScore = returnCSV()
            self.response.headers.add_header(str('Content-Disposition'), str('attachment;filename=studentScores.csv'))
            self.response.out.write(csvFormatScore)
        else:
            self.response.out.write('Permission denied!')


app = webapp2.WSGIApplication([('/teacher/home',teacherHomeHanlder),
                               ('/teacher/team',teacherTeamHandler),
                               ('/teacher/students',teacherStuHandler),
                               ('/teacher/assignment',teacherAssignmentHandler),
                               ('/teacher/review',teacherReviewHandler),
                               ('/teacher/releaseassignment',releaseAssignmentHandler),
                               ('/teacher/review',teacherReviewHandler),
                               ('/teacher.csv',csvHandler)],debug=True)
