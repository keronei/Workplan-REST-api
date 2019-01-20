from app.tests.v1.base_test import BaseTest
import json

class Activity(BaseTest):
    def test_it_creates_comment(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status":201, "data":"Activity Created"}], \
                         "With requirements provided an activity should be created")
        self.assertEqual(json.loads(self.create_comment().data), [{"status":201, "data":"Comment Added"}], "Comment should be creatable")
        #tests deletion
        self.assertEqual(json.loads(self.app.delete('/api/v1/comment/1',  headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 200, "data": "Comment removed"}], 'Comment exists, should be removable')
        #test deleting non-existent comment
        self.assertEqual(json.loads(self.app.delete('/api/v1/comment/100',  headers = {'Authorization': f'Bearer {token}'}).data), [{"status": 404, "data": "No comments with such an id"}], "no comment")
        self.assertEqual(self.app.delete('/api/v1/comment/100',  headers = {'Authorization': f'Bearer {token}'}).status_code, 404, 'Not found')
        
    def test_it_fetches_comment(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status":201, "data":"Activity Created"}], \
                         "With requirements provided an activity should be created")
        self.create_comment()
        self.assertEqual(json.loads(self.app.get('/api/v1/comment/1').data), { "data": [self.get_comment_detail ], "status": 200})
        
    def test_get_unexsiting_comment(self):
        token = self.filter_token()
        self.create_output()
        self.assertEqual(json.loads(self.create_new_activity().data), [{"status":201, "data":"Activity Created"}], \
                         "With requirements provided an activity should be created")
        self.assertEqual(json.loads(self.app.get('/api/v1/comment/1').data),  [{"status": 404, "data": "No comments under this activity"}])
        