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
    lock = db.BooleanProperty(required=True)

class Users(db.Model):
    #reference = db.ReferenceProperty(Team,collection_name=teamMembers,required=False)
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    role = db.StringProperty(required=True, choices=set(['teacher','student','TA']))
    teamID = db.IntegerProperty(required=False)
    hasTeam = db.BooleanProperty()
    leader = db.BooleanProperty()

class Assignment(db.Model):
    reference = db.ReferenceProperty(Users, collection_name='assignments', required=True)
    assignmentName = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    #tag = db.StringProperty(required=True)
    receivers = db.StringListProperty(required= True)
    content = db.TextProperty()
    deadLine = db.DateTimeProperty(required=True)
    releaseTime = db.DateTimeProperty(auto_now_add=True)
    pubOrTeam = db.StringProperty(required=True)


class Tag(db.Model):
    #reference = db.ReferenceProperty(Assignment,collection_name='tags', required=True)
    tagName = db.StringProperty(required=True)
    tagAmount = db.IntegerProperty()

class AssignmentKey(db.Model):
    assignments = db.ReferenceProperty(Assignment,collection_name="tags",required=True)
    tags = db.ReferenceProperty(Tag,collection_name="assignments",required=True)


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

def ifAssignmentNameOK(assignmentName):
    #team = db.GqlQuery("SELECT * FROM Team WHERE teamName = :1", teamname)
    result = db.GqlQuery("SELECT * FROM Assignment WHERE assignmentName = :1", assignmentName)
    return result.get()

def ifTagNameOK(tagName):
    result = db.GqlQuery("SELECT * FROM Tag WHERE tagName = :1", tagName)
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
    result = students.fetch(50)
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

def query_assigments():
    """
    return all assignments
    """
    assignments = Assignment.all().fetch(20)
    return assignments

def query_tags():
    """
    return all tags
    """
    tags = Tag.all().fetch(20)
    return tags

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
    if team and team.lock == True:
        return 'lock'
    elif  team and user:
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
        return 'successQuit'
    else:
        return 'fail'


def createTeam(username, teamName):
    userInfo = db.GqlQuery("SELECT * FROM Users WHERE name = :1", username)
    result = userInfo.get()
    if not result.hasTeam:
        if not ifTeamNameOK(teamName):
            now = datetime.now()
            teamID = int(str(now.hour)+str(now.minute)+str(now.second))
            teamMember = [username]
            new_Team = Team(teamName = teamName, teamID = teamID,
                            teamMember =teamMember,teamLeader = username,lock = False)

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
    #teamResult = db.GqlQuery("SELECT * FROM Team WHERE teamID = :1 AND lock = :2",teamID,False)
    if teamResult and teamResult.lock == True:
        return 'lock'

    elif  teamResult and userResult:
        userResult.teamID = int(teamID)
        userResult.hasTeam = True
        teamMember =teamResult.teamMember
        teamMember.append(username)
        teamResult.teamMember = teamMember
        teamResult.put()
        userResult.put()
    else:
        return 'fail'

def createAssignment(paraDictionary):
    creator = Users.all().filter('name = ',paraDictionary['username']).get()
    receivers = []
    if paraDictionary['receiver'] == 'public':
        users = Users.all()
        for user in users:
            receivers.append(user.name)
    if paraDictionary['receiver'] == 'team':
        teams = Team.all()
        for team in teams:
            receivers += team.teamMember
    new_assignment = Assignment(
        reference=creator,
        assignmentName=paraDictionary['assignmentName'],
        author = creator.name,
        receivers = receivers,
        content = paraDictionary['assignmentContent'],
        deadLine = paraDictionary['deadline'],
        pubOrTeam = paraDictionary['receiver']
    )
    new_assignment.put()
    for tagName in paraDictionary['tagNames']:
        tag = createTag(tagName)
        assignmentTag = AssignmentKey(assignments = new_assignment,tags = tag)
        assignmentTag.put()


def createTag(tagName):
    tag =  ifTagNameOK(tagName)
    if not tag:
        newTag = Tag(
            tagName = tagName,
            tagAmount = 1
        )
        newTag.put()
        return newTag
    else:
        tag.tagAmount += 1
        tag.put()
        return tag

def updateAssignment(assignmentName,deadLine,assignmentContent):
    assignment = Assignment.all().filter('assignmentName = ',assignmentName).get()
    assignment.deadLine = deadLine
    assignment.content = assignmentContent
    assignment.put()

def updateAssignmentTeam(username,quitOrJoin):
    if quitOrJoin == 'join':
        assignments = db.GqlQuery("SELECT * FROM Assignment WHERE pubOrTeam = :1",'team').fetch(20)
        for assignment in assignments:
            assignment.receivers.append(username)
            assignment.put()
    if quitOrJoin == 'quit':
        assignments = db.GqlQuery("SELECT * FROM Assignment WHERE pubOrTeam = :1",'team').fetch(20)
        for assignment in assignments:
            assignment.receivers = filter(lambda a: a!= username,assignment.receivers)
            assignment.put()


def lockTeam(teamID):
    #team = Team.all().filter('teamID = ',teamID).get()
    team = db.GqlQuery("SELECT * FROM Team WHERE teamID = :1",int(teamID)).get()
    team.lock = True
    team.put()



