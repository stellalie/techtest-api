import json
from datetime import datetime
from app import db
from app.models import Company, Person, people_friends_table

COMPANIES_DATA = 'resources/companies.json'
PEOPLE_DATA = 'resources/people.json'
DB_FILE = 'resources/db.sqlite3'

# I read the whole JSON and hard code the fruits list here
FRUITS_LIST = ['banana', 'orange', 'strawberry', 'apple']


def load_companies_data():
    with open(COMPANIES_DATA, 'r') as f:
        companies = json.load(f)

    for company in companies:
        db.session.add(Company(
            id=company['index'],
            name=company['company'])
        )
    db.session.commit()


def load_people_data():
    with open(PEOPLE_DATA, 'r') as f:
        people = json.load(f)

    # Load people
    friends = []
    for person in people:
        db.session.add(Person(
            id=person['index'],
            guid=person['guid'],
            has_died=person['has_died'],
            balance=person['balance'],
            picture=person['picture'],
            age=person['age'],
            eye_colour=person['eyeColor'],
            name=person['name'],
            gender=person['gender'],
            company_id=(person['company_id'] - 1),
            username=person['email'],
            phone=person['phone'],
            address=person['address'],
            about=person['about'],
            registered=datetime.strptime(person['registered'], '%Y-%m-%dT%H:%M:%S %z').date(),
            friends=[],
            tags=person['tags'],
            greeting=person['greeting'],
            fruits=[x for x in person['favouriteFood'] if x in FRUITS_LIST],
            vegetables=[x for x in person['favouriteFood'] if x not in FRUITS_LIST],
        ))
        # Store friends in tuple for later loading
        for friend in person['friends']:
            friends.append((person['index'], friend['index']))

    # Tried to count tuple occurrence ignoring order, we found out that friend relationship is not two way.
    # Thus, no cleaning necessary
    # from collections import Counter
    # counter = Counter(tuple(sorted(f)) for f in friends)
    # print(counter)

    # Load people friends relationship (Bulk inserts so its faster)
    data = [dict(zip(('person_id', 'friend_id'), x)) for x in friends]
    db.session.execute(people_friends_table.insert(), data)

    db.session.commit()


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    load_companies_data()
    load_people_data()
