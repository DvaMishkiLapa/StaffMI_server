# -*- coding: utf-8 -*-

import datetime
from hashlib import sha256

import jwt
import pymongo


class DBManager():
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(host='db')
        except pymongo.errors.ConnectionFailure as e:
            print(e)
        self.db = self.client.software

        # Collections
        self.users = self.db.users
        self.projects = self.db.projects
        self.tokens = self.db.tokens

        self.secret = '12345'


    # Authentication

    def create_token(self, email):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        token = jwt.encode({'email': email, 'exp': exp}, self.secret, algorithm='HS256')
        return {'token': token.decode()}


    def check_token(self, token):
        try:
            payload = jwt.decode(token.encode(), self.secret, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return 403, 'Invalid token!'
        return 200, payload['email']


    # Users

    def add_user(self, userdata):
        if self.users.find_one({'email': userdata['email']}):
            return 400, 'User already exist!'
        pwd_hash = sha256(userdata['pwd'].encode()).hexdigest()
        userdata['pwd'] = pwd_hash
        self.users.insert_one(userdata)
        return 200, 'OK'


    def del_user(self, email):
        if self.users.delete_one({'email': email}).deleted_count:
            return 200, 'OK'
        return 404, 'User not found!'


    def edit_user(self, userdata):
        user = self.users.find_one({'email': userdata['email']})
        if not user:
            return 404, 'User not found!'
        pwd_hash = sha256(userdata['pwd'].encode()).hexdigest()
        userdata['pwd'] = pwd_hash
        self.users.update({'email': userdata['email']}, userdata)
        return 200


    def authorization(self, email, pwd):
        user = self.users.find_one({'email': email})
        if not user:
            return 404, 'User not found!'
        if user['pwd'] == sha256(pwd.encode()).hexdigest():
            return 200, self.create_token(email)
        return 400, 'Wrong password!'


    def get_all_users(self):
        # TODO: Access rights!
        users = self.users.find({}, {'_id': False, 'pwd': False})
        return 200, tuple(users)


    # Projets

    def add_project(self, projectdata):
        if self.projects.find_one({'name': projectdata['name']}):
            return 400, 'Project already exist!'
        self.projects.insert_one(projectdata)
        return 200


    def del_project(self, name):
        if self.projects.delete_one({'name': name}).deleted_count:
            return 200
        return 404, 'Project not found!'


    def edit_project(self, projectdata):
        project = self.projects.find_one({'name': projectdata['name']})
        if not project:
            return 404, 'Project not found!'
        self.projects.update({'name': projectdata['name']}, projectdata)
        return 200


    def get_all_projects(self):
        # TODO: Access rights!
        projects = self.projects.find({}, {'_id': False})
        return 200, tuple(projects)


    def get_projects_by_names(self, names):
        return 200, list(self.projects.find({'name': name}) for name in names)
