#!/usr/bin/python3
"""routes for users"""
from flask import Flask, jsonify, abort, request, url_for, session, redirect
from models import storage
from models.registration import Registration
from models.logout import TokenBlacklist
from api.v1.views import app_views
from requests_oauthlib import OAuth2Session
from flask_jwt_extended import JWTManager,create_access_token, jwt_required, get_jwt_identity, get_jti
#from authlib.integrations.flask_client import OAuth
from os import getenv, urandom

Session = storage._DBStorage__session

app = Flask(__name__)
# manage user authentication on page request
jwt = JWTManager(app)
#oauth = OAuth(app)

CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
redirect_uri = 'http://localhost:5500/frontend/index.html'  # Client-side app callback URL

authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'


@app_views.route('/registered_users', methods=['GET'],
                 strict_slashes=False, endpoint='registered_users')
def registered_users():
    """get all registered users from strage"""
    registered_users = []
    s = storage.all(Registration)
    for obj in s.values():
        registered_users.append(obj.to_dict())
    return jsonify(registered_users)


@app_views.route('/reg_users/<user_id>', methods=['GET'],
                 strict_slashes=False, endpoint='single_user')
def single_user(user_id):
    #return user based on id
    #print(user_id)
    s = storage.all(Registration)
    for key, value in s.items():
        if value.id == user_id:
            #print(value.id, user_id)
            return jsonify(value.to_dict())
    abort(404, description="User not found")


# Register endpoint
@app_views.route("/register", methods=["POST"],
                 strict_slashes=False, endpoint='register')
def register():
    """register new user"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400, 'Not a JSON')
    if "email" not in data:
        abort(400, 'Missing email') 
    
    email = data.get('email')
    password = data.get('password')
    if not email:
        return jsonify({'error': 'Missing data'}), 400

    session = Session()
    if session.query(Registration).filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already exists'}), 401

    # Save new user to database
    new_user = Registration(
                    email=email,
                    )
    if password: # thsi line is for testing purpose here
        new_user.set_password(password)
    #session.add(new_user)
    storage.new(new_user)
    #session.commit()
    storage.save()
    session.close()

    return jsonify({'message': 'User registered successfully'}), 201



# Login endpoint
@app_views.route("/login", methods=["POST"],
                 strict_slashes=False, endpoint='login_user')
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Missing data'}), 400

    session = Session()
    user = session.query(Registration).filter_by(email=email).first()
    session.close()

    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity={'id':user.id, 'email':user.email})
    return jsonify({'token': access_token}), 200



# Function to get current user info
@app_views.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_identity = get_jwt_identity()
    session = Session()
    user = session.query(Registration).filter_by(id=current_user_identity['id']).first()
    if user:
        user_info = {
            'id': user.id,
            'email': user.email
            # Add other fields as needed
        }
        session.close()
        return jsonify(user_info), 200
    else:
        session.close()
        return jsonify({"msg": "User not found"}), 404


# Logout endpoint
@app_views.route("/logout", methods=["POST"],
                 strict_slashes=False, endpoint='logout')
@jwt_required()
def logout():
    jti = get_jti(request.headers['Authorization'].split(' ')[1])
    #print(jti)
    session = Session()
    blacklist_token = TokenBlacklist(jti=jti)
    storage.new(blacklist_token)
    storage.save()
    session.close()
    return jsonify({'message': 'Successfully logged out'}), 200


# Check if a token is blacklisted 
# part of logout functionality
@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    session = Session()
    token = session.query(TokenBlacklist).filter_by(jti=jti).first()
    session.close()
    return token is not None


# Protected endpoint
@app_views.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    session = Session()
    user = session.query(Registration).get(current_user_id)
    session.close()

    return jsonify({'message': f'Hello, {user.email}!'}), 200

@app_views.route('/login/google')
def login_google():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['openid', 'email', 'profile'])
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline')
    session['oauth_state'] = state
    return jsonify({'authorization_url': authorization_url, 'response': "ok"})


@app_views.route('/token', methods=['POST'])
def token():
    code = request.json.get('code')
    google = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = google.fetch_token(token_url, client_secret=client_secret, code=code)
    user_info = google.get(user_info_url).json()
    user_email = user_info.get('email')
    #print(user_email)
    if user_email:
        # Check if user exists, if not, add to the database
        session = Session()
        user = session.query(Registration).filter_by(email=user_email).first()
        if not user:
            user = Registration(email=user_email)
            storage.new(user)
            storage.save()

        # Generate JWT token
        #create a JWT token for the user
        access_token = create_access_token(identity={'id':user.id, 'email':user.email})
        session.close()
        return jsonify({'token': access_token}), 200
        
    return jsonify({'error': 'Failed to fetch user email'}), 400














































"""
@app_views.route("/users/<user_id>", methods=["PUT"],
                 strict_slashes=False, endpoint='update_user')
def update_user(user_id):
    
    update user object by ID
    user_json = request.get_json(silent=True)
    if user_json is None:
        abort(400, 'Not a JSON')
    user_obj = storage.get(User, user_id)
    if user_obj is None:
        abort(404)
    for key, val in user_json.items():
        cond: below is a key exclusion to ensure
        id, created_at & updated_at don't get updated
        if key not in ["id", "created_at", "updated_at", "email"]:
            setattr(user_obj, key, val)
    user_obj.save()
    return jsonify(user_obj.to_dict())


@app_views.route('/users/<user_id>', methods=['DELETE'],
                 strict_slashes=False, endpoint='del_user')
def del_user(user_id):
    delete user based on id
   
    entity = storage.get(User, user_id)
    if entity is None:
        abort(404, description="State not found")
    storage.delete(entity)
    storage.save()
    return jsonify({})
"""
