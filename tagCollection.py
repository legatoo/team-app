__author__ = 'Steven_yang'


import os
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import  template

from dataTable import createAssignmentComment
from dataTable import commentAcomment
from dataTable import cookieUsername
from dataTable import Users

class tagCollectionHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/tagcollection.html')
        templateValues ={}
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        tagName = self.request.get('tagName')
        tag = db.GqlQuery("SELECT * FROM Tag WHERE tagName = :1",tagName).get()
        templateValues['tag'] = tag
        templateValues['tagName'] = tagName
        templateValues['user'] = user
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

class assignmentWallHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/assignmentwall.html')
        templateValues ={}
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        user =  Users.all().filter('name = ',username).get()
        reply=self.request.get('reply')
        comment = self.request.get('comment')
        templateValues['replyMode'] = False
        templateValues['commentMode'] = False
        if reply== 'yes':
            commentID = self.request.get('commentID')
            templateValues['replyMode'] = True
            templateValues['commentID'] = int(commentID)

        assignmentName = self.request.get('assignmentName')
        assignment = db.GqlQuery("SELECT * FROM Assignment WHERE assignmentName = :1",assignmentName).get()
        #assignment.comments.order('-date')
        templateValues['assignment'] = assignment
        templateValues['user'] = user
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        assignmentName = self.request.get('assignmentName')
        title = self.request.get('title')
        content = self.request.get('commentContent')
        if title and content:

            paraDic = {
                'username':username,
                'assignmentName':assignmentName,
                'content':content,
                'title':title,

            }
            createAssignmentComment(paraDic)
        if submit == 'commentThis':
            commentID = int(self.request.get('commentID'))
            content = self.request.get('commentContent')
            commentAcomment(username,commentID,content)

        self.redirect('/assignmentwall?assignmentName='+assignmentName)

app = webapp2.WSGIApplication([('/tagcollection',tagCollectionHandler),
                               ('/assignmentwall',assignmentWallHandler)],debug=True)
