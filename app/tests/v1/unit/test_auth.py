from app.tests.v1.base_test import BaseTest
import json

class TestAuth(BaseTest):
    def test_user_can_create_account(self):
        self.assertEqual(json.loads(self.create_account().data), [{"status": 201, "data": "User Registered successfully"}],'User should be able to create account')
        
    def test_user_can_login(self):
        self.assertEqual(self.login_auth().status_code, 404, 'User has no account yet')
        self.create_account()
        self.assertEqual(self.login_auth().status_code, 202, 'User should be allowed to log in')
        token = self.filter_token()
        #test logging out, then place a request!
        self.assertEqual(json.loads(self.app.post('/api/v1/auth/log-out/', headers = {'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), \
                         [{"status": 202, "data": "Logged out successfully"}], 'should log out if has session')
        #place a request requiring auth, after loggout
        self.assertEqual(json.loads(self.app.delete('/api/v1/output/10', headers = {'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data),\
                         [{"status": 401, "data": "Your session expired, A token was required, but yours has expired."}], 'no token at the moment')
        
    def test_user_detail_can_be_updated(self):
        token = self.filter_token()
        self.create_account()
        self.login_auth()
       # self.assertEqual(json.loads(self.app.put('/api/v1/auth/update/', data = json.dumps({"user_id":"1"}), headers = {'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), \
        #                 [{"status": 202, "data": "User detail Successfully updated"}], "putting same detail, result is key")
    
    def test_get_users(self):
        token = self.filter_token()
        self.assertEqual(json.loads(self.app.get('/api/v1/auth/sign-in/', headers = {'Authorization': f'Bearer {token}'}).data)['data'][0]['email'], self.user_credentials['email'],"should reflect user detail")
        