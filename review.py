__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from dataTable import Users
from dataTable import queryStudentWorks
from dataTable import UplaodWork
from dataTable import cookieUsername

class reviewHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/review.html')
        templateValues = {}
        assignmentName = self.request.get('assignmentName')

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

        (teams,assignment) = queryStudentWorks(assignmentName)
        templateValues['teams'] = teams
        templateValues['assignment'] = assignment
        templateValues['username'] = username
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')
        if submit == 'Download':
            uploadID = int(self.request.get('target'))
            sourceCode_key = UplaodWork.all().filter('uploadID = ',uploadID).get().sourceCode.key()
            self.send_blob(blobstore.BlobInfo.get(sourceCode_key), save_as=True)
        if submit == 'Score':
            teamID = self.request.get('teamID')
            assignmentName = self.request.get('assignmentName')
            self.redirect('/teachergrade?teamID='+teamID+'&assignmentName='+assignmentName)

app = webapp2.WSGIApplication([('/teacher/review',reviewHandler)],debug=True)