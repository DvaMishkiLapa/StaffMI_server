# -*- coding: utf-8 -*-

import datetime
import os
from hashlib import sha256

import jwt
import pymongo


class DBManager:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(host='db')
        except pymongo.errors.ConnectionFailure as e:
            print(e)
        self.db = self.client.software

        # Collections
        self.users = self.db.users
        self.projects = self.db.projects

        self.secret = os.getenv('DB_SECRET')

        self.add_users([{
            'email': os.getenv('ADMIN_EMAIL'),
            'pwd': os.getenv('ADMIN_PWD'),
            'name': ['Иванов', 'Иван', 'Иванович'],
            'position': 'Генеральный директор'
        }])


    # Authentication

    def create_token(self, email):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        token = jwt.encode({'email': email, 'exp': exp}, self.secret, algorithm='HS256')
        return token.decode()


    def check_token(self, token):
        try:
            payload = jwt.decode(token.encode(), self.secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return False, 'Token expired!', 403
        except (jwt.DecodeError, AttributeError):
            return False, 'Invalid token!', 403
        return True, payload['email'], 200


    # Users

    def add_users(self, users_data):
        result = []
        for user in users_data:
            if self.users.find_one({'email': user['email']}):
                result.append((False, 'User already exist!', 400))
            else:
                pwd_hash = sha256(user['pwd'].encode()).hexdigest()
                user['pwd'] = pwd_hash
                self.users.insert_one(user)
                result.append((True, 'User has been added.', 200))
        return result


    def del_users(self, users_list):
        result = []
        for user in users_list:
            if self.users.delete_one({'email': user['email']}).deleted_count:
                result.append((True, 'User has been removed.', 200))
            else:
                result.append((False, 'User not found!', 404))
        return result


    def edit_users(self, users_data):
        result = []
        for user in users_data:
            if not self.users.find_one({'email': user['email']}):
                result.append([False, 'User not found!', 404])
            else:
                pwd_hash = sha256(user['pwd'].encode()).hexdigest()
                user['pwd'] = pwd_hash
                self.users.replace_one({'email': user['email']}, user)
                result.append((True, 'User has been changed.', 200))
        return result


    def authorization(self, user_data):
        email = user_data['email']
        pwd = user_data['pwd']
        user = self.users.find_one({'email': email})
        if not user:
            return False, 'User not found!', 404
        if user['pwd'] == sha256(pwd.encode()).hexdigest():
            return True, self.create_token(email), 200
        return False, 'Wrong password!', 400


    def get_all_users(self, _={}):
        users = self.users.find({}, {'_id': False, 'pwd': False})
        return True, tuple(users), 200


    # Projets

    def add_projects(self, projects_data):
        result = []
        for project in projects_data:
            if self.projects.find_one({'name': project['name']}):
                result.append([False, 'Project already exist!', 400])
            else:
                self.projects.insert_one(project)
                result.append((True, 'Project has been added.', 200))
        return result


    def del_projects(self, projects_list):
        result = []
        for project in projects_list:
            if self.projects.delete_one({'name': project}).deleted_count:
                result.append((True, 'Project has been removed.', 200))
            else:
                result.append((False, 'Project not found!', 404))
        return result


    def edit_projects(self, projects_data):
        result = []
        for project in projects_data:
            if not self.projects.find_one({'name': project['name']}):
                result.append([False, 'Project not found!', 404])
            else:
                self.projects.replace_one({'name': project['name']}, project)
                result.append((True, 'Project has been changed.', 200))
        return result


    def get_all_projects(self, _={}):
        projects = self.projects.find({}, {'_id': False})
        return True, tuple(projects), 200
