__author__ = 'Steven_yang'

import os
import webapp2
import urllib2
#import httplib2
import random
import time

from xml.dom import minidom
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from dataTable import createUploadWork
from dataTable import cookieUsername

IP_URL = 'http://api.hostip.info/?ip='
WEBPAGETEST = 'http://www.webpagetest.org/runtest.php?f=xml&k=6301c5ec512b446e8c4315e9e1d6dd81&url='




def getCoordinates(ip):
    ip = '4.4.4.2'
    url = IP_URL+ip
    content = None

    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return

    if content:
        parseContent = minidom.parseString(content)
        coordinate = parseContent.getElementsByTagName('gml:coordinates')
        if coordinate and coordinate[0].childNodes[0].nodeValue:
            lon,lat = coordinate[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat,lon)

def getTestURL(url):
    request = random.randint(100,10000)

    URL = WEBPAGETEST + url + '&r=' + str(request)
    #return URL
    content = None
    urlRequest = urllib2.Request(URL)
    try:
        content = urllib2.urlopen(urlRequest)
    except urllib2.URLError:
        return 'noOpen'
    content = content.read()
    if content:
        parseContent = minidom.parseString(content)
        xmlResultNode = parseContent.getElementsByTagName('xmlUrl')
        if xmlResultNode and xmlResultNode[0].childNodes[0].nodeValue:
            getTestResult = xmlResultNode[0].childNodes[0].nodeValue + '?r=' + str(request)
            return getTestResult
        else:
            return 'noNode'
    else:
        return 'noContent'


class uploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.render_page()

    def render_page(self,uploadMessage='',error=''):
        self.response.out.write(repr(getCoordinates(self.request.remote_addr)))
        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name

        assignmentName = self.request.get('assignmentName')
        upload_url = blobstore.create_upload_url('/upload?assignmentName='+assignmentName+'&username='+username)
        form = os.path.join(os.path.dirname(__file__),'templates/upload.html')
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        templateValues['upload_url'] = upload_url
        templateValues['uploadMessage'] = uploadMessage
        templateValues['error'] = error
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)


    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form



        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        assignmentName = self.request.get('assignmentName')
        title = self.request.get('uploadTitle')
        version = self.request.get('uploadVersion')
        description = self.request.get('uploadDescription')
        URL = self.request.get('URL')

        if title and version and description and URL:
            #Get the user coordinate information
            coordinate = getCoordinates(self.request.remote_addr)
            testResultURL = getTestURL(URL)
            paraDic = {
                'username': username,
                'assignmentName':assignmentName,
                'title':title,
                'version':version,
                'description':description,
                #'sourceCode':blob_info.key(),
                'URL':URL,
                #'filename':blob_info.filename
            }
            if upload_files:
                blob_info = upload_files[0]
                paraDic['sourceCode'] = blob_info.key()
                paraDic['filename'] = blob_info.filename
            else:
                paraDic['sourceCode'] = None
                paraDic['filename'] = None
            if coordinate:
                paraDic['coordinate'] = coordinate
                #if testResultURL:
            paraDic['testResultURL'] = testResultURL


            if createUploadWork(paraDic):
                self.redirect('/student')
            else:
                self.render_page(uploadMessage='Bad luck! This assignment is expired!')
        else:
            self.render_page(error = 'No field can be empty!')




app = webapp2.WSGIApplication([('/upload',uploadHandler)],debug=True)