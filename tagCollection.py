__author__ = 'Steven_yang'


import os
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import  template

from dataTable import createAssignmentComment
from dataTable import commentAcomment


class tagCollectionHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/tagcollection.html')
        templateValues ={}
        tagName = self.request.get('tagName')
        tag = db.GqlQuery("SELECT * FROM Tag WHERE tagName = :1",tagName).get()
        templateValues['tag'] = tag
        templateValues['tagName'] = tagName
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)
class assignmentWallHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'templates/assignmentwall.html')
        templateValues ={}
        assignmentName = self.request.get('assignmentName')
        assignment = db.GqlQuery("SELECT * FROM Assignment WHERE assignmentName = :1",assignmentName).get()
        #assignment.comments.order('-date')
        templateValues['assignment'] = assignment
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def post(self):
        submit = self.request.get('submit')
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        if submit == 'comment':
            content = self.request.get('content')
            title = self.request.get('title')
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

        self.render_page()

app = webapp2.WSGIApplication([('/tagcollection',tagCollectionHandler),
                               ('/assignmentwall',assignmentWallHandler)],debug=True)
