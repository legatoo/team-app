__author__ = 'Steven_yang'

import os
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from dataTable import createUploadWork


class uploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.render_page()

    def render_page(self):
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        upload_url = blobstore.create_upload_url('/upload?assignmentName='+assignmentName+'&username='+username)
        form = os.path.join(os.path.dirname(__file__),'templates/upload.html')
        templateValues = {}
        username = self.request.get('username')
        templateValues['username'] = username
        templateValues['upload_url'] = upload_url
        renderPage = template.render(form,templateValues)
        self.response.out.write(renderPage)


    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        username = self.request.get('username')
        assignmentName = self.request.get('assignmentName')
        title = self.request.get('uploadTitle')
        version = self.request.get('uploadVersion')
        description = self.request.get('uploadDescription')
        #sourceCode = self.get_uploads('file')
        #bolb_info = sourceCode[0]
        paraDic = {
            'username': username,
            'assignmentName':assignmentName,
            'title':title,
            'version':version,
            'description':description,
            'sourceCode':blob_info.key()
        }
        createUploadWork(paraDic)
        self.redirect('/student?username='+username)



app = webapp2.WSGIApplication([('/upload',uploadHandler)],debug=True)