__author__ = 'Steven_yang'

import os
import json
import csv


import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers


from dataTable import Users
from dataTable import Team
from dataTable import Score
from dataTable import Assignment
from dataTable import UplaodWork
from dataTable import ifHasTeam
from dataTable import returnStuANDTeam
from dataTable import addMember
from dataTable import quitTeam
from dataTable import updateAssignmentTeam
from dataTable import voteWork
from dataTable import cookieUsername
from dataTable import createTeam


def findTop3(assignments):
    topThree = []
    for assignment in assignments:
        if assignment.topThree:
            top3 = assignment.topThree.order('-score').fetch(3)
            if top3:
                topThree.append((assignment.assignmentName,top3))

    return topThree


def returnCSV(user):
    scores = user.scores
    teamName = Team.all().filter('teamID = ',user.teamID).get().teamName
    #cvs = ""
    if scores:
        csv = "Name,Team,Role,Assignment,PersonScore,PersonRank,Votes,TeamScore,TeamRank\n"
        for score in scores:
            csv += str(user.name)+','
            csv += str(teamName)+','
            csv += str(user.teamRole)+','
            csv += str(score.assignmentName)+','
            csv += str(score.personScore)+','
            csv += str(score.personRank)+','
            csv += str(score.votes)+','
            csv += str(score.teamScore)+','
            csv += str(score.teamRank)+'\n'
        return csv


class studentHomeHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'student/index.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user = Users.all().filter('name = ',username).get()
        templateValues['user'] = user
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        pass

class studentTeamHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self,message1='',message2='',teamID=''):
        form  = os.path.join(os.path.dirname(__file__),'student/team.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)

        quit = self.request.get('quit')
        if quit == 'yes':
            quitResult = quitTeam(user.name)
            if quitResult == 'lock':
                (team,user) = returnStuANDTeam(user.name)
                templateValues['team'] = team
                templateValues['message2'] = 'team has been locked!'
            if quitResult == 'successQuit':
                updateAssignmentTeam(user.name,'quit')
                self.redirect('/student/team')
            if quitResult == 'fail':
                (team,user) = returnStuANDTeam(user.name)
                templateValues['team'] = team
                templateValues['message2'] = 'quit failed!'
        else:
            if not user.hasTeam:
                templateValues['hasTeam'] = 'no'
                teams = Team.all().fetch(20)
                templateValues['teams'] = teams
                templateValues['message1'] = message1
                templateValues['teamID'] = teamID

            else:
                templateValues['hasTeam'] = 'yes'
                (team,user) = returnStuANDTeam(user.name)
                templateValues['team'] = team

        templateValues['user'] = user

        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)
    def post(self):
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

        teamID = self.request.get('joinTarget')
        teamRole = self.request.get('teamRole')
        joinResult = addMember(teamID,username,teamRole)
        if  joinResult == 'fail':
            self.render_page(message1='join failed!',teamID=teamID)
        elif joinResult == 'lock':
            self.render_page(message1='team locked',teamID=teamID)
        else:
            updateAssignmentTeam(username,'join')
            self.render_page(message1='join success!')

class studentCreateTeamHandler(webapp2.RequestHandler):
    def render_page(self,teamName='',error=''):
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        form = os.path.join(os.path.dirname(__file__),'student/createteam.html')
        templateValues['teamName'] = teamName
        templateValues['teamNameError'] = error
        templateValues['user'] = user
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        teamName = self.request.get('teamName')
        teamRole = self.request.get('teamRole')
        flag = createTeam(username,teamName,teamRole)
        if flag == 'success':
            updateAssignmentTeam(username,'join')
            self.redirect('/student/team')
        if flag == 'teamExisted':
            error = 'Team has already existed!'
            self.render_page(teamName=teamName,error=error)
        if flag == 'hadTeam':
            error = 'You can only join one team!'
            self.render_page(teamName=teamName,error=error)

class studentAssignmentHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self,error=''):
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        form = os.path.join(os.path.dirname(__file__),'student/assignment.html')
        templateValues['user'] = user
        assignmentName = self.request.get('assignmentName')
        templateValues = {}
        if assignmentName:
            assignments = Assignment.all().filter('assignmentName = ',assignmentName).get()
            templateValues['assignment'] = assignments
            templateValues['error'] = error
        else:
            assignments = Assignment.all().fetch(20)
            if assignments:
                templateValues['assignments'] = assignments

        topThree = findTop3(assignments)
        templateValues['topThree'] = topThree
        templateValues['user'] = user

        renderPage = template.render(form,templateValues)
        self.response.write(renderPage)
    def post(self):
        pass

class studentProductHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self,voteMessage=''):
        form = os.path.join(os.path.dirname(__file__),'student/product.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        if user.hasTeam:
            team = Team.all().filter('teamID = ',user.teamID).get()
            templateValues['team'] = team
            teamWorks = team.works.order('assignmentName').fetch(50)
            templateValues['teamWorks'] = teamWorks
        assignments = Assignment.all().fetch(20)
        templateValues['user'] = user
        templateValues['assignments'] = assignments
        templateValues['voteMessage'] = voteMessage

        renderPage = template.render(form, templateValues)
        self.response.write(renderPage)

    def post(self):

        submit = self.request.get('submit')
        if submit == 'voteUp':
            vote = self.request.get('voteUp')
            if voteWork(vote):
                self.render_page(voteMessage='Thanks for voting!')
            else :
                self.render_page(voteMessage='You can vote this work only once!')
        if submit == 'voteDown':
            vote = self.request.get('voteDown')
            if voteWork(vote):
                self.render_page(voteMessage='Thanks for voting!')
            else :
                self.render_page(voteMessage='You can vote this work only once!')

class studentMyscoreHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'student/myscores.html')
        templateValues = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        myScores = Score.all().filter('username = ',user.name)

        templateValues['user'] = user
        templateValues['myScores'] = myScores

        renderPage = template.render(form,templateValues)
        self.response.write(renderPage)
    def post(self):
        pass

class studentTopworkHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'student/topwork.html')
        templateValue = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        assignmentName = self.request.get('assignmentName')
        assignment = Assignment.all().filter('assignmentName = ',assignmentName).get()
        top3 = assignment.topThree.order('-score').fetch(3)
        templateValue['top3'] = top3
        topwork = []
        i = 1
        for top in top3:
            team = Team.all().filter('teamName = ',top.teamName).get()
            temp = team.works.filter('assignmentName = ',assignmentName).fetch(20)
            topwork.append((str(i),temp))
            i += 1
        templateValue['topworks'] = topwork
        templateValue['assignment'] = assignment
        templateValue['top3'] = top3
        templateValue['user'] = user

        renderPage = template.render(form,templateValue)
        self.response.write(renderPage)

    def post(self):
        uploadID = int(self.request.get('downloadTarget'))
        sourceCode_key = UplaodWork.all().filter('uploadID = ',uploadID).get().sourceCode.key()
        self.send_blob(blobstore.BlobInfo.get(sourceCode_key), save_as=True)

class csvHandler(webapp2.RequestHandler):
    def get(self):
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        self.response.headers.add_header(str('Content-Disposition'), str('attachment;filename='+username+'Scores.csv'))

        user = Users.all().filter('name = ',username).get()
        csvFormatScore = returnCSV(user)
        self.response.out.write(csvFormatScore)


app = webapp2.WSGIApplication([
                               ('/student/home',studentHomeHandler),
                               ('/student/team',studentTeamHandler),
                               ('/student/createteam',studentCreateTeamHandler),
                               ('/student/assignment',studentAssignmentHandler),
                               ('/student/product',studentProductHandler),
                               ('/student/myscore',studentMyscoreHandler),
                               ('/student/topwork',studentTopworkHandler),
                               ('/student.csv',csvHandler)
                                ], debug=True)
