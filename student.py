__author__ = 'Steven_yang'

import os

import webapp2
from google.appengine.ext.webapp import template
from dataTable import ifHasTeam
from dataTable import returnStuANDTeam
from dataTable import query_teams
from dataTable import addMember

class studentHandler(webapp2.RequestHandler):

    def render_page(self,message='',teamID=''):
        templateValues = {}
        form  = os.path.join(os.path.dirname(__file__),'templates/student.html')
        username = self.request.get('username')
        if not ifHasTeam(username):
            templateValues['hasTeam'] = 'no'
            teams = query_teams()
            templateValues['teams'] = teams
            templateValues['message'] = message
            templateValues['teamID'] = teamID
        else:
            templateValues['hasTeam'] = 'yes'
            (members,team) = returnStuANDTeam(username)
            templateValues['team'] = team
            templateValues['members'] = members
        templateValues['username'] = username
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
            if addMember(teamID,username) == 'fail':
                self.render_page(message='join failed!',teamID=teamID)
            else:
                self.render_page(message='join success!')



app = webapp2.WSGIApplication([('/student',studentHandler)], debug=True)
