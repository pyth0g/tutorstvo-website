from flask_login import UserMixin
from extensions import db
from resources import formatTitle

class Subject(db.Model):
    __bind_key__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tutors = db.Column(db.String(100), nullable=False)
    learning_resources = db.Column(db.String(1000), default='', nullable=False)

    def get_tutors(self) -> list:
        return list(filter(None, self.tutors.split(',')))

    def get_learning_resources(self) -> list:
        return list(filter(None, self.learning_resources.split(',')))

class Lesson(db.Model):
    __bind_key__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(200), default='General', nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    classroom = db.Column(db.String(10), nullable=False)
    min = db.Column(db.Integer)
    datetime = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    filled = db.Column(db.Integer, default=0)

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def isInGroup(self, group: str) -> bool:
        return group in self.get_groups()

    def get_tutors(self, subject_db: Subject) -> list:
        return subject_db.query.filter_by(name=self.subject).first().get_tutors()

    def tutors(self, subject_db: Subject) -> str:
        return ', '.join(list(map(formatTitle, self.get_tutors(subject_db))))

class User(UserMixin, db.Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(200), default='General', nullable=False) 
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user')
    selected_subjects = db.Column(db.String(200), default='', nullable=False)
    email = db.Column(db.String(100), default='', nullable=False)
    unverified_email = db.Column(db.String(100), default='', nullable=False)
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)

    def get_groups(self) -> list:
        groups_str = self.groups

        return groups_str.split(',')

    def is_admin(self):
        return self.role == 'admin'

    def is_tutor(self):
        return self.role == 'tutor'

    def tutor_for(self, subject: Subject):
        subjects = []
        for subject in subject.query.all():
            for i in subject.get_tutors():
                if i.lower() == self.username.lower():
                    subjects.append(subject.name)

        return subjects

    def subjects(self, subject: Subject):
        subjects = []

        if self.is_admin():
            subjects = list(map(lambda x: x.name, subject.query.all()))

        elif self.is_tutor():
            for subject in subject.query.all():
                for i in subject.get_tutors():
                    if i.lower() == self.username.lower():
                        subjects.append(subject.name)

        return subjects

    def getSelectedSubjects(self):
        return list((filter(None, self.selected_subjects.split(','))))

class Group(db.Model):
    __bind_key__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
