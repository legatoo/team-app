__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template

from dataTable import Users
from dataTable import Team
from dataTable import Score
from dataTable import Assignment
from dataTable import scoreMem



class stuMutualScoreHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self,message='',confirmMessage=''):
        form = os.path.join(os.path.dirname(__file__),'templates/stumutualscore.html')
        templateValues = {}
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        user = Users.all().filter('name = ',username).get()
        team = Team.all().filter('teamID = ',user.teamID).get()
        memberScores = team.scores.filter('assignmentName = ',assignmentName)
        if user.leader:
            templateValues['leader'] = True
        else:
            templateValues['leader'] = False
        templateValues['user'] = user
        templateValues['assignmentName'] = assignmentName
        templateValues['teamName'] = team.teamName
        templateValues['memberScores'] = memberScores
        templateValues['message'] = message

        templateValues['confirmMessage'] = confirmMessage
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)



    def post(self):
        submit = self.request.get('submit')
        username = self.request.get('username')
        if submit == 'submit':
            score = int(self.request.get('scoreNumber'))
            scoreTarget = int(self.request.get('scoreTarget'))
            comment = self.request.get('comment')
            result = scoreMem(username,scoreTarget,score,comment)
            if result == 'scored':
                self.render_page(message = 'You have scored!')
            if result == 'success':
                self.render_page()
        if submit == 'confirm':

            assignmentName = self.request.get('assignmentName')
            user = Users.all().filter('name = ',username).get()
            team = Team.all().filter('teamID = ',user.teamID).get()
            memberScores = team.scores.filter('assignmentName = ',assignmentName)
            for memberScore in memberScores:
                memberScore.confirm = True
                memberScore.put()
            self.redirect('/student?username='+username)


app = webapp2.WSGIApplication([('/stumutualscore',stuMutualScoreHandler)],debug=True)
