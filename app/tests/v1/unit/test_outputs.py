from app.tests.v1.base_test import BaseTest
import json

class Outouts(BaseTest):
    
    def test_create_output(self):
        
        self.assertEqual(json.loads(self.create_output().data),[{"status": 201, "data":"Output Added"}],"with all details provided correctly, an output shoult be created." )
    
    def test_it_doesnt_create_with_less_params(self):
        self.assertEqual(json.loads(self.create_output_without_name().data),[{"status": 400, "data":"Error adding output, output_name not set"}],"You cannot create an output without name")

    def test_it_returns_output(self):
        self.create_output()
        self.assertEqual(json.loads(self.get_output().data),{'data': [{'output_id': 1, 'output_name': 'Maternity support'}], 'status': 200})
    
    def test_it_deletes_output(self):
        self.create_output()
        self.assertEqual(json.loads(self.delete_output().data), [{"status": 202, "data":"Output with output_id 1 Removed"}])
    
    def test_deletion_without_id(self):
        token = self.filter_token()
        self.assertEqual(json.loads(self.app.delete('/api/v1/output/10', headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 404, "data":"No output found with output_id 10"}])
    
    def test_get_single_output(self):
        self.create_output()
        self.assertEqual(json.loads(self.app.get('/api/v1/output/1').data),{'data': [{'output_id': 1, 'output_name': 'Maternity support'}], 'status': 200},"If exists, then should be returned" )
    
    def test_get_unexisting(self):
        self.assertEqual(json.loads(self.app.get('/api/v1/output/1').data),[{"status":404, "data":"No Output found with output_id 1"}],"Should have 404, not found")
        
    def test_get_while_empty(self):
        self.assertEqual(json.loads(self.app.get('/api/v1/output/').data), [{"status":404, "data":"No output found"}], "404, No data")
        
    def test_can_update_output(self):
        self.create_output()
        self.assertEqual(json.loads(self.update_output().data),[{"status":200, "data":"Output with output_id 1 updated"}], "if details are provided, result is 200")
        
    def test_update_without_values(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.app.put('/api/v1/output/', data=json.dumps(self.output_details),headers={'content-type':'application/json','Authorization': f'Bearer {token}'}).data),\
                         [{"status":400, "data":"Output_id not provided. Cannot update"}])
    
    def test_update_without_new_name(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.app.put('/api/v1/output/', data=json.dumps(self.output_update_minus_name),headers={'content-type':'application/json', 'Authorization': f'Bearer {token}'}).data),\
                         [{"status":400, "data":"Output name not set for output_id 1"}])
        
    def test_update_non_existent(self):
        self.assertEqual(json.loads(self.update_output().data),[{"status":404, "data":"No Ouptut found with output_id 1"}],"No data in the first place")
        
    def test_get_output_with_children(self):
        self.create_output()
        self.create_new_activity()
        self.assertEqual(json.loads(self.get_single_output().data)[0], self.single_out_put_with_child, "Real serious one")