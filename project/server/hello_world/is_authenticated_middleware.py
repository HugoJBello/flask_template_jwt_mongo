from flask import request, make_response, jsonify
from project.server.models import User
from functools import wraps


def is_authenticated():
    def _is_authenticated_decorator(f):
        @wraps(f)
        def __is_authenticated_decorator(*args, **kwargs):
            # get the auth token
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    auth_token = auth_header.split(" ")[1]
                except IndexError:
                    userObject = {
                        'status': 'fail',
                        'message': 'Bearer token malformed.'
                    }
                    return make_response(jsonify(userObject)), 401
            else:
                auth_token = ''
            if auth_token:
                resp = User.decode_auth_token(auth_token)
                if not isinstance(resp, str):
                    user = User.query.filter_by(id=resp).first()
                    userObject = {
                        'status': 'success',
                        'data': {
                            'user_id': user.id,
                            'email': user.email,
                            'admin': user.admin,
                            'registered_on': user.registered_on
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