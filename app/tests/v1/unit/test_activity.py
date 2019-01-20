from app.tests.v1.base_test import BaseTest
import json

class Activity(BaseTest):
    def test_it_creates_activity(self):
        self.create_output()
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status":201, "data":"Activity Created"}], \
                         "With requirements provided an activity should be created")
    
    def test_it_requires_param_under_output(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.app.post('/api/v1/activity/', data=json.dumps(\
                        self.activity_details_minus_output), headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":400, "data":"under_output not set"}], "parent output is required")
    
    def test_creation_without_parent_existense(self):
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status": 404, "data": "Activity cannot be added without parent output"}], \
                         "Parent output must exist before creating a child")
                         
    def test_it_requires_activity_desc(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.app.post('/api/v1/activity/', data=json.dumps(self.activity_details_minus_desc), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":400, "data":"Activity_desc not set"}], "Activity desc is required")
    
    def test_it_takes_activity_partner_default(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.app.post('/api/v1/activity/', data=json.dumps(self.activity_details_minus_patner), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":201, "data":"Activity Created, Patner default is CGK/partner"}], "Activity patner may be required")
        
    def test_it_returns_activity_as_created(self):
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.get('/api/v1/activity/').data), {"data" : [self.activity_details_get], "status" : 200}, "Created should equal fetched")
        
    def test_it_returns_activity_by_id(self):
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.get('/api/v1/activity/1').data), {"data" : [self.activity_details_get], "status" : 200}, "Created should equal fetched by id")
        
    def test_it_updates_activity(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.put('/api/v1/activity/', data=json.dumps(self.activity_details_minus_output), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":200, "data":"Activity with activity_id 1 updated"}])
        self.assertEqual(json.loads(self.app.get('/api/v1/activity/1').data)['data'][0]['activity_patner'], 'CGK/TUPIME KAUNTI', 'The request should fetch the updated patner')
        
    def test_update_minus_id(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.put('/api/v1/activity/', data=json.dumps(self.activity_details_minus_desc), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":400, "data":"Activity_id not provided. Cannot update"}], 'if not id, error 404')
        
    def test_update_minus_desc(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.put('/api/v1/activity/', data=json.dumps(self.activity_details_minus_detail), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":400, "data":"Activity desc not set for activity_id 1"}],'If not desc, error 404')
        
    def test_update_minus_progress(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.put('/api/v1/activity/', data=json.dumps(self.activity_details_minus_progress), \
        headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data), [{"status":400, "data":"Activity_progress not provided. Cannot update"}],'If not progress, error 404')
        
    def test_deletion_of_activity(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.delete('/api/v1/activity/1', headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 201, "data":"Activity with activity_id 1 Removed"}], "Should delete")
        
    def test_deletion_of_activity_less_id(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.delete('/api/v1/activity/', headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 400, "data":"Please provide an identifier"}], "no identifier")
        
    def test_deletion_of_activity(self):
        token = self.filter_token()
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.app.delete('/api/v1/activity/40', headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 404, "data":"No activity found with activity_id 40"}], "Not found")
        
        
    def test_getting_single_activity_under_specific_output(self):
        #smelly code, repeated
        self.create_output()
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status":201, "data":"Activity Created"}], \
                         "With requirements provided an activity should be created")
        
        #test getting thru
        self.assertEqual(json.loads(self.app.get('/api/v1/activity/1/1').data), {"data": [self.activity_details_get], 'status': 200}, 'Real deep detail')
        