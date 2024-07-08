from quart import Blueprint, jsonify

hello_bp = Blueprint('hello', __name__)

@hello_bp.route('/')
async def hello():
    return 'hello'


