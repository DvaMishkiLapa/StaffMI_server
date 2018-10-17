# -*- coding: utf-8 -*-

import json
import unittest

import pymongo
from jsonschema import FormatChecker, ValidationError, validate

import db
from app import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.dbm = db.DBManager()
        self.dbm.add_users([
            {
                'email': 'test0@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            },
            {
                'email': 'test1@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            }
        ])
        self.dbm.add_projects([
            {'name': 'test0', 'deadline': '12-12-2020'},
            {'name': 'test1', 'deadline': '12-12-2020'}
        ])


    def tearDown(self):
        self.dbm.del_users([
            {'email': 'test0@test.ru'},
            {'email': 'test1@test.ru'},
            {'email': 'test2@test.ru'},
            {'email': 'test3@test.ru'}
        ])
        self.dbm.del_projects([
            {'name': 'test0'},
            {'name': 'test1'},
            {'name': 'test2'},
            {'name': 'test3'}
        ])


    def test_add_users(self):
        users_data = [
            {
                'email': 'test2@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            },
            {
                'email': 'test3@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            }
        ]
        result = self.dbm.add_users(users_data)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test users has not been added! ({content})')
        result = self.dbm.add_users(users_data)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 400, f'Added users with the same email! ({content})')


    def test_del_users(self):
        users_list = [{'email': 'test0@test.ru'}, {'email': 'test1@test.ru'}]
        result = self.dbm.del_users(users_list)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test users has not been removed! ({content})')
        result = self.dbm.del_users(users_list)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 404, f'Removed non-existent user! ({content})')


    def test_edit_users(self):
        users_data = [
            {
                'email': 'test0@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            },
            {
                'email': 'test1@test.ru',
                'pwd': 'test', 'name': ['test', 'test', 'test'], 'position': 'test'
            }
        ]
        result = self.dbm.edit_users(users_data)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test users has not been edited! ({content})')
        users_data[0]['email'] = 'not-test@test.ru'
        users_data[1]['email'] = 'not-test@test.ru'
        result = self.dbm.edit_users(users_data)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 404, f'Edited non-existent user! ({content})')


    def test_authorization(self):
        user_data = {'email': 'test0@test.ru', 'pwd': 'test'}
        _, content, code = self.dbm.authorization(user_data)
        self.assertEqual(code, 200, f'User not authorized! ({content})')
        user_data['email'] = 'not-test@test.ru'
        _, content, code = self.dbm.authorization(user_data)
        self.assertEqual(code, 404, f'Authorized non-existent user! ({content})')


    def test_get_all_users(self):
        _, content, code = self.dbm.get_all_users()
        self.assertEqual(code, 200, f'Users not received! ({content})')


    def test_add_projects(self):
        projects_data = [
            {'name': 'test2', 'deadline': '12-12-2020'},
            {'name': 'test3', 'deadline': '12-12-2020'}
        ]
        result = self.dbm.add_projects(projects_data)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test projects has not been added! ({content})')
        result = self.dbm.add_projects(projects_data)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 400, f'Added projects with the same email! ({content})')


    def test_del_projects(self):
        projects_list = [
            {'name': 'test0'},
            {'name': 'test1'}
        ]
        result = self.dbm.del_projects(projects_list)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test projects has not been removed! ({content})')
        result = self.dbm.del_projects(projects_list)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 404, f'Removed non-existent project! ({content})')


    def test_edit_projects(self):
        projects_data = [
            {'name': 'test0', 'deadline': '12-12-2020'},
            {'name': 'test1', 'deadline': '12-12-2020'}
        ]
        result = self.dbm.edit_projects(projects_data)
        self.assertEqual(len(result), 2, f'Too many response! ({len(result)})')
        for r in result:
            _, content, code = r
            self.assertEqual(code, 200, f'Test projects has not been edited! ({content})')
        projects_data[0]['name'] = 'not-test'
        projects_data[1]['name'] = 'not-test'
        result = self.dbm.edit_projects(projects_data)
        for r in result:
            _, content, code = r
            self.assertEqual(code, 404, f'Edited non-existent project! ({content})')


    def test_get_all_projects(self):
        _, content, code = self.dbm.get_all_projects()
        self.assertEqual(code, 200, f'Projects not received! ({content})')


class JSONTestCase(unittest.TestCase):
    def test_json_schema(self):
        bad_jsons = (
            {},
            {'key': 'value'},
            {'requests': {}},
            {'token': ''},
            {'requests': {}, 'token': {}},
            {'requests': {}, 'token': ''},
            {'requests': {'key': 'value'}, 'token': ''},
            {'requests': '', 'token': ''},
            {'requests': {}, 'token': '1'},

            {'requests': {'authorization': {'email': '', 'pwd': '12345'}}, 'token': ''},
            {'requests': {'authorization': {'email': 'qwe@qwe.ru', 'pwd': '12345', 'key': 'value'}}, 'token': ''},
            {'requests': {'authorization': [{'email': 'qwe@qwe.ru', 'pwd': '12345'}, {'email': 'qwe@qwe.ru', 'pwd': '12345'}]}, 'token': ''},
            {'requests': {'authorization': {'email': 'qwe@qwe.ru'}}, 'token': ''},
            {'requests': {'authorization': {'email': 'not-email', 'pwd': '12345'}}, 'token': ''},

            {'requests': {'add_users': [{'email': 'qwe@qwe.ru', 'pwd': '', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'add_users': [{'email': 'qwe@qwe.ru', 'pwd': '0', 'name': ['', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'add_users': [{'email': 'qwe@qwe.ru', 'pwd': '0', 'name': ['1', '2', '3'], 'position': ''}]}, 'token': ''},
            {'requests': {'add_users': [{'email': '', 'pwd': '0', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'add_users': [{'email': 'not-email', 'pwd': '0', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},

            {'requests': {'del_users': [{'email': 'qwe@qwe.ru'}, {'email': 'qwe@qwe.ru'}, {}]}, 'token': ''},
            {'requests': {'del_users': [{'email': 'qwe@qwe.ru', 'key': 'value'}]}, 'token': ''},

            {'requests': {'edit_users': [{'email': 'qwe@qwe.ru', 'pwd': '', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'edit_users': [{'email': 'qwe@qwe.ru', 'pwd': '0', 'name': ['', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'edit_users': [{'email': 'qwe@qwe.ru', 'pwd': '0', 'name': ['1', '2', '3'], 'position': ''}]}, 'token': ''},
            {'requests': {'edit_users': [{'email': '', 'pwd': '0', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},
            {'requests': {'edit_users': [{'email': 'not-email', 'pwd': '0', 'name': ['1', '2', '3'], 'position': '4'}]}, 'token': ''},

            {'requests': {'get_all_users': ''}, 'token': ''},
            {'requests': {'get_all_users': {'key': 'value'}}, 'token': ''},
        )
        with open('schema.json', 'r') as f:
            json_schema = json.load(f)
        for j in bad_jsons:
            print(j)
            self.assertRaises(ValidationError, validate, j, json_schema, format_checker=FormatChecker())


if __name__ == '__main__':
    unittest.main()
