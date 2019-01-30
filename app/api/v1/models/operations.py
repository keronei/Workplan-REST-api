from datetime import datetime, timedelta

import jwt
import psycopg2
from flask import current_app, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
class DbHelper:
    '''Creates a connection object as a member and a cursor.
    '''
    def __init__(self):

        self.connection_object = psycopg2.connect(host = "localhost", database = current_app.config['DATABASE'], user = "keronei", password = "")
        self.cursor_object = self.connection_object.cursor()

class Response:
    '''This class takes in: database headers, data-objects
    returns: json-formatted data from the database.'''

    def jsonify_things(self, description, cursor):  
        row_headers = [x[0] for x in description]
       
        json_data = []
        for result in cursor:
            json_data.append(dict(zip(row_headers, result)))
        
        return {"status" : 200, "data" : json_data}, 200
    
    def jsonify_activity(self, description_parent, cursor_parent, decription_child, cursor_child):  
        row_headers_parent = [x[0] for x in description_parent]
        row_headers_child = [y[0] for y in decription_child]
       
        row_headers_parent.append('activities')
        json_data = []
        child_data = []
        for result in cursor_parent:
            json_data.append(dict(zip(row_headers_parent, result)))
            
            
        for split in cursor_child:
            child_data.append(dict(zip(row_headers_child, split)))
            
        json_data[0]['activities'] = child_data
        
        return {"status" : 200, "data" : json_data}, 200

       
class Output(DbHelper, Response , db.Model):
    '''Deals with parent entries->contains child activities'''
    __tablename__ = 'outputs'
    output_id = db.Column(db.Integer, primary_key=True)
    output_name = db.Column(db.String(100), nullable=False)
    other_info = db.Column(db.String(256))
    
    def __init__(self):# inherit all the functions from the classes.
        super().__init__()

    def create(self, data):
        
         if 'output_name' in data.keys():# check if name is provided. Only param.
            output_name = data['output_name']
            sql = 'INSERT into outputs(output_name) VALUES (%s);'
            self.cursor_object.execute(sql, (output_name,))
            self.connection_object.commit()
            self.cursor_object.close()
            return True
         return False
        
    def query_outputs(self, identifier=None):
        '''returns outputs in 2 formats:
        1. simple output
        2. nested output, with activities as children.
        Facilitated by the provision of identifier(output_id)
        '''
        if(identifier is None):
            sql = 'SELECT output_id, output_name from outputs;'
            self.cursor_object.execute(sql)
            if self.cursor_object.rowcount == 0:
                return [{"status":404, "data":"No output found"}], 404
            
            return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
        
        sql_with_id = 'SELECT output_id, output_name from outputs where output_id = %s ;'
        self.cursor_object.execute(sql_with_id, (identifier,))
        if self.cursor_object.rowcount == 0:
            
            return [{"status":404, "data":"No Output found with output_id {}".format(identifier)}]
        description_parent = self.cursor_object.description
        cursor_parent = self.cursor_object.fetchall()
        
        sql_activity = 'SELECT * from activities where under_output = %s;'
        
        self.cursor_object.execute(sql_activity, (identifier,))
        
        if self.cursor_object.rowcount == 0:
            # Child activities requested but not available
            return self.jsonify_things(description_parent, cursor_parent)
        # Child activities present, call Response to next them.
        description_child = self.cursor_object.description
        cursor_child = self.cursor_object.fetchall()
        
        return jsonify(self.jsonify_activity(description_parent, cursor_parent, description_child, cursor_child))
 
    def update_output(self, data):
        
        if 'output_id' in data.keys():
            output_id = data['output_id']
            sql = 'SELECT output_id, output_name from outputs where output_id = %s ;'
            self.cursor_object.execute(sql, (output_id,))
            if self.cursor_object.rowcount == 0:
                 return [{"status":404, "data":"No Ouptut found with output_id {}".format(output_id)}], 404
            if 'output_name' in data.keys():
                new_name = data['output_name']
                
                sql = 'UPDATE outputs set output_name = (%s) where output_id = (%s);'
                self.cursor_object.execute(sql, (new_name,output_id,))
                self.connection_object.commit()
                self.cursor_object.close()
                return [{"status":200, "data":"Output with output_id {} updated".format(output_id)}]
            return [{"status":400, "data":"Output name not set for output_id {}".format(output_id)}], 400
        return [{"status":400, "data":"Output_id not provided. Cannot update"}], 400
    def remove_output(self, identifier):
        sql = 'DELETE from outputs where output_id = %s;'
        self.cursor_object.execute(sql, (identifier,))
        if self.cursor_object.rowcount == 0:
            return False
        self.connection_object.commit()
        self.cursor_object.close()
        return True
    
    
