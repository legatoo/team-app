__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from dataTable import queryStudentWorks
from dataTable import UplaodWork

class reviewHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/review.html')
        templateValues = {}
        assignmentName = self.request.get('assignmentName')
        username = self.request.get('username')
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


app = webapp2.WSGIApplication([('/teacher/review',reviewHandler)],debug=True)