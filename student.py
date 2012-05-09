__author__ = 'Steven_yang'

import os

import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from dataTable import Users
from dataTable import Team
from dataTable import Assignment
from dataTable import ifHasTeam
from dataTable import returnStuANDTeam
from dataTable import query_teams
from dataTable import addMember
from dataTable import quitTeam
from dataTable import updateAssignmentTeam
from dataTable import voteWork

class studentHandler(webapp2.RequestHandler):

    def render_page(self,message1='',message2='',teamID='',voteMessage = ''):
        templateValues = {}
        form  = os.path.join(os.path.dirname(__file__),'templates/student.html')
        username = self.request.get('username')
        user = Users.all().filter('name = ',username).get()

        if not ifHasTeam(username):
            templateValues['hasTeam'] = 'no'
            teams = query_teams()
            templateValues['teams'] = teams
            templateValues['message1'] = message1
            assignments = db.GqlQuery("SELECT * FROM Assignment WHERE pubOrTeam = :1",'public')
            templateValues['teamID'] = teamID

        else:
            templateValues['hasTeam'] = 'yes'
            (members,team,user) = returnStuANDTeam(username)
            templateValues['team'] = team
            templateValues['members'] = members
            assignments = Assignment.all()
            #only teammates can see and vote a team work
            uploadWorks = Team.all().filter('teamID = ',user.teamID).get().works
            templateValues['uploadWorks'] = uploadWorks

        templateValues['assignments'] = assignments
        templateValues['voteMessage'] = voteMessage
        templateValues['username'] = username
        templateValues['message2'] = message2

        templateValues['user'] = user

        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        username = self.request.get('username')
        submit = self.request.get('submit')

        if submit == 'create':

            self.redirect('/createteam?username='+username)
        if submit == 'join':
            teamID = self.request.get('joinTarget')
            joinResult = addMember(teamID,username)
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
            self.redirect('/upload?assignmentName='+assignmentTarget+'&username='+username)
        if submit == 'download':
            assignmentTarget = self.request.get('assignmentTarget')
            self.redirect('/team?assignmentName='+assignmentTarget+'&username='+username)
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




app = webapp2.WSGIApplication([('/student',studentHandler)], debug=True)
