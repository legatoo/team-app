__author__ = 'Steven_yang'
import os

import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from dataTable import Users
from dataTable import Team
from dataTable import Assignment
from dataTable import UplaodWork
from dataTable import teamAssignmentsCollection
from dataTable import cookieUsername


class teamDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'student/download.html')
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        assignmentName = self.request.get('assignmentName')
        teamID = Users.all().filter('name = ',username).get().teamID
        teamName = Team.all().filter('teamID = ',teamID).get().teamName

        (uploads,assignment) = teamAssignmentsCollection(username=username,assignmentName=assignmentName)

        templateValues = {}
        templateValues['teamName'] = teamName
        templateValues['assignment'] = assignment
        templateValues['uploads'] = uploads

        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        uploadID = int(self.request.get('downloadTarget'))
        sourceCode_key = UplaodWork.all().filter('uploadID = ',uploadID).get().sourceCode.key()
        self.send_blob(blobstore.BlobInfo.get(sourceCode_key), save_as=True)



class leaderHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self,message=''):
        form = os.path.join(os.path.dirname(__file__),'student/leadership.html')
        templateValue = {}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)

        leader = Users.all().filter('name = ',user.name).get()
        team = Team.all().filter('teamID = ',leader.teamID).get()
        scores = team.scores.order('-personScore')
        assignments = Assignment.all().fetch(20)
        templateValue['scores'] = scores
        templateValue['user'] = user
        templateValue['assignments'] = assignments
        templateValue['message'] = message

        renderPage = template.render(form,templateValue)
        self.response.out.write(renderPage)

    def post(self):

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        assignmentName = self.request.get('assignmentName')
        user = Users.all().filter('name = ',username).get()
        team = Team.all().filter('teamID = ',user.teamID).get()
        memberScores = team.scores.filter('assignmentName = ',assignmentName).order('-personScore')
        #count = memberScores.count(1)
        rank = 1
        for memberScore in memberScores:
            memberScore.confirm = True
            memberScore.personRank = rank
            rank += 1
            memberScore.put()
        self.render_page(message='Confirm successfully!')




app = webapp2.WSGIApplication([('/student/download',teamDownloadHandler),
                               ('/student/leadership',leaderHandler)],debug=True)