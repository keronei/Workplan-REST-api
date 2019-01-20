from functools import wraps
from flask import g, request, redirect, url_for
from app.api.v1.models.operations import Users, RevokeToken


def token_requiried(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(" ")[1]
            if RevokeToken().check_if_blacklisted(access_token):
                return [{"status": 401, "data": "Your session expired, A token was required, but yours has expired."}], 401
            user_id = Users.decode_token(access_token)
            if isinstance(user_id, int):
                logged_in_user = Users().get_user_by_id(user_id)
                if logged_in_user:
                    g.user = {'user_id': user_id}
                    return f(*args, **kwargs)
                return [{"status": 401, "data": "No user with user_id {}, Inavlid token.".format(user_id)}], 401
            return [{"status": 401, "data": user_id}], 401
                
        #return redirect(url_for('api_v1.userauthsignin'))
        return [{"status": 400, "data": "Please sign-in to process your request, A token was required."}], 400
    return decorated_function
    
