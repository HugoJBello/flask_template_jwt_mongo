from functools import wraps
from flask import request, Blueprint, make_response, jsonify
from flask_restful import Resource
from flask.views import MethodView

from project.server.hello_world.is_authenticated_middleware import is_authenticated
from project.server import bcrypt, db

hello_blueprint = Blueprint('hello', __name__)

def home_decorator():
    def _home_decorator(f):
        @wraps(f)
        def __home_decorator(*args, **kwargs):
            # just do here everything what you need
            print('before home')
            print(request.args)
            result = f(*args, **kwargs)
            print('home result: %s' % result)
            print('after home')
            return result
        return __home_decorator
    return _home_decorator

class HelloWorld(MethodView):
    @home_decorator()
    def get(self):
        args = request.args
        return make_response(jsonify({'hello': 'world ' + args["user"]}))


class HelloWorldSecured(Resource):
    @is_authenticated()
    def get(self):
        args = request.args
        return make_response(jsonify({'hello': 'world ' + args["user"]}))


hello_view = HelloWorld.as_view('hello')
hello_secured = HelloWorldSecured.as_view('hello-sec')

hello_blueprint.add_url_rule(
    '/',
    view_func=hello_view,
    methods=['GET']
)

hello_blueprint.add_url_rule(
    '/hello_secured',
    view_func=hello_secured,
    methods=['GET']
)