from flask_restful import Resource
from flask import request, jsonify, Response
from app.api.v1.models.operations import *
from app.api.v1.utils.decorators import token_requiried

class ActivityViews(Resource):
    def __init__(self):
        self.activity_model = Activities()
    
    @token_requiried
    def post(self):
        return self.activity_model.create(request.get_json())
    def get(self,identifier=None, under_output=None):
        
        if(identifier is None):
            return self.activity_model.query_activity()
        elif identifier is not None and under_output is None:
            return jsonify(self.activity_model.query_activity(identifier))
        else:
            return jsonify(self.activity_model.query_activity(identifier, under_output))
    
    @token_requiried
    def delete(self, identifier=None):
        if identifier is not None:
            if self.activity_model.remove_activity(identifier):
                return [{"status": 202, "data":"Activity with activity_id {} Removed".format(identifier)}], 202
            return [{"status": 404, "data":"No activity found with activity_id {}".format(identifier)}], 404
        return [{"status": 400, "data":"Please provide an identifier"}], 400
    
    @token_requiried
    def put(self, identifier=None):
        data = request.get_json()
        return self.activity_model.update_activity(data)
        
        
    
class OutputViews(Resource):
    def __init__(self):
        self.output_model = Output()
    @token_requiried
    def post(self):
        data = request.get_json()
        if self.output_model.create(data):
            return [{"status": 201, "data":"Output Added"}], 201
        return [{"status": 400, "data":"Error adding output, output_name not set"}], 400
        
    def get(self, identifier=None):
        if(identifier is None):
            return self.output_model.query_outputs()
        else:
            return jsonify(self.output_model.query_outputs(identifier))
        
    @token_requiried
    def put(self, identifier=None):
        data = request.get_json()
        return self.output_model.update_output(data)
    
    @token_requiried
    def delete(self, identifier=None):
        if identifier is not None:
            if self.output_model.remove_output(identifier):
                return [{"status": 202, "data":"Output with output_id {} Removed".format(identifier)}], 202
            return [{"status": 404, "data":"No output found with output_id {}".format(identifier)}], 404
        return [{"status": 400, "data":"Please provide an identifier"}], 400
        
    
class PeriodViews(Resource):
    def post(self):
        pass

class CommentsView(Resource):
    def __init__(self):
        self.comments_model = Comments()
        
    @token_requiried    
    def post(self):
       return self.comments_model.create(request.get_json())
    def get(self, _id=None):
        if _id is None:
             return [{"status": 400, "data":"Please provide an activity_id"}], 400
        return self.comments_model.query_comments(_id)
    @token_requiried
    def delete(self, _id):
        if _id is None:
            return [{"status": 400, "data":"Please provide a comment_id"}], 400
        return self.comments_model.delete_comment(_id)
            
class UsersAuthSignUp(Resource):
    def __init__(self):
        self.user_model = Users()
    def post(self):
        return self.user_model.sign_up(request.get_json())
class UserAuthSignIn(Resource):
    def __init__(self):
        self.user_model = Users()
    def post(self):
        return self.user_model.sign_in(request.get_json())
    @token_requiried
    def get(self, user_id=None):
        if user_id is None:
            return self.user_model.get_all_users()
        return self.user_model.get_user_by_id(user_id)
    @token_requiried
    def put(self):
        return self.user_model.update_user(request.get_json())
class Misc(Resource):
    @token_requiried
    def get(self, name):
        return Users().get_user_by_name(name)
    @token_requiried
    def post(self):
        users_token = request.headers.get('Authorization')
        if users_token:
            actual_token = users_token.split(" ")[1]
            if actual_token:
                if RevokeToken().check_if_blacklisted(actual_token):
                    return [{"status": 401, "data": "Currently unauthenticated."}]               
                RevokeToken().blacklist_token(actual_token)
                return [{"status": 202, "data": "Logged out successfully"}]
            return [{"status": 400, "data": "Bad token, Not logged in"}]
        return [{"status": 401, "data": "Not authenticated, no token on your header"}]
            
        
    