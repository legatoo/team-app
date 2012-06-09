__author__ = 'Steven_yang'

import os
import webapp2

from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from dataTable import Users
from dataTable import UplaodWork
from dataTable import Assignment
from dataTable import createUploadComment
from dataTable import commentAcomment
from dataTable import cookieUsername
from dataTable import scoreMem

class teamworkCommentHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        self.render_page()
    def render_page(self,error='',message=''):
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        form = os.path.join(os.path.dirname(__file__),'templates/teamworkcomments.html')
        templateValues= {}
        uploadID = int(self.request.get('uploadID'))

        reply=self.request.get('reply')
        comment = self.request.get('comment')
        templateValues['replyMode'] = False
        templateValues['commentMode'] = False
        if reply== 'yes':
            commentID = self.request.get('commentID')
            templateValues['replyMode'] = True
            templateValues['commentID'] = int(commentID)
        if comment == 'yes':
            templateValues['commentMode'] = True

        work = db.GqlQuery("SELECT * FROM UplaodWork WHERE uploadID = :1",uploadID).get()

        assignmentName = work.assignmentName
        assignment = db.GqlQuery("SELECT * FROM Assignment WHERE assignmentName = :1",assignmentName).get()

        templateValues['assignment'] = assignment
        templateValues['user'] = user
        templateValues['work'] = work
        templateValues['error'] = error
        templateValues['message'] = message
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        uploadID = int(self.request.get('uploadID'))

        uploadWork = UplaodWork.all().filter('uploadID = ',uploadID).get()
        score = self.request.get('score')
        if score:
            if score.isdigit():
                score = int(score)
                if score > 100 or score < 0:
                    self.render_page(error='Score should be number between [0-100].')
                else:
                    scoreTargetStu = Users.all().filter('name = ',uploadWork.author).get()
                    scoreTarget = scoreTargetStu.scores.filter('assignmentName = ',uploadWork.assignmentName).get()
                    result = scoreMem(username,scoreTarget,score)
                    if result == 'scored':
                        self.render_page(message = 'You have scored!')
                    if result == 'success':
                        self.render_page(message='Succeed!')
            else:
                self.render_page(error='Score can not be empty! '\
                                           'Score should be number between [0-100].')
        else :
            self.render_page(error='Score can not be empty! '\
                                       'Score should be number between [0-100].')

        title = self.request.get('title')
        content = self.request.get('commentContent')
        if title and content:

            paraDic = {
                'username':username,
                'assignmentName':'',
                'content':content,
                'title':title,
                'uploads':uploadWork

            }
            createUploadComment(paraDic)
            self.redirect('/student/teamworkcomments?uploadID='+str(uploadID))

        if submit == 'commentThis':
            commentID = int(self.request.get('commentID'))
            content = self.request.get('commentContent')
            commentAcomment(username,commentID,content)
            self.redirect('/student/teamworkcomments?uploadID='+str(uploadID))



app = webapp2.WSGIApplication([('/student/teamworkcomments',teamworkCommentHandler)],debug=True)