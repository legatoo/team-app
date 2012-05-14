__author__ = 'Steven_yang'

import os
import webapp2

from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from dataTable import UplaodWork
from dataTable import Assignment
from dataTable import createUploadComment
from dataTable import commentAcomment
from dataTable import cookieUsername

class teamworkCommentHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/teamworkcomments.html')
        templateValues= {}
        uploadID = int(self.request.get('uploadID'))
        work = db.GqlQuery("SELECT * FROM UplaodWork WHERE uploadID = :1",uploadID).get()

        assignmentName = work.assignmentName
        assignment = db.GqlQuery("SELECT * FROM Assignment WHERE assignmentName = :1",assignmentName).get()

        templateValues['assignment'] = assignment

        templateValues['work'] = work
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        uploadID = int(self.request.get('uploadID'))

        uploadWork = UplaodWork.all().filter('uploadID = ',uploadID).get()
        assignmentName =uploadWork.assignmentName
        if submit == 'Download':
            self.redirect('/team?assignmentName='+assignmentName)
        if submit == 'Comment':
            title = self.request.get('title')
            content = self.request.get('content')
            paraDic = {
                'username':username,
                'assignmentName':'',
                'content':content,
                'title':title,
                'uploads':uploadWork
            }
            createUploadComment(paraDic)
            self.render_page()
        if submit == 'commentThis':
            commentID = int(self.request.get('commentID'))
            content = self.request.get('commentContent')
            commentAcomment(username,commentID,content)
            self.render_page()








app = webapp2.WSGIApplication([('/teamworkcomments',teamworkCommentHandler)],debug=True)