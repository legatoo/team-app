__author__ = 'Steven_yang'

import os
import json
import csv


import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from dataTable import Users
from dataTable import Team
from dataTable import Score
from dataTable import Assignment
from dataTable import ifHasTeam
from dataTable import returnStuANDTeam
from dataTable import query_teams
from dataTable import addMember
from dataTable import quitTeam
from dataTable import updateAssignmentTeam
from dataTable import voteWork
from dataTable import TeamScore
from dataTable import cookieUsername


def findTop3(assignments):
    topThree = []
    for assignment in assignments:
        if assignment.topThree:
            top3 = assignment.topThree.order('-score').fetch(3)
            topThree.append((assignment.assignmentName,top3))
    return topThree


def returnCSV(user):
    scores = user.scores
    teamName = Team.all().filter('teamID = ',user.teamID).get().teamName
    cvs = ""
    if scores:
        cvs = "Name,Team,Role,Assignment,PersonScore,PersonRank,Votes,TeamScore,TeamRank\n"
        for score in scores:
            cvs += str(user.name)+','
            csv += str(teamName)+','
            csv += str(user.teamRole)+','
            cvs += str(score.assignmentName)+','
            cvs += str(score.personScore)+','
            cvs += str(score.personRank)+','
            cvs += str(score.votes)+','
            cvs += str(score.teamScore)+','
            cvs += str(score.teamRank)+'\n'
        return cvs

class studentHandler(webapp2.RequestHandler):

    def render_page(self,message1='',message2='',teamID='',voteMessage = ''):
        templateValues = {}
        form  = os.path.join(os.path.dirname(__file__),'templates/student.html')
        #username = self.request.get('username')
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        username = user.name

        if not ifHasTeam(username):
            templateValues['hasTeam'] = 'no'
            teams = query_teams()
            templateValues['teams'] = teams
            templateValues['message1'] = message1
            assignments = db.GqlQuery("SELECT * FROM Assignment WHERE pubOrTeam = :1",'public')
            templateValues['teamID'] = teamID

        else:
            templateValues['hasTeam'] = 'yes'
            (team,user) = returnStuANDTeam(username)
            templateValues['team'] = team
            assignments = Assignment.all()


        myScores = Score.all().filter('username = ',username)

        topThree = findTop3(assignments)

        templateValues['assignments'] = assignments
        templateValues['voteMessage'] = voteMessage
        templateValues['username'] = username
        templateValues['message2'] = message2
        templateValues['myScores'] = myScores
        templateValues['topThree'] = topThree

        templateValues['user'] = user

        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        submit = self.request.get('submit')

        if submit == 'create':

            self.redirect('/createteam')
        if submit == 'join':
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
        if submit == 'quit':
            quitResult = quitTeam(username)
            if quitResult == 'lock':
                self.render_page(message2='team has been locked!')
            if quitResult == 'successQuit':
                updateAssignmentTeam(username,'quit')
                self.render_page(message2='quit success!')
            if quitResult == 'fail':
                self.render_page(message2='quit failed!')
        if submit == 'upload':
            assignmentTarget = self.request.get('assignmentTarget')
            self.redirect('/upload?assignmentName='+assignmentTarget)
        if submit == 'download':
            assignmentTarget = self.request.get('assignmentTarget')
            self.redirect('/team?assignmentName='+assignmentTarget)
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
        if submit == 'leader':
            assignmentTarget = self.request.get('assignmentTarget')
            self.redirect('/team/leader?assignmentName='+assignmentTarget)
        if submit == 'export':
            self.redirect('/student.json')


class csvHandler(webapp2.RequestHandler):
    def get(self):
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        self.response.headers.add_header(str('Content-Disposition'), str('attachment;filename='+username+'.csv'))
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user = Users.all().filter('name = ',username).get()
        csvFormatScore = returnCSV(user)
        self.response.out.write(csvFormatScore)


app = webapp2.WSGIApplication([('/student',studentHandler),
                               ('/student.csv',csvHandler)], debug=True)
