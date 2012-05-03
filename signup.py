__author__ = 'Steven_yang'

import os

from login import input_validation
from dataTable import Users

import webapp2
from google.appengine.ext.webapp import template


class Error():
    ifError = False
    pass

def ifTwoPasswordSame(pw1,pw2):
    return pw1 == pw2

def addStudent(paraTuple):
    new_user = Users(name = paraTuple[0], password = paraTuple[1],
                     email = paraTuple[2], role = paraTuple[3], leader = False)
    new_user.put()

class signupHandler(webapp2.RequestHandler):
    def render_page(self,username = '',email='', role = '',message = 'User Sign Up',
                    error = None):
        messageTeacher = self.request.get('message')
        templateValues = {'username':username,
                          'email':email,
                          'role':role,
                          'message':message,
                          'error':error}
        if messageTeacher:
            templateValues['message'] = messageTeacher
        form = os.path.join(os.path.dirname(__file__),'templates/signup.html')

        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)

    def get(self):
        self.render_page()

    def post(self):
        username = self.request.get('username')
        password =self.request.get('password')
        pwAgain = self.request.get('pwAgain')
        email = self.request.get('email')
        role = self.request.get('role')
        error = Error()

        if not input_validation(('username',username)):
            error.ifError = True
            error.username = 'This is a invalid username'
        if not input_validation(('password',password)):
            error.ifError = True
            error.password = 'This is a invalid password'
        elif not ifTwoPasswordSame(password,pwAgain):
            error.ifError = True
            error.pwAgain = 'Make sure this is the same with above'
        if not input_validation(('email',email)):
            error.ifError = True
            error.email ='This is a invalid email'
        if not role:
            error.roleError = 'Role is required'

        if not error.ifError:
            paraTuple = (username,password,email,role)
            addStudent(paraTuple)
            self.redirect('/welcome?username='+username+'&password='+password)
        else:
            self.render_page(username= username, email= email, role=role, error=error)








app = webapp2.WSGIApplication([('/signup',signupHandler)],debug=True)

