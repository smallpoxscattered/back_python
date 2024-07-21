import ast
from quart import Blueprint, request, jsonify
from ..utils.gene import gene_map, auto_map
from PIL import Image
import numpy as np
import io
import asyncio
from sqlalchemy import select
from app.database import db_session
from app.models.models import User, Leaderboard


Normal_bp = Blueprint("getMap", __name__)


@Normal_bp.route("/getMap", methods=["POST"])
async def getMap():
    data = await request.get_json()
    serial_number = data.get("serial_number")
    size = int(data.get("size", "20"))
    size = (size, size)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, gene_map, serial_number, size)

    response = {
        "result_map": result[0],
        "path_map": result[1],
        "middle_wall": result[2],
        "picture": result[3]
    }

    return jsonify(response)


@Normal_bp.route("/leaderboard", methods=["POST"])
async def get_leaderboard():
    data = await request.json
    level_id = data.get("level_id")
    difficulty = data.get("difficulty")

    if not level_id:
        return jsonify({"error": "Missing level ID"}), 400

    with db_session() as session:
        query = (
            select(Leaderboard, User.username)
            .join(User, User.id == Leaderboard.user_id)
            .filter(Leaderboard.level_id == level_id)
        )

        if difficulty is not None:
            query = query.filter(Leaderboard.difficulty == difficulty)

        query = query.order_by(Leaderboard.rank)

        leaderboard_entries = session.execute(query).all()

        if not leaderboard_entries:
            return (
                jsonify(
                    {
                        "level": level_id,
                        "difficulty": difficulty,
                        "message": f"No leaderboard data for level {level_id}{' and difficulty ' + str(difficulty) if difficulty is not None else ''}",
                        "leaderboard": [],
                    }
                ),
                200,
            )

        leaderboard_data = [
            {
                "rank": entry.Leaderboard.rank,
                "username": entry.username,
                "completion_time": entry.Leaderboard.completion_time,
                "difficulty": entry.Leaderboard.difficulty,
                "timestamp": entry.Leaderboard.timestamp.isoformat(),
            }
            for entry in leaderboard_entries
        ]

        return (
            jsonify({"level": level_id, "difficulty": difficulty, "leaderboard": leaderboard_data}),
            200,
        )


@Normal_bp.route('/upload', methods=['POST'])
async def upload_file():
    files = await request.files
    if 'image' not in files:
        return jsonify({'error': 'No file part'}), 400
    file = files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    form = await request.form
    size_str = form.get('size')

    if not size_str:
        return jsonify({'error': 'Size parameter is missing'}), 400
    
    try:
        # 将字符串转换为元组
        size = tuple(ast.literal_eval(size_str))
        if not isinstance(size, tuple) or len(size) != 2 or not all(isinstance(i, int) for i in size):
            raise ValueError("Invalid size format")
    except (ValueError, SyntaxError):
        return jsonify({'error': 'Invalid size parameter'}), 400
    if file:
        file_bytes = file.read()  # 移除 await
        
        image = Image.open(io.BytesIO(file_bytes))
        
        numpy_image = np.array(image)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, auto_map, numpy_image, size)
        response = {
            "result_map": result[0],
            "path_map": result[1],
            "middle_wall": result[2],
            "picture": result[3]
        }

        return jsonify(response)
