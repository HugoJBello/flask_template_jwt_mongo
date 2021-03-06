# project/server/auth/views.py


from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User, BlacklistToken

auth_blueprint = Blueprint('auth', __name__)


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        username = post_data.get('username')
        user = User.find_one_by_username(username)
        if not user:
            try:
                user = User(
                    username=post_data.get('username'),
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                # insert the user
                user.save()
                # generate the auth token
                auth_token = user.encode_auth_token(user._id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                print(e)
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            username = post_data.get('username')
            user = User.find_one_by_username(username)
            print(user)
            if user and bcrypt.check_password_hash(
                user["password"], post_data.get('password')
            ):
                auth_token = User.encode_auth_token(user["_id"])
                auth_token_decoded = auth_token.decode()
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token_decoded
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if (auth_header is not None) and (' ' in auth_header):
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = auth_header

        if auth_token:
            resp = None
            try:
                resp = User.decode_auth_token(auth_token)
            except Exception as e:
                print("invalid id token")
            if isinstance(resp, str) and ('Invalid token' not in resp) and ('Signature expired' not in resp) and ('Token blacklisted' not in resp):
                id = resp
                user = User.find_one_by_id(id)
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': str(user["_id"]),
                        'email': user['email'],
                        'admin': user['admin'],
                        'registered_on': user['registered_on']
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if (auth_header is not None) and (' ' in auth_header):
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = auth_header
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, str) and ('Signature expired' not in resp) and ('Token blacklisted' not in resp):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    blacklist_token.save()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)