class Activities(DbHelper, Response ,db.Model):
    '''Children to outputs, achieved quaterly.'''
    __tablename__ = 'activities'
    
    activity_id = db.Column(db.Integer, primary_key=True)
    activity_desc = db.Column(db.String(1000), nullable=False)
    activity_period = db.Column(db.Integer)
    activity_progress = db.Column(db.Integer, default = 0)
    activity_patner = db.Column(db.String(100), default = 'CGK/Partner')
    under_output = db.Column(db.Integer, db.ForeignKey(Output.output_id, ondelete = 'CASCADE'))
    # relates to parent-Output
    output_relation = db.relationship(Output, backref = db.backref('children_to_output', passive_deletes=True))
    
    def __init__(self):
        super().__init__() # Inherit all the functions in child classes.
        
    def create(self, data):
        if 'under_output' in data.keys():
            if 'activity_desc' in data.keys():
                if 'activity_period' in data.keys():
                    activity_period = data['activity_period']
                    activity_desc = data['activity_desc']
                    under_output = data['under_output']
                    sql_check = 'SELECT output_id from outputs where output_id = %s;'
                    # perfom a check to ensure that an activity will get a parent output, else terminate request.
                    self.cursor_object.execute(sql_check, (under_output,))
                    if self.cursor_object.rowcount == 0:
                        return [{"status": 404, "data": "Activity cannot be added without parent output"}], 404
                    if 'activity_patner' in data.keys():

                        activity_patner = data['activity_patner']
                        sql = 'INSERT into activities(activity_desc, under_output, activity_period, activity_patner, activity_progress) VALUES (%s, %s, %s, %s, %s);'
                        self.cursor_object.execute(sql, (activity_desc, under_output, activity_period, activity_patner, 0))
                        self.connection_object.commit()
                        self.cursor_object.close()
                        return [{"status":201, "data":"Activity Created"}], 201
                    sql = 'INSERT into activities(activity_desc, under_output, activity_period, activity_patner, activity_progress) VALUES (%s, %s, %s, %s, %s);'
                    self.cursor_object.execute(sql, (activity_desc, under_output, activity_period, 'CGK/partner', 0))
                    self.connection_object.commit()
                    self.cursor_object.close()
                    return [{"status":201, "data":"Activity Created, Patner default is CGK/partner"}], 201
                    
                return [{"status":400, "data":"Activity_period not set"}], 400
            return [{"status":400, "data":"Activity_desc not set"}], 400
        return [{"status":400, "data":"under_output not set"}], 400
    def query_activity(self, identifier=None,under_output=None):
        # Double nesting, follow up
        if(identifier is None and under_output is None): # None specified, dump all the activities
            sql = 'SELECT activity_id,activity_progress, activity_desc, under_output, activity_period, activity_patner from activities;'
            self.cursor_object.execute(sql)
            if self.cursor_object.rowcount == 0:
                return [{"status":404, "data":"No activity found"}], 404
            return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
        elif identifier is not None and under_output is None: # Dump the particular activity: has to be only one.
            sql = 'SELECT activity_id, activity_progress, activity_desc, under_output, activity_period, activity_patner from activities where activity_id = %s ;'
            self.cursor_object.execute(sql,(identifier,))
            if self.cursor_object.rowcount == 0:
                
                return [{"status":404, "data":"No activity found with activity_id {}".format(identifier)}], 404
            
            return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
            

        sql = 'SELECT activity_id ,activity_progress, activity_desc,under_output,activity_period, activity_patner from activities where activity_id = %s and under_output = %s;'
        # Particular activity requested under specified output : returns 1 Output, various activities, if any
        self.cursor_object.execute(sql,(identifier,under_output))
        if self.cursor_object.rowcount == 0:
            
            return [{"status":404, "data":"No activity found with activity_id {} under output of output_id {}".format(identifier,under_output)}], 404
        
        return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
        
    def remove_activity(self, identifier):
        sql = 'DELETE from activities where activity_id = %s;'
        self.cursor_object.execute(sql, (identifier,))
        if self.cursor_object.rowcount == 0:
            return False
        self.connection_object.commit()
        self.cursor_object.close()
        return True
    def update_activity(self, data):
        
        if 'activity_id' in data.keys():
            activity_id = data['activity_id']
            sql = 'SELECT activity_id, activity_desc, under_output from activities where activity_id = %s ;'
            self.cursor_object.execute(sql, (activity_id,))
            if self.cursor_object.rowcount == 0: # Check that the activity to update is present
                 return [{"status":404, "data":"No activity found with activity_id {}".format(activity_id)}], 404
            if 'activity_desc' in data.keys():
                new_desc = data['activity_desc']
                if 'activity_patner' in data.keys():
                    patner = data['activity_patner']
                    if 'activity_progress' in data.keys():
                        activity_progress = data['activity_progress']
                        sql = 'UPDATE activities set activity_progress = (%s), activity_desc = (%s), activity_patner = %s where activity_id = (%s);'
                        self.cursor_object.execute(sql, (activity_progress, new_desc, patner, activity_id,))
                        self.connection_object.commit()
                        self.cursor_object.close()
                        return [{"status":200, "data":"Activity with activity_id {} updated".format(activity_id)}]
                    return [{"status":400, "data":"Activity_progress not provided. Cannot update"}], 400
                return [{"status":400, "data":"Activity_patner not provided. Cannot update"}], 400
            return [{"status":400, "data":"Activity desc not set for activity_id {}".format(activity_id)}], 400
        return [{"status":400, "data":"Activity_id not provided. Cannot update"}], 400
            
