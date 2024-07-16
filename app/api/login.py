from quart import Blueprint, request, jsonify
from app.models.models import User
from app.database import db_session
import uuid
from quart_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
async def register():
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400
    
    new_user = User(username=username)
    new_user.set_password(password)
    db_session.add(new_user)
    db_session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
async def login():
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session_id = str(uuid.uuid4())
        
        # 更新用户的session_id
        user.session_id = session_id
        db_session.commit()
        
        access_token = create_access_token(identity=username)
        
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401



