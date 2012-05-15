__author__ = 'Steven_yang'

import os
import webapp2
import urllib2
from xml.dom import minidom
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from dataTable import createUploadWork
from dataTable import cookieUsername

IP_URL = 'http://api.hostip.info/?ip='

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



class uploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.render_page()

    def render_page(self,uploadMessage=''):
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
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)


    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]

        user_cookie = self.request.cookies.get('user')
        username = cookieUsername(user_cookie).name
        assignmentName = self.request.get('assignmentName')
        title = self.request.get('uploadTitle')
        version = self.request.get('uploadVersion')
        description = self.request.get('uploadDescription')
        URL = self.request.get('URL')
        #Get the user coordinate information
        coordinate = getCoordinates(self.request.remote_addr)

        paraDic = {
            'username': username,
            'assignmentName':assignmentName,
            'title':title,
            'version':version,
            'description':description,
            'sourceCode':blob_info.key(),
            'URL':URL,
            'filename':blob_info.filename
        }
        if coordinate:
            paraDic['coordinate'] = coordinate


        if createUploadWork(paraDic):
            self.redirect('/student')
        else:
            self.render_page(uploadMessage='Bad luck! This assignment is expired!')



app = webapp2.WSGIApplication([('/upload',uploadHandler)],debug=True)