import unittest

from app import app, db


class RoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = db

    def assertIsList(self, response):
        self.assertEqual(200, response.status_code)
        self.assertIs(list, type(response.json))
        return response.json

    def assertIsSingle(self, response):
        self.assertEqual(200, response.status_code)
        self.assertIs(dict, type(response.json))
        return response.json

    # /companies endpoint tests
    def test_list_companies(self):
        self.assertIsList(self.app.get('/companies'))

    def test_list_companies_by_name(self):
        data = self.assertIsList(self.app.get('/companies?name=STRALUM'))
        self.assertEqual(99, data[0]['id'])
        self.assertEqual('STRALUM', data[0]['name'])

    def test_get_company(self):
        data = self.assertIsSingle(self.app.get('/companies/99'))
        self.assertEqual(99, data['id'])
        self.assertEqual('STRALUM', data['name'])

    def test_get_non_existant_company(self):
        response = self.app.get('/companies/100')
        self.assertEqual(404, response.status_code)

    # /people endpoint tests
    def test_list_people(self):
        self.assertIsList(self.app.get('/people'))

    def test_get_person(self):
        data = self.assertIsSingle(self.app.get('/people/99'))
        self.assertEqual(99, data['id'])
        self.assertEqual('Deborah Browning', data['name'])

    # /special_friends endpoint tests
    def test_list_special_friends(self):
        data = self.assertIsList(self.app.get('/special_friends?person_id=20,1'))
        self.assertEqual(1, data[0])
