# project/server/models.py


import jwt
import datetime
import os
from bson.objectid import ObjectId

from project.server import app, db, bcrypt

db_users = db["testing"].users
db_blacklist = db["auth_db"].blacklisted_tokens


class User:
    """ User Model for storing user related details """
    def __init__(self, email, password, username, admin=False, id=None):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.id = id

    def save(self):
        id = db_users.insert_one(self.__dict__).inserted_id
        self._id =str(id)

    @staticmethod
    def delete_one(username):
        db_users.delete_one({'username': username})

    @staticmethod
    def find_one_by_username(username):
        result = db_users.find_one({'username':username})
        print(result)
        if (result):
            result['_id'] = str(result['_id'])
        return result

    @staticmethod
    def find_one_by_id(id):
        return db_users.find_one({})

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        user_id=str(user_id)
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'UserId': user_id
            }
            return jwt.encode(
                payload,
                os.getenv('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithm='HS256')
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['Username']
        except jwt.ExpiredSignatureError as e:
            print(e)
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError as e:
            print(e)
            return 'Invalid token. Please log in again.'


class BlacklistToken:
    """
    Token Model for storing JWT tokens
    """

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    def save(self):
        item = {"token": self.token, "blacklisted_on": self.blacklisted_on, "_id": self.token}
        db_blacklist.save(item)

    @staticmethod
    def find_one(self, token):
        return db_blacklist.find_one({'token': token})

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        token = str(auth_token)
        res = db_blacklist.find_one({'token': token})
        if res:
            return True
        else:
            return False
