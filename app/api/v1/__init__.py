from flask import Blueprint
from flask_restful import Api, Resource
from .views.operations_view import *


version_one = Blueprint('api_v1',__name__)

api = Api(version_one)

api.add_resource(OutputViews, '/api/v1/output/', '/api/v1/output/<identifier>')

api.add_resource(ActivityViews, '/api/v1/activity/', '/api/v1/activity/<identifier>', '/api/v1/activity/<identifier>/<under_output>')

api.add_resource(CommentsView, '/api/v1/comment/', '/api/v1/comment/<_id>')

api.add_resource(UsersAuthSignUp, '/api/v1/auth/sign-up/')

api.add_resource(UserAuthSignIn, '/api/v1/auth/sign-in/','/api/v1/auth/', '/api/v1/auth/<user_id>', '/api/v1/auth/update/')

api.add_resource(Misc, '/api/v1/misc/search/<name>', '/api/v1/auth/log-out/')


