__author__ = 'Steven_yang'

import os
import re


import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from dataTable import createDefaultUsers

regexDic = { 'username':r'^[a-zA-Z0-9_-]{3,20}$',
             'password':r'^.{3,20}$',
             }

def input_validation(tuple):
    REGEX = re.compile(regexDic[tuple[0]])
    return REGEX.match(tuple[1])

def user_validation(username,password):
    user = db.GqlQuery("SELECT * FROM Users WHERE name = :1 AND password = :2"
        ,username,password)
    result = user.get()
    template_values = {}
    if result:
        template_values['error'] = 'no'
        template_values['user'] = result
        #template_values['userKey'] = user
    else:
        template_values['error'] = 'yes'
    return template_values


class loginHandler(webapp2.RequestHandler):
    """
    user login handler
    """
    def render_page(self, username='',errors=None):
        form = os.path.join(os.path.dirname(__file__),'templates/login.html')
        template_values = {}
        template_values['username'] = username
        if errors:
            template_values['username'] = username
            if 'usernameError' in errors:
                template_values['usernameError'] = errors['usernameError']
            if 'passwordError' in errors:
                template_values['passwordError'] = errors['passwordError']
        renderForm = template.render(form,template_values)
        self.response.out.write(renderForm)


    def get(self):
        createDefaultUsers()
        self.render_page()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        errors = {}
        if not input_validation(tuple=('username',username)):
            errors['usernameError'] = 'username is invalid'
        if not input_validation(tuple=('password',password)):
            errors['passwordError'] = 'password is invalid'
        if errors:
            self.render_page(username=username,errors=errors)
        else:
            #templateValues = user_validation(username,password)
            self.redirect('/welcome?username='+username+'&password='+password)


class welcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get('username')
        password = self.request.get('password')
        templateValues = user_validation(username,password)
        form = os.path.join(os.path.dirname(__file__),'templates/welcome.html')
        if templateValues['error'] == 'no':
            if templateValues['user'].role == 'teacher':
                self.redirect('/teacher?username='+templateValues['user'].name)
            else:
                templateValues['userKey'] = templateValues['user'].key()
                renderForm = template.render(form,templateValues)
                self.response.out.write(renderForm)
        else:
            renderForm = template.render(form,templateValues)
            self.response.out.write(renderForm)


app = webapp2.WSGIApplication([('/login', loginHandler),
    ('/welcome',welcomeHandler)],
    debug=True)

def main():

    run_wsgi_app(app)

if __name__ == "__main__":
    main()