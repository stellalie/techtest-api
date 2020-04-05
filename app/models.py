from . import db

people_friends_table = db.Table('people_friends',
                                db.Model.metadata,
                                db.Column('person_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
                                db.Column('friend_id', db.Integer, db.ForeignKey('people.id'), primary_key=True))


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return '<Company {}>'.format(self.name)


class Person(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String)
    has_died = db.Column(db.Boolean)
    balance = db.Column(db.String)  # Ideally this need to be stored in cents (not floats ofc)
    picture = db.Column(db.String)
    age = db.Column(db.Integer)
    eye_colour = db.Column(db.String)
    name = db.Column(db.String)
    gender = db.Column(db.String)  # This would be some sort of enum
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref=db.backref('people', lazy='select'))
    username = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    about = db.Column(db.Text)
    registered = db.Column(db.DateTime)
    tags = db.Column(db.JSON)
    friends = db.relationship('Person', secondary=people_friends_table,
                              primaryjoin=id == people_friends_table.c.person_id,
                              secondaryjoin=id == people_friends_table.c.friend_id,
                              lazy='select'
                              )
    greeting = db.Column(db.Text)
    fruits = db.Column(db.JSON)
    vegetables = db.Column(db.JSON)

    def __repr__(self):
        return '<Person {}>'.format(self.name)
