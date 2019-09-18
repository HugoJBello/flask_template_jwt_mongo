from flask import request, make_response, jsonify
from project.server.models import User
from functools import wraps


def is_authenticated():
    def _is_authenticated_decorator(f):
        @wraps(f)
        def __is_authenticated_decorator(*args, **kwargs):
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
                if isinstance(resp, str) and ('Invalid token' not in resp) and ('Signature expired' not in resp) and (
                        'Token blacklisted' not in resp):
                    id = resp
                    user = User.find_one_by_username(id)
                    userObject = {
                        'status': 'success',
                        'data': {
                            'user_id': user['_id'],
                            'email': user['email'],
                            'admin': user['admin'],
                            'registered_on': user['registered_on']
                        }
                    }
                    print('authenticated user ')
                    print(userObject)
                    return f(*args, **kwargs)

                responseObj = {
                    'status': 'fail',
                    'message': resp
                }
                print('not authenticated user')
                return make_response(jsonify(responseObj)), 401
            else:
                responseObj = {
                    'status': 'fail',
                    'message': 'Provide a valid auth token.'
                }
                print('not authenticated user')
                return make_response(jsonify(responseObj)), 401
            return result
        return __is_authenticated_decorator
    return _is_authenticated_decorator