__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template

from dataTable import createTeam

class createdTeamHandler(webapp2.RequestHandler):
    pass



app = webapp2.WSGIApplication([('/createteam',createdTeamHandler)],debug=True)
