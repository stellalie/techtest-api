from flask import request, jsonify
from marshmallow import Schema, fields
from functools import reduce

from . import app, db
from app.models import Company, Person, people_friends_table


class CompanySchema(Schema):
    class Meta:
        fields = ("id", "name")


class PersonSchema(Schema):
    company = fields.Nested(CompanySchema, only=["id"])

    class Meta:
        fields = (
            "id",
            "username",
            "guid",
            "has_died",
            "balance",
            "picture",
            "age",
            "eye_colour",
            "name",
            "gender",
            "company_id",
            "phone",
            "address",
            "about",
            "registered",
            "tags",
            "greeting",
            "fruits",
            "vegetables",
        )


@app.errorhandler(404)
def not_found(Error=None):
    response = jsonify({
        'status': 404,
        'message': 'Not Found: ' + request.url,
    })
    response.status_code = 404
    return response


@app.errorhandler(500)
def bad_request(Error=None):
    response = jsonify({
        'status': 500,
        'message': 'Bad Request: ' + request.url,
    })
    response.status_code = 500
    return response


@app.route('/companies', methods=['GET'])
def list_companies():
    query = Company.query

    # Filter by name
    name = request.args.get("name")
    if name:
        query = query.filter(Company.name == name)

    return jsonify(CompanySchema(many=True).dump(query.all()))


@app.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get(company_id)
    if company is None:
        return not_found()
    return jsonify(CompanySchema().dump(company))


@app.route('/people', methods=['GET'])
def list_people():
    query = Person.query

    # Filter by id
    id = request.args.get("id")
    if id:
        ids = [int(i) for i in id.split(",")]
        query = query.filter(Person.id.in_(ids))
    # Filter by username
    username = request.args.get("username")
    if username:
        query = query.filter(Person.username == username)
    # Filter by company id
    company_id = request.args.get("company_id")
    if company_id:
        query = query.filter(Person.company_id == company_id)
    # Respect includes
    includes = request.args.get("includes")
    only = None
    if includes:
        only = [x for x in PersonSchema.Meta.fields if x in set(includes.split(","))]

    return jsonify(PersonSchema(many=True, only=only).dump(query.all()))


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get(people_id)
    if person is None:
        return not_found()

    # Respect includes
    includes = request.args.get("includes")
    only = None
    if includes:
        only = [x for x in PersonSchema.Meta.fields if x in set(includes.split(","))]

    return jsonify(PersonSchema(only=only).dump(person))


@app.route('/special_friends', methods=['GET'])
def list_special_friends():
    # Filter by id
    id = request.args.get("person_id")
    if id is None:
        return bad_request()
    ids = [int(i) for i in id.split(",")]

    # Query these common friends with `special` filter, ie. brown eyes and still alive
    people_friends = db.session.query(people_friends_table)\
        .join(Person, people_friends_table.c.friend_id == Person.id) \
        .filter(people_friends_table.c.person_id.in_(ids)) \
        .filter(Person.eye_colour == 'brown') \
        .filter(Person.has_died == False) \
        .all()

    # Get common element from list of people friends
    friends = {id: [] for id in ids}
    for person_id, friend_id in people_friends:
        friends[person_id].append(friend_id)
    common_friends_ids = list(reduce(lambda i, j: i & j, (set(x) for x in friends.values())))

    return jsonify(common_friends_ids)
