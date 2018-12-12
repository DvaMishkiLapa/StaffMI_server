# -*- coding: utf-8 -*-

import datetime
import os
from bson import ObjectId
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

        self.secret = os.getenv('DB_SECRET', 'MOSTSECUREKEY')

        self.add_users([{
            'email': os.getenv('ADMIN_EMAIL', 'admin@admin.ru'),
            'pwd': os.getenv('ADMIN_PWD', '12345'),
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
        for _id in users_list:
            if self.users.delete_one({'_id': ObjectId(_id)}).deleted_count:
                result.append((True, 'User has been removed.', 200))
            else:
                result.append((False, 'User not found!', 404))
        return result


    def edit_users(self, users_data):
        result = []
        for user in users_data:
            if not self.users.find_one({'_id': ObjectId(user['_id'])}):
                result.append([False, 'User not found!', 404])
            else:
                pwd_hash = sha256(user['pwd'].encode()).hexdigest()
                user['pwd'] = pwd_hash
                _id = user.pop('_id')
                self.users.replace_one({'_id': ObjectId(_id)}, user)
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


    def get_all_users(self, params):
        offset = params['offset']
        length = params['length']
        users = self.users.find({}, {'pwd': False})
        users = list(users)[offset:offset + length]
        for u in users:
            u['_id'] = str(u['_id'])
        return True, tuple(users), 200


    def change_password(self, user_data):
        email = user_data['email']
        old_pwd = user_data['old_pwd']
        new_pwd = user_data['new_pwd']
        user = self.users.find_one({'email': email})
        if not user:
            return False, 'User not found!', 404
        if user['pwd'] == sha256(old_pwd.encode()).hexdigest():
            pwd_hash = sha256(new_pwd.encode()).hexdigest()
            user['pwd'] = pwd_hash
            self.users.replace_one({'_id': ObjectId(user['_id'])}, user)
            return True, 'Password has been changed.', 200
        return False, 'Wrong password!', 400


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
        for _id in projects_list:
            if self.projects.delete_one({'_id': ObjectId(_id)}).deleted_count:
                result.append((True, 'Project has been removed.', 200))
            else:
                result.append((False, 'Project not found!', 404))
        return result


    def edit_projects(self, projects_data):
        result = []
        for project in projects_data:
            if not self.projects.find_one({'_id': ObjectId(project['_id'])}):
                result.append([False, 'Project not found!', 404])
            else:
                _id = project.pop('_id')
                self.projects.replace_one({'_id': ObjectId(_id)}, project)
                result.append((True, 'Project has been changed.', 200))
        return result


    def get_all_projects(self, params):
        offset = params['offset']
        length = params['length']
        projects = self.projects.find({})
        projects = list(projects)[offset:offset + length]
        for p in projects:
            p['_id'] = str(p['_id'])
        return True, tuple(projects), 200
