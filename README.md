# Installation

The application is tested using Python 3 thats on my machine, ie:
```
(local) ~/W/techtest-api ❯❯❯ python --version
Python 3.7.1
```

Install deps, build DB with data and run the server
```
virtualenv -p `which python3` .venv/local
source .venv/local/bin/activate
pip install -r requirements.txt

export APP_SETTINGS=config.development
python migrate.py
python manage.py runserver
```

To run integration tests
```
pytest
```

(Optional) To load the DB with data in different JSON, replace the JSON file in `resources/*.json`, then re-recreate
```
rm -f resources/db.sqlite3
python migrate.py
```

# Implementation Notes

The simplified implementation is a quick POC to show my API design and coding skills within max a day constraint thus many production ready essentials are being left out intentionally. Happy to discuss how I would further approach these in person instead

* Limited data cleansing and validation strategies (Looking at the existing data friendship does not seems to be bi-directional so I leave it as it is, not sure whats with self-referencing friends (?), company id from the data seems off by 1 which I fixed upon import, balance dollars could be stored in cents to avoid floating precision issues which I ignore for now, gender can be enum, email/url/address/phone/tags validations are skipped, and many more that I might miss)
* Limited structured validation on request parameter query, ie. can create an abstraction to check type, whether to allow multi input and validate each values shall be numbers (ie. id=1,2,3), map auto split string to list of ints, provide consistent error messages, etc
* Limited performance strategies. I simply ensure no unnecessary multi selects slipped through by watching closely the number of performed by the ORM in the log (ie. I skipped considerations regarding lazy loading techniques, assigning column indexes for frequently used searches by column, separate tables for foods, tags, pagination, etc)
* Limited testing strategies. I did simple integration test hitting the dev DB directly in which ideally we should use mock datas, various scenarios are not tested and it is lacking due to time constraints
* No configuration setup for production (ie. debug mode is by default, debug log is on as well)
* No automated API documentation (Swagger equivalent)
* No API version system
* No DB migration strategies
* No logging, metrics and alerting strategies
* No response caching strategies (and possibly consider cache lock mechanism to avoid request swarm in a multi process environment)
* No response caching header considerations (ie. ETag, Last-Modified)
* No rate limiting strategies
* No pagination strategies
* No authentication
* No security consideration, ie. SSL, exposing database index as id to the public, etc
* No deployment plan (deploy to a server instance as it is or on an alternative vendor dependent approach with AWS serverless offering combo: Route53, API Gateway, Lambda, ElasticCache, RDS)

Design decisions (KISS)
* I took a simplistic and avoid over engineering approach on various decisions due to combination of time constraints, my value lies upon balance between too much assumptions and to get further analysis on requirements, and also the fact I like to maintain as little features as possible
* Sqlite is used for local DB as it requires no installation and simple to setup
* GraphQL is not considered as REST is simpler, also the requirements doesn't seems to indicate an ultimate need for it
* Fav food and tags are stored as JSON object in the column for faster access and simplicity as the requirements doesn't seems to indicate a need for filtering by it. For limited distant future, the Paranuara government can rely on both Sqlite and Postgres support search for JSON object in columns for that would support low use API load until proven otherwise
* By default all the DB fields in the table (no join) are displayed, `include` functionality is implemented in people endpoint to fit the exact requirements. This a naive approach for simplicity since the field inclusions are done on the serialisation side thus does not actually increase query performance however improve request load size 

# Route design as per feature requirements

## Available routes
I purposely kept the routes flat instead of adding /companies/{id}/employees

* `GET /companies` allowing filtering by `?name={name}`
* `GET /companies/{id}`
* `GET /people` allowing filtering by `?company_id={id}`, `?id={id,id,..}`, `?username={?}` and use include to only display certain fields `?includes=username,age,fruits,vegetables,..`
* `GET /people/{id}` and also allow include fields `?includes=username,age,...`
* `GET /special_friends?person_id={id,id,..}`

Possible includes fields for people endpoint:
"id", "username", "guid", "has_died", "balance", "picture", "age", "eye_colour", "name", "gender", "company_id", "phone", "address", "about", "registered", "tags", "greeting", "fruits", "vegetables",

I'd argue some requirements has to be retrieved via multiple GET request as we want to keep each endpoint with no nested resources. More advanced API practices could be considered, ie. links to related resources, embed resources functionality, etc, but I'd prefer keep things simple for demo

There is no username field in the data, more clarification is needed. For now, I made an assumption that it would be the `email` field

