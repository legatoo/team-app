__author__ = 'Steven_yang'

from google.appengine.ext import db
from datetime import datetime


defaultUsers = [
    ('qingWANG','wang123456','wangqing@saad.com','teacher'),
    ('stevenYANG','123456','yifan@gmail.com','student'),
    ('jingZHU','zhu123456','zhujing@example.com','student'),
    ('conghuiHE','he123456','conghui@where.com','student'),
    ('lianDUAN','duan123456','duanlian@what.com','student'),
    ('xinHAO','hao123456','haoxin@example.com','student')
]

class Team(db.Model):
    teamName = db.StringProperty(required=True)
    teamID = db.IntegerProperty(required=True)
    teamLeader = db.StringProperty(required=True)
    teamMember = db.StringListProperty(required=True)

class Users(db.Model):
    #reference = db.ReferenceProperty(Team,collection_name=teamMembers,required=False)
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    role = db.StringProperty(required=True, choices=set(['teacher','student','TA']))
    teamID = db.IntegerProperty(required=False)
    hasTeam = db.BooleanProperty()
    leader = db.BooleanProperty()

def createDefaultUsers():
    """
    create default user table
    """
    user_count = Users.all().count(1)
    if user_count == 0:
        for user in defaultUsers:
            new_user = Users( name = user[0], password = user[1],
                email = user[2], role = user[3],  hasTeam = False, leader = False)
            new_user.put()

def addStudent(paraTuple):
    new_user = Users(name = paraTuple[0], password = paraTuple[1],
        email = paraTuple[2], role = paraTuple[3], leader = False, hasTeam = False)
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

def ifTeamNameOK(teamname):
    #team = db.GqlQuery("SELECT * FROM Team WHERE teamName = :1", teamname)
    result = db.GqlQuery("SELECT * FROM Team WHERE teamName = :1", teamname)
    return result.get()

def ifHasTeam(username):
    user = db.GqlQuery("SELECT * FROM Users where name = :1", username)
    result = user.get()
    return result.hasTeam

def query_students():
    """
    return all students
    """
    students = db.GqlQuery("SELECT * FROM Users WHERE role = :1 ORDER BY teamID DESC",'student')
    result = students.fetch(10)
    if result:
        return result
    else:
        return None

def query_teams():
    """
    return all teams
    """
    teams = Team.all().fetch(15)
    return teams

def returnStuANDTeam(username):
    #user = db.GqlQuery("SELECT * FROM Users WHERE name = :1",username)
    #fetchUser = user.get()
    #teamID =fetchUser.teamID
    #members = db.GqlQuery("SELECT * FROM Users WHERE teamID = :1",teamID)
    #fetchMembers = members.fetch(10)
    team = db.GqlQuery("SELECT * FROM Team WHERE teamMember = :1",username)
    fetchTeam = team.get()
    teamID = fetchTeam.teamID
    members = db.GqlQuery("SELECT * FROM Users WHERE teamID = :1",teamID)
    fetchMembers = members.fetch(10)
    return (fetchMembers,fetchTeam)


def delete_student(studentName):
    student = db.GqlQuery("SELECT * FROM Users WHERE name = :1",studentName)
    result = student.get()
    #key = result.getkey()
    db.delete(result)

def quitTeam(username):
    team = db.GqlQuery("SELECT * FROM Team WHERE teamMember = :1",username).get()
    user = Users.all().filter('teamID = ', team.teamID).get()
    if team and user:
        if len(team.teamMember) == 1:
            team.delete()
            user.hasTeam = False
            user.teamID = 0
            user.leader = False
            user.put()

        else:
            members = filter(lambda a: a!= username,team.teamMember)
            team.teamMember = members
            user.hasTeam = False
            user.teamID = 0
            
            if user.leader == True:
                user.leader = False
                nextUser = Users.all().filter('name = ',members[0]).get()
                nextUser.leader = True
                team.teamLeader = nextUser.name
                nextUser.put()
            user.put()
            team.put()
        return True
    else:
        return False




def createTeam(username, teamName):
    userInfo = db.GqlQuery("SELECT * FROM Users WHERE name = :1", username)
    result = userInfo.get()
    if not result.hasTeam:
        if not ifTeamNameOK(teamName):
            now = datetime.now()
            teamID = int(str(now.hour)+str(now.minute)+str(now.second))
            teamMember = [username]
            new_Team = Team(teamName = teamName, teamID = teamID,
                            teamMember =teamMember,teamLeader = username)

            new_Team.put()
            result.hasTeam = True
            result.leader = True
            result.teamID = teamID
            result.put()
            return 'success'
        else:
            return 'teamExisted'
    else:
        return 'hadTeam'

def addMember(teamID,username):
    user = db.GqlQuery("SELECT * FROM Users WHERE name =:1", username)
    userResult = user.get()
    teamID = int(teamID)

    teamResult = Team.all().filter('teamID = ',teamID).get()

    if teamResult and userResult:
        userResult.teamID = int(teamID)
        userResult.hasTeam = True
        teamMember =teamResult.teamMember
        teamMember.append(username)
        teamResult.teamMember = teamMember
        teamResult.put()
        userResult.put()
    else:
        return 'fail'




