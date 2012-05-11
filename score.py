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

    def render_page(self,message='',confirmMessage='',error=''):
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
        templateValues['error'] = error

        templateValues['confirmMessage'] = confirmMessage
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)



    def post(self):
        submit = self.request.get('submit')
        username = self.request.get('username')
        if submit == 'submit':
            score = self.request.get('scoreNumber')
            scoreTarget = int(self.request.get('scoreTarget'))
            comment = self.request.get('comment')
            if score and comment:
                if score.isdigit():
                    score = int(score)
                    if score > 100 or score < 0:
                        self.render_page(error='Score and comment can not be empty! ' \
                                           'Score should be number between [0-100].')
                    else:
                        result = scoreMem(username,scoreTarget,score,comment)
                        if result == 'scored':
                            self.render_page(message = 'You have scored!')
                        if result == 'success':
                            self.render_page()
                else:
                    self.render_page(error='Score and comment can not be empty! '\
                                           'Score should be number between [0-100].')
            else :
                self.render_page(error='Score and comment can not be empty! ' \
                                       'Score should be number between [0-100].')
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
