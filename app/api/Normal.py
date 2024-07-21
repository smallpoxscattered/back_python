from quart import Blueprint, request, jsonify
from ..utils.gene import gene_map
import asyncio
from sqlalchemy import select
from app.database import db_session
from app.models.models import User, Leaderboard


Normal_bp = Blueprint("getMap", __name__)


@Normal_bp.route("/getMap", methods=["POST"])
async def getMap():
    data = await request.get_json()
    serial_number = data.get("serial_number")
    size = tuple(data.get("size", [20, 20]))  # 默认大小为(20, 20)
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