## Requirements

Given a company, the API needs to return all their employees. Provide the appropriate solution if the company does not have any employees.
* The /companies endpoint could be useful if needed to get company id by name
* If the company does not have any employees `GET /people?company_id={id}` would simply return a 200 OK with an empty list
```
GET /companies?name=TECHTRIX
GET /people?company_id=7
```
```
(local) ~/W/techtest-api ❯❯❯ curl "http://localhost:5000/companies?name=TECHTRIX"
[{"id":7,"name":"TECHTRIX"}]
(local) ~/W/techtest-api ❯❯❯ curl "http://localhost:5000/people?company_id=7" | json_pp

(redacted - content too large)
```

Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common which have brown eyes and are still alive.
* The /people endpoint could be useful to get people id by name and email (more can potentially be included)
* The logic "common friends with brown eyes and still alive" is be hardcoded under the term "special" for simplicity given the current requirements instead of implementing flexible filter
* The `/special_friends` endpoint simply outputs a list of user ids per relationship as information about people can be derived at `/people` endpoint
```
GET /people?username=garzariley@earthmark.com
GET /special_friends?person_id=20,4
GET /people?id=20,4&includes=name,age,address,phone
```
```
(local) ~/W/techtest-api ❯❯❯ curl "http://localhost:5000/special_friends?person_id=20,4"
[1,4]
(local) ~/W/techtest-api ❯❯❯ curl "http://localhost:5000/people?id=1,4&includes=name,age,address,phone" | json_pp
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   236  100   236    0     0  10260      0 --:--:-- --:--:-- --:--:-- 10260
[
   {
      "address" : "492 Stockton Street, Lawrence, Guam, 4854",
      "phone" : "+1 (893) 587-3311",
      "age" : 60,
      "name" : "Decker Mckenzie"
   },
   {
      "age" : 62,
      "name" : "Mindy Beasley",
      "address" : "628 Brevoort Place, Bellamy, Kansas, 2696",
      "phone" : "+1 (862) 503-2197"
   }
]
```

Given 1 people, provide a list of fruits and vegetables they like. This endpoint must respect this interface for the output: `{"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}`
```
GET /people/{id}?includes=username,age,fruits,vegetables
```
```
(local) ~/W/techtest-api ❯❯❯ curl "http://localhost:5000/people/10?includes=username,age,fruits,vegetables" | json_pp                                                                                             ⏎
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   120  100   120    0     0   5000      0 --:--:-- --:--:-- --:--:--  5000
{
   "age" : 30,
   "vegetables" : [
      "cucumber"
   ],
   "username" : "kathleenclarke@earthmark.com",
   "fruits" : [
      "apple",
      "banana",
      "strawberry"
   ]
}
```

====


# Paranuara Challenge
Paranuara is a class-m planet. Those types of planets can support human life, for that reason the president of the Checktoporov decides to send some people to colonise this new planet and
reduce the number of people in their own country. After 10 years, the new president wants to know how the new colony is growing, and wants some information about his citizens. Hence he hired you to build a rest API to provide the desired information.

The government from Paranuara will provide you two json files (located at resource folder) which will provide information about all the citizens in Paranuara (name, age, friends list, fruits and vegetables they like to eat...) and all founded companies on that planet.
Unfortunately, the systems are not that evolved yet, thus you need to clean and organise the data before use.
For example, instead of providing a list of fruits and vegetables their citizens like, they are providing a list of favourite food, and you will need to split that list (please, check below the options for fruits and vegetables).

## New Features
Your API must provides these end points:
- Given a company, the API needs to return all their employees. Provide the appropriate solution if the company does not have any employees.
- Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common which have brown eyes and are still alive.
- Given 1 people, provide a list of fruits and vegetables they like. This endpoint must respect this interface for the output: `{"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}`

## Delivery
To deliver your system, you need to send the link on GitHub. Your solution must provide tasks to install dependencies, build the system and run. Solutions that does not fit this criteria **will not be accepted** as a solution. Assume that we have already installed in our environment Java, Ruby, Node.js, Python, MySQL, MongoDB and Redis; any other technologies required must be installed in the install dependencies task. Moreover well tested and designed systems are one of the main criteria of this assessement 

## Evaluation criteria
- Solutions written in Python would be preferred.
- Installation instructions that work.
- During installation, we may use different companies.json or people.json files.
- The API must work.
- Tests

Feel free to reach to your point of contact for clarification if you have any questions.