class RevokeToken( DbHelper, db.Model):
    '''Handle session closures, discard token, facilitate validity checks '''
    __tablename__ = 'blacklisted'
    token_id = db.Column(db.Integer, primary_key=True)
    blacklisted_token = db.Column(db.String(150), unique=True)
    
    
    def __init__(self):
        super().__init__()
        
    def blacklist_token(self, token):
        """
        Not soo bad as it sounds thought,
        when a user logs out, just prevent anyone hitting back button to gain session.
        So, mark their token as blacklisted, coz we cant force the token to expire :)
        """
        sql_insert = 'INSERT into blacklisted (blacklisted_token) VALUES (%s);'
        self.cursor_object.execute(sql_insert, (token,))
        self.connection_object.commit()
        self.cursor_object.close()
        
    def check_if_blacklisted(self, token):
        """
        Query the db for particular token,
        :return count
        if 0, all is well.
        """
        sql_check = 'SELECT blacklisted_token from blacklisted where blacklisted_token = %s;'
        self.cursor_object.execute(sql_check,(token, ))
        if self.cursor_object.rowcount == 0:
            return False
        return True
  

class Users( DbHelper, Response ,db.Model):
    '''Handles all user accounting requests'''
    def __init__(self):
        super().__init__()
        
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000))
    is_approved = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(15), nullable=True)
    
    def sign_up(self, data):
        # Nasty checks, will have to be refactored 
        if 'first_name' in data.keys():
            if 'last_name' in data.keys():
                if 'email' in data.keys():
                    if 'phone_number' in data.keys():
                        
                        if 'password' in data.keys():
                            sql_checker = 'SELECT email from users where email = %s;'
                            email = data['email']
                            first_name = data['first_name']
                            last_name = data['last_name']
                            phone_number = data['phone_number']
                            password = generate_password_hash(data['password'])
                            self.cursor_object.execute(sql_checker, (email,))
                            
                            if self.cursor_object.rowcount == 0:
                                sql_create = 'INSERT into users(first_name, last_name, email, phone_number, password) VALUES (%s, %s, %s, %s, %s);'
                                self.cursor_object.execute(sql_create, (first_name, last_name, email,phone_number, password))
                                self.connection_object.commit()
                                self.cursor_object.close()
                                return [{"status": 201, "data": "User Registered successfully"}], 201
                            return [{"status": 400, "data": "User Already registered with that email"}], 400
                        return [{"status": 400, "data": "Password must be provided"}], 400
                    return [{"status": 400, "data": "Phone number must be provided"}], 400
                return [{"status": 400, "data": "Email must be provided"}], 400
            return [{"status": 400, "data": "Last name required"}], 400
        return [{"status": 400, "data": "First name required"}], 400
    def sign_in(self, data):
        if 'email' in data.keys():
            if 'password' in data.keys():
                sql_checker = 'SELECT user_id, email, password, first_name, last_name from users where email = %s;'
                email = data['email']
                password = data['password']
                self.cursor_object.execute(sql_checker, (email,))
                if self.cursor_object.rowcount == 0:
                    return [{"status": 404, "data": "No User found with such mail"}], 404
                user_detail = self.cursor_object.fetchone()
                
                if check_password_hash(user_detail[2], password):
                    token = self.generate_token(user_detail[0])
                    return [{"status": 202, "data": "Successfully Authenticated", "token": token.decode()}], 202
                return [{"status": 401, "data": "Wrong password provided"}],  401
            return [{"status": 400, "data": "Please provide user password"}], 400
        return [{"status": 400, "data": "No email provided."}], 400
    def get_all_users(self):
        sql_query_all = 'SELECT user_id, first_name, last_name, email, phone_number from users;'
        self.cursor_object.execute(sql_query_all)
        if self.cursor_object.rowcount == 0:
            return [{"status": 204, "data": "No users at the moment."}], 204
        return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
        
    def get_user_by_id(self, user_id):
        sql_checker_id = 'SELECT user_id, email, phone_number, first_name, last_name from users where user_id = %s;'
        self.cursor_object.execute(sql_checker_id, (user_id,))
        if self.cursor_object.rowcount == 0:
            return [{"status": 404, "data": "No user with user_id {}.".format(user_id)}], 404
        return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
    
    def get_user_by_name(self, name):
        sql_checker_id = 'SELECT user_id, email, phone_number,  first_name, last_name from users where first_name LIKE %s;'
        self.cursor_object.execute(sql_checker_id, ('%'+name+'%',))
        if self.cursor_object.rowcount == 0:
            return [{"status": 404, "data": "No user with name {}.".format(name)}], 404
        return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
    
    def update_user(self, data):
        user_id = g.user['user_id']
        sql_check_if_user_exists = 'SELECT user_id, email, first_name, last_name from users where user_id = %s;'
        self.cursor_object.execute(sql_check_if_user_exists, (user_id,))
        if self.cursor_object.rowcount == 0:
            return [{"status": 404, "data": "No user with user_id {}.".format(user_id)}], 404
        # decode sent_data
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        phone_number = data['phone_number']
        if 'password' in data.keys():
            # password was not queried, so check if user requested update
            password = data['password']
            
            sql_update_with_pass = 'UPDATE users set email = %s, phone_number=%s, first_name = %s, last_name = %s, password = s% where user_id = %s;'
            self.cursor_object.execute(sql_update_with_pass, (email, phone_number, first_name, last_name, generate_password_hash(password)))
            self.connection_object.commit()
            self.cursor_object.close()
            return [{"status": 202, "data": "User detail Successfully updated"}], 202
        sql_update = 'UPDATE users set email = %s, phone_number = %s, first_name = %s, last_name = %s where user_id = %s;'
        self.cursor_object.execute(sql_update, (email, phone_number, first_name, last_name, user_id))
        self.connection_object.commit()
        self.cursor_object.close()
        return [{"status": 202, "data": "User detail Successfully updated, use previous password"}], 202
    def generate_token(self, user_id):
        """
        Encoding user_id to get JSON Web Tokens (JWT)

        :return: token
        """
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=15),  # Expiration Time
                'iat': datetime.utcnow(),  # Issued At
                'user_id': user_id  # payload
            }
            # create the byte string token using the payload and the SECRET key
            encoded_jwt = jwt.encode(
                payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            return encoded_jwt
        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """
        Decodes the access token from the Authorization header.

        :param token: String
        :return: Payload
        """
        try:
            payload = jwt.decode(token,
                                 current_app.config.get('JWT_SECRET_KEY'),
                                 algorithms=['HS256'])
            return payload["user_id"]
        except jwt.DecodeError:
            # Raised when a token cannot be decoded because it failed validation
            return "Token failed validation hence decode failed."
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


                        
class Comments(DbHelper,Response , db.Model):
    '''Handles feedbacks:
    ->A feedback can be created under an activity(References activity_id)
    ->Removed activity Delete-Cascades subsequent comments'''
    __tablename__ = 'comments'
    
    actual_comment_id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey(Activities.activity_id, ondelete = 'CASCADE'), nullable=False)
    comment = db.Column(db.String(1000), nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    created_on = db.Column(db.String(30))
    activities_relation_comments = db.relationship(Activities, backref = db.backref('children_to_activity_as_comments', passive_deletes=True))
    
    
    def __init__(self):
        super().__init__()

    def create(self, data):
        if 'comment' in data.keys():
 
            if 'activity_id' in data.keys():
                activity_id = data['activity_id']
                sql_check = 'SELECT activity_id from activities where activity_id = %s;'
                self.cursor_object.execute(sql_check, (activity_id,))
                if self.cursor_object.rowcount == 0:
                    return [{"status": 404, "data": "Comment cannot be added without reference activity"}], 404
                comment = data['comment']
                author_user_id = g.user['user_id']
                sql_check_user = 'SELECT user_id from users where user_id = %s;'
                self.cursor_object.execute(sql_check_user, (author_user_id,))
                if self.cursor_object.rowcount == 0:
                    return [{"status": 404, "data": "Comment cannot be posted by anonymous"}], 404
                sql = 'INSERT into comments(activity_id, comment, author_user_id, created_on) VALUES (%s, %s, %s, %s);'
                created_on = datetime.today().strftime("%d %B %Y %H:%M")
                self.cursor_object.execute(sql, (activity_id, comment, author_user_id, created_on))
                self.connection_object.commit()
                self.cursor_object.close()
                return [{"status":201, "data":"Comment Added"}], 201
            return [{"status": 400, "data": "Comment cannot be added without activity_id reference"}], 400
 
        return [{"status": 400, "data": "Comment cannot be empty"}], 400
    def query_comments(self, activity_id):
        sql_query = 'SELECT comments.actual_comment_id, comments.comment, comments.created_on, users.email from comments INNER JOIN users ON users.user_id = comments.author_user_id where activity_id = %s;'
        self.cursor_object.execute(sql_query, (activity_id,))
        if self.cursor_object.rowcount == 0:
            return [{"status": 404, "data": "No comments under this activity"}], 404
        return self.jsonify_things(self.cursor_object.description, self.cursor_object.fetchall())
    
    def delete_comment(self, actual_comment_id):
        sql_check = 'SELECT author_user_id, actual_comment_id from comments where actual_comment_id = %s;'
        self.cursor_object.execute(sql_check, (actual_comment_id,))
        if self.cursor_object.rowcount == 0:
            return [{"status": 404, "data": "No comments with such an id"}], 404
        
        comment_data = self.cursor_object.fetchone()
        if comment_data[0] == g.user['user_id']: # Check that the request comes from the creator, deny if not.
            
            sql_remove_comment = 'DELETE from comments where actual_comment_id = %s;'
            self.cursor_object.execute(sql_remove_comment, (actual_comment_id,))
            self.connection_object.commit()
            self.cursor_object.close()
            return [{"status": 200, "data": "Comment removed"}], 200
        return [{"status": 401, "data": "You can only remove the comments you created"}], 401
