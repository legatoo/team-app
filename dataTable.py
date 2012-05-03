__author__ = 'Steven_yang'

from google.appengine.ext import db


defaultUsers = [
    ('qingWANG','wang123456','wangqing@saad.com','teacher'),
    ('stevenYANG','123456','yifan@gmail.com','student'),
    ('jingZHU','zhu123456','zhujing@example.com','student'),
    ('conghuiHE','he123456','conghui@where.com','student'),
    ('lianDUAN','duan123456','duanlian@what.com','student'),
    ('xinHAO','hao123456','haoxin@example.com','student')
]
class Users(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    role = db.StringProperty(required=True, choices=set(['teacher','student','TA']))
    teamID = db.IntegerProperty()
    leader = db.BooleanProperty()

class Team(db.Model):
    teamID = db.IntegerProperty(required=True)
    members = db.StringListProperty(required=True)
def createDefaultUsers():
    """
    create default user table
    """
    user_count = Users.all().count(1)
    if user_count == 0:
        for user in defaultUsers:
            new_user = Users(name = user[0], password = user[1],
                email = user[2], role = user[3], leader = False)
            new_user.put()


def user_validation(username,password):
    user = db.GqlQuery("SELECT * FROM Users WHERE name = :1 AND password = :2"
        ,username,password)
    result = user.get()
    template_values = {}
    if result:
        template_values['haveUser'] = 'yes'
        template_values['user'] = result
        #template_values['userKey'] = user
    else:
        template_values['haveUser'] = 'no'
    return template_values

def ifUsernameOK(username):
    result = db.GqlQuery("SELECT * FROM Users WHERE name = :1", username)
    if result:
        return False
    else:
        return True
