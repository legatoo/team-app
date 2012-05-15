__author__ = 'Steven_yang'

import os
import webapp2

from google.appengine.ext.webapp import template

from dataTable import Team
from dataTable import teacherScore

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def googleMap_image(team):
    if team:
        markers = '&'.join('markers=%s,%s' %(upload.coordinate.lat,upload.coordinate.lat)
                            for upload in team.works)
        return GMAPS_URL + markers


class teacherGradeHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        assignmentName = self.request.get('assignmentName')
        teamID = int(self.request.get('teamID'))
        team = Team.all().filter('teamID = ',teamID).get()


        form = os.path.join(os.path.dirname(__file__),'templates/teachergrade.html')
        templateValues = {}
        templateValues['assignmentName'] = assignmentName
        templateValues['team'] = team
        googleMap = None
        googleMap = googleMap_image(team)
        templateValues['googleMap'] = googleMap
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)
    def post(self):
        assignmentName = self.request.get('assignmentName')
        teamID = int(self.request.get('teamID'))
        teamScore = float(self.request.get('teamScore'))
        teacherComment = self.request.get('teacherComment')
        teacherScore(teamID,assignmentName,teamScore,teacherComment)
        self.render_page()



app = webapp2.WSGIApplication([('/teachergrade',teacherGradeHandler)],debug=True)