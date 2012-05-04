__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template

from dataTable import createTeam


class createdTeamHandler(webapp2.RequestHandler):
    def render_page(self,teamName='',error=''):
        templateValues = {}
        form = os.path.join(os.path.dirname(__file__),'templates/createteam.html')
        templateValues['teamName'] = teamName
        templateValues['teamNameError'] = error
        renderForm = template.render(form,templateValues)
        self.response.out.write(renderForm)

    def get(self):
        self.render_page()

    def post(self):
        username = self.request.get('username')
        teamName = self.request.get('teamName')
        flag = createTeam(username,teamName)
        if flag == 'success':
            self.redirect('/student?username='+username)
        if flag == 'teamExisted':
            error = 'Team has already existed!'
            self.render_page(teamName=teamName,error=error)
        if flag == 'hadTeam':
            error = 'You can only join one team!'
            self.render_page(teamName=teamName,error=error)




app = webapp2.WSGIApplication([('/createteam',createdTeamHandler)],debug=True)
