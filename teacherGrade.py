__author__ = 'Steven_yang'

import os
import webapp2
import urllib2
from xml.dom import minidom
import time

from google.appengine.ext.webapp import template

from dataTable import Team
from dataTable import teacherScore
from dataTable import cookieUsername

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def googleMap_image(team):
    if team:
        markers = '&'.join('markers=%s,%s' %(upload.coordinate.lat,upload.coordinate.lat)
                            for upload in team.works)
        return GMAPS_URL + markers

def getScreenShots(url):
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return

    if content:
        parseContent = minidom.parseString(content)
        data = parseContent.getElementsByTagName('data')
        if data:
            imageURL =  data[0].childNodes[27].\
            childNodes[3].childNodes[7].\
            childNodes[7].childNodes[0].nodeValue
            return imageURL

def returnScreenShots(screenShotList):
    imageList = []
    for item in screenShotList:
        imageList.append(getScreenShots(item))
        time.sleep(1)
    return imageList


class teacherGradeHandler(webapp2.RequestHandler):
    def get(self):
        self.render_page()
    def render_page(self):
        form = os.path.join(os.path.dirname(__file__),'teacher/teachergrade.html')
        templateValues = {}
        assignmentName = self.request.get('assignmentName')
        teamID = int(self.request.get('teamID'))
        team = Team.all().filter('teamID = ',teamID).get()
        user_cookie = self.request.cookies.get('user')
        user = cookieUsername(user_cookie)
        templateValues['user'] = user


        templateValues['assignmentName'] = assignmentName
        templateValues['team'] = team
        googleMap = None
        googleMap = googleMap_image(team)
        templateValues['googleMap'] = googleMap


        screenShotList = []
        for work in team.works:
            if work.assignmentName == assignmentName:
                screenShotList.append(work.testResultURL)
        imageList = returnScreenShots(screenShotList)
        templateValues['imageList'] = imageList
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)
    def post(self):
        assignmentName = self.request.get('assignmentName')
        teamID = int(self.request.get('teamID'))
        teamScore = float(self.request.get('teamScore'))
        teacherComment = self.request.get('teacherComment')
        teacherScore(teamID,assignmentName,teamScore,teacherComment)
        self.render_page()



app = webapp2.WSGIApplication([('/teacher/grade',teacherGradeHandler)],debug=True)