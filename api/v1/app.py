#!/usr/bin/python3
"""register blueprint of routes to main application"""
from flask import Flask, make_response, jsonify
from flask import Flask, request
from flask_cors import CORS
from models import storage
from api.v1.views import app_views
import os
from flask_jwt_extended import JWTManager
from datetime import timedelta
from authlib.integrations.flask_client import OAuth

storage_t = os.environ.get('HBNB_TYPE_STORAGE')
host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('HBNB_API_PORT', 5000)

app = Flask(__name__)
#required for google auth
app.secret_key = "your_secret_key"

oauth = OAuth(app)

#required for JWT auth
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
#app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) #Optional: set token expiration
jwt = JWTManager(app)


CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown_db(exception):
    """close database connection after session"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """return 404 error on page not found"""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(host, port)
