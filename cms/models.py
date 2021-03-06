from enum import unique

from sqlalchemy.orm import backref
# from cms.core.views import index
from cms import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


course_helper=db.Table('course_helper',
                        db.Column('user_id',db.Integer,db.ForeignKey('users.id')),
                        db.Column('course_id',db.Integer,db.ForeignKey('courses.id'))
                        )
branch_helper=db.Table('branch_helper',
                        db.Column('course_id',db.Integer,db.ForeignKey('courses.id')),
                        db.Column('branch_id',db.Integer,db.ForeignKey('branches.id'))
                        )



class Branch(db.Model):
    __tablename__='branches'
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    students=db.relationship('User',backref='branch')
    professors = db.relationship('Professor', backref='branch')
    def __init__(self,name):
        self.name = name
    def __repr__(self) -> str:
        return self.name

class User(db.Model,UserMixin):
    __tablename__='users'
    name=db.Column(db.String(),nullable=False)
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    year=db.Column(db.Integer())
    branch_id=db.Column(db.Integer,db.ForeignKey('branches.id'))
    courses = db.relationship('Course', secondary=course_helper,
                              backref=db.backref('students'))
    submissions=db.relationship('Submission',backref='user')
    requests=db.relationship('Request',backref='user')
    def __init__(self,name,email,password,year,branch_id):
        self.name=name
        self.email=email
        self.password_hash=generate_password_hash(password)
        self.year=year
        self.branch_id=branch_id

    def to_dict(self):
        return {
            'id': self.id,
            'Name': self.name,
            'E-Mail': self.email,
            'Year': self.year,
            'Branch': self.branch.name}

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


    @property
    def requested_courses(self):
        req_courses=[]
        for request in self.requests:
            req_courses.append(request.course)
        return req_courses

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    details = db.Column(db.String())
    prof_id = db.Column(db.Integer, db.ForeignKey(
        'professors.id'), nullable=False)
    course_code = db.Column(db.String(), unique=True)
    branches=db.relationship('Branch',secondary=branch_helper,backref=db.backref('courses'))
    can_apply=db.Column(db.Boolean)
    courseNotes = db.relationship(
        'courseNote', backref='Course', order_by="desc(courseNote.time)")
    assignments = db.relationship(
        'Assignment', backref='Course', order_by="desc(Assignment.time)")
    requests = db.relationship('Request', backref='course')
    def __init__(self, name, course_code, details, prof_id,can_apply,):
        self.name = name
        self.course_code = course_code
        self.details = details
        self.prof_id = prof_id
        self.can_apply=can_apply


class Professor(db.Model, UserMixin):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(64), unique=True, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    courses = db.relationship('Course', backref='professor', lazy=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, name, email, password, branch_id):
        self.email = email
        self.name = name
        self.password_hash = generate_password_hash(password)
        self.branch_id = branch_id

class courseNote(db.Model):
    __tablename__='coursenotes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    details = db.Column(db.String())
    time=db.Column(db.DateTime,nullable=False,default=datetime.now)
    attachments=db.relationship('Attachment',backref='coursenote')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    def __init__(self,title,details,course_id):
        self.title=title
        self.details=details
        self.course_id=course_id
class Assignment(db.Model):
    __tablename__='assignments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    details = db.Column(db.String())
    time=db.Column(db.DateTime,nullable=False,default=datetime.now)
    attachments=db.relationship('Attachment',backref='assignment')
    submissions=db.relationship('Submission',backref='assignment')
    deadline=db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    def __init__(self,title,details,deadline,course_id):
        self.title=title
        self.details=details
        self.deadline=deadline
        self.course_id=course_id

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    ext = db.Column(db.String(10))
    link = db.Column(db.String())
    coursenote_id=db.Column(db.Integer,db.ForeignKey('coursenotes.id'))
    assignment_id=db.Column(db.Integer,db.ForeignKey('assignments.id'))
    submission_id=db.Column(db.Integer,db.ForeignKey('submission.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))

    def __init__(self,name,ext,link,coursenote_id=None,assignment_id=None,submission_id=None,request_id=None):
        self.name=name
        self.ext=ext
        self.link=link
        self.coursenote_id=coursenote_id
        self.assignment_id=assignment_id
        self.submission_id=submission_id
        self.request_id=request_id


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    details = db.Column(db.String())
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    attachments = db.relationship('Attachment', backref='submissions')
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    def __init__(self, title, details, assignment_id,user_id):
        self.title = title
        self.details = details
        self.assignment_id = assignment_id
        self.user_id=user_id


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String())
    details = db.Column(db.String())
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    attachments = db.relationship('Attachment', backref='request')
    status=db.Column(db.Integer,default=0)
    def __init__(self,user_id,course_id,title,details):
        self.user_id=user_id
        self.course_id=course_id
        self.title=title
        self.details=details
    pass
