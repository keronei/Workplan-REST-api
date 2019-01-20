
from flask import Flask, Blueprint, current_app
from .api.v1.models.operations import db
from .api.v1 import version_one as v1
from instance.config import app_config



def launcher(configuration=None):
    app = Flask(__name__)
    
    if not configuration:
        configuration = app_config['development']
    app.config.from_object(configuration)
    app.register_blueprint(v1)
    db.init_app(app)
    
    return app
    

    
    