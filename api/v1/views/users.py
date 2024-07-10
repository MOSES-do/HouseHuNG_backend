#!/usr/bin/python3
"""routes for users"""
from sqlalchemy import create_engine
from flask import Flask, jsonify, abort, request
from models import storage
from models.registration import Registration
from api.v1.views import app_views
from models.base_model import Base
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import storage_t

engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                format('housing_dev',
                                       'housing_pwd',
                                       'localhost',
                                       'housing_db'))


if storage_t == 'db':
    Session = storage._DBStorage__session

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

@app.before_request
def create_tables():
    Base.metadata.create_all(engine)

@app_views.route('/registered_users', methods=['GET'],
                 strict_slashes=False, endpoint='registered_users')
def registered_users():
    """get all registered users from strage"""
    registered_users = []
    s = storage.all(Registration)
    for obj in s.values():
        registered_users.append(obj.to_dict())
    return jsonify(all_users)


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
    password = data.get('password_hash')

    if not email:
        return jsonify({'error': 'Missing data'}), 400

    session = Session()
    if session.query(Registration).filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already exists'}), 400


    # Save new user to database
    new_user = User(
                    email=email,
                    )
    if password: # thsi line is for testing purpose here
        new_user.set_password(password)
    session.add(new_user)
    session.commit()
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
    
    #access_token = create_access_token(identity=user.id)
    #return jsonify({'token': access_token}), 200
    return jsonify({}), 200



# Protected endpoint
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    session = Session()
    user = session.query(Registration).get(current_user_id)
    session.close()

    return jsonify({'message': f'Hello, {user.email}!'}), 200



"""
@app_views.route('/users/<user_id>', methods=['GET'],
                 strict_slashes=False, endpoint='single_user')
def single_user(user_id):
    
    #return state based on id
   
    s = storage.all(User)
    for key, value in s.items():
        if value.id == user_id:
            return jsonify(value.to_dict())
    abort(404, description="State not found")


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
