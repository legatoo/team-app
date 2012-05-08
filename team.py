__author__ = 'Steven_yang'
import os

import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from dataTable import Users
from dataTable import Team
from dataTable import UplaodWork
from dataTable import teamAssignmentsCollection



class teamHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/team.html')
        username = self.request.get('username')
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


app = webapp2.WSGIApplication([('/team',teamHandler)],debug=True)