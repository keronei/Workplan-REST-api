from unittest import TestCase
from flask import current_app
from datetime import datetime
from app import launcher
from instance.config import app_config
import json
from app.api.v1.models.operations import db

class BaseTest(TestCase):
    
    def setUp(self):
        _app = launcher(app_config['testing'])
        
        self.app = _app.test_client()
        self.app_context = _app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.commit()
        
        self.output_details = {
            "name":"Maternity support"
        }
        self.output_update_details = {
            "id":1,
            "name":"Maternity support updated"
        }
        self.output_update_minus_name = {
            "output_id":1
        }
        self.activity_details = {
            "activity_desc":"polio phase 1 Vaccination",
            "under_output":1,
            "activity_period":0,
            "activity_patner":"CountyMOH"
        }
        
        self.activity_details_get = {
            "activity_desc": "polio phase 1 Vaccination",
            "activity_id": 1,
            "activity_patner": "CountyMOH",
            "activity_period": 0,
            "activity_progress": 0,
            "under_output": 1
   
        }
        
        
        self.activity_details_minus_output = {
            "activity_desc":"polio phase 1 Vaccination",
            "activity_period":0,
            "activity_patner":"CGK/TUPIME KAUNTI",
            "activity_id": 1,
            "activity_progress": 0
        }
        
        self.activity_details_minus_desc = {
            "under_output":1,
            "activity_period":0,
            "activity_patner":"CountyMOH"
        }
        self.activity_details_minus_detail = {
            "under_output":1,
            "activity_period":0,
            "activity_id": 1,
            "activity_patner":"CountyMOH"
        }
        
        self.activity_details_minus_progress = {
            "under_output":1,
            "activity_period":0,
            "activity_id": 1,
            "activity_desc":"polio phase 1 Vaccination",
            "activity_patner":"CountyMOH"
        }
        self.activity_details_minus_patner = {
            "activity_desc":"polio phase 1 Vaccination",
            "under_output":1,
            "activity_period":0
        }
        
        self.single_out_put_with_child = {
        "data": [
            {
                "activities": [
                    {
                        "activity_desc": "polio phase 1 Vaccination",
                        "activity_id": 1,
                        "activity_patner": "CountyMOH",
                        "activity_period": 0,
                        "activity_progress": 0,
                        "under_output": 1
                    }
                ],
                "output_id": 1,
                "output_name": "Maternity support"
            }
        ],
        "status": 200
    }
        
        self.user_credentials = {
            "first_name":"Omondi",
            "last_name":"Johansen",
            "email":"superomondi@rocketmail.io",
            "phone_number":"2547394261",
            "password":"iggodfkllfk"
        }
        
        self.comment_details = {
            "comment": "started well",
            "author_user_id" : 1,
            "activity_id" :1
        }

        self.get_comment_detail = { "comment": "started well","created_on": datetime.today().strftime("%d %B %Y %H:%M"), "email": "superomondi@rocketmail.io" }
        
    def create_account(self):
        response = self.app.post('/api/v1/auth/sign-up/', data=json.dumps(
            self.user_credentials),
            headers={'content-type':'application/json'})
            
        return response
    def login_auth(self):
        response = self.app.post('/api/v1/auth/sign-in/', data=json.dumps(
            self.user_credentials),
            headers={'content-type':'application/json' })
        
        return response
        
    
    def filter_token(self):
        self.create_account()
        response = self.login_auth()
        token = json.loads(response.data)[0]['token']
        return token
        
    def create_output(self):
        token = self.filter_token()
        response = self.app.post('/api/v1/output/', data=json.dumps({
            'output_name':self.output_details['name']}),
            headers={'content-type':'application/json',
                     'Authorization': f'Bearer {token}'})
            
        return response
    
    def update_output(self):
        token = self.filter_token()
        response = self.app.put('/api/v1/output/', data = json.dumps({
            'output_id':self.output_update_details['id'],
            'output_name':self.output_update_details['name']}),
            headers={'content-type':'application/json',
                     'Authorization': f'Bearer {token}'})
            
        return response
        
    def create_output_without_name(self):
        token = self.filter_token()
        response = self.app.post('/api/v1/output/', data = json.dumps({
            'output':self.output_details['name']}),
            headers={'content-type':'application/json',
                     'Authorization': f'Bearer {token}'})
            
        return response
        
    def get_output(self):
        response = self.app.get('/api/v1/output/')
        return response
    
    def get_single_output(self):
        response = self.app.get('/api/v1/output/1')
        return response
    
    def delete_output(self):
        token = self.filter_token()
        response = self.app.delete('/api/v1/output/1', headers = {'Authorization': f'Bearer {token}'})
        return response
    
    def create_new_activity(self):
        token = self.filter_token()
        response = self.app.post('/api/v1/activity/', data = json.dumps(
            self.activity_details
            ),
            headers = {'content-type':'application/json',
                     'Authorization': f'Bearer {token}'})
            
        return response
    def create_comment(self):
        token = self.filter_token()
        response = self.app.post('/api/v1/comment/', data = json.dumps(
            self.comment_details
            ),
            headers = {'content-type':'application/json',
                     'Authorization': f'Bearer {token}'})
            
        return response

    def test_app_exists(self):
        """Testing for app context existence"""
        self.assertFalse(current_app is None)
    
    def token_is_not_empty(self):
        """Test if something is returned on login"""
        self.assertFalse(self.login_auth is None)
        
    def tearDown(self):
        """Destroy app context once the setup succeeds"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()