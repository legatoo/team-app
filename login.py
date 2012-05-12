__author__ = 'Steven_yang'

import os
import re


import webapp2

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from dataTable import createDefaultUsers
from dataTable import user_validation

regexDic = { 'username':r'^[a-zA-Z0-9_-]{3,20}$',
             'password':r'^.{3,20}$',
             'studentID':r'^[0-9]{8,10}$',
             'email':r'^[\S]+@[\S]+\.[\S]+$'
             }

def input_validation(tuple):
    REGEX = re.compile(regexDic[tuple[0]])
    return REGEX.match(tuple[1])

class loginHandler(webapp2.RequestHandler):
    """
    user login handler
    """
    def render_page(self, username='',haveUser='yes', errors=None):
        form = os.path.join(os.path.dirname(__file__),'templates/login.html')
        template_values = {}
        if haveUser == 'no':
            template_values['haveUser'] = haveUser
        else:
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
            templateValues = user_validation(username,password)
            if templateValues['haveUser'] == 'yes':
                if templateValues['user'].role == 'teacher':
                    self.redirect('/teacher?username=' + username)
                if templateValues['user'].role == 'student':
                    self.redirect('/student?username=' + username)
            if templateValues['haveUser'] == 'no':
                self.render_page(haveUser='no')


app = webapp2.WSGIApplication([('/login', loginHandler)],debug=True)

def main():

    run_wsgi_app(app)

if __name__ == "__main__":
    main()