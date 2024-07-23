from quart import Blueprint, request, jsonify
from quart_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from sqlalchemy import select
from app.database import db_session
from app.models.models import User, GameRecord, Leaderboard
from sqlalchemy import delete
from datetime import datetime, timezone

protect_bp = Blueprint('protect', __name__)


@protect_bp.route('/check_session', methods=['GET'])
@jwt_required
async def check_session():
    current_user = get_jwt_identity()
    claims = get_jwt_claims()
    token_session_id = claims.get('session_id')
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "用户未找到"}), 404
    if user.session_id != token_session_id:
        return jsonify({"message": "会话过期或无效", "valid": False}), 401
    return jsonify({"message": "会话有效", "valid": True}), 200


@protect_bp.route('/logout', methods=['POST'])
@jwt_required
async def logout():
    current_user = get_jwt_identity()
    
    async with db_session() as session:
        result = await session.execute(select(User).filter_by(username=current_user))
        user = result.scalar_one_or_none()
        
        if user:
            user.session_id = None
            await session.commit()
    
    return jsonify({"message": "登录成功"}), 200


@protect_bp.route('/protected', methods=['GET'])
@jwt_required
async def protected():
    current_user = get_jwt_identity()
    
    with db_session() as session:
        user = session.execute(select(User).filter_by(username=current_user)).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User does not exist"}), 404
        
        game_records = session.execute(
            select(GameRecord).filter_by(user_id=user.id).order_by(GameRecord.timestamp.desc())
        ).scalars().all()
        
        if not game_records:
            return jsonify({
                "username": current_user,
                "game_records": [],
                "message": "This user has no game records yet"
            }), 200
        
        # Build response data
        records = []
        for record in game_records:
            records.append({
                "level": record.level_id,
                "completion_time": record.completion_time,
                "score": record.score,
                "timestamp": record.timestamp.isoformat()
            })
        
        return jsonify({
            "username": current_user,
            "game_records": records
        }), 200


@protect_bp.route('/level_record', methods=['POST'])
@jwt_required
async def get_level_record():
    current_user = get_jwt_identity()
    data = await request.json
    level_id = data.get('level_id')
    
    if not level_id:
        return jsonify({"error": "Missing level ID"}), 400
    
    with db_session() as session:
        # Get user
        user = session.execute(select(User).filter_by(username=current_user)).scalar_one_or_none()
        
        if not user:
            return jsonify({"error": "User does not exist"}), 404
        
        # Get game records for the specified level
        game_records = session.execute(
            select(GameRecord).filter_by(user_id=user.id, level_id=level_id).order_by(GameRecord.timestamp.desc())
        ).scalars().all()
        
        # Handle case with no game records
        if not game_records:
            return jsonify({
                "username": current_user,
                "level": level_id,
                "game_records": [],
                "message": f"This user has no game records for level {level_id} yet"
            }), 200
        
        # Build response data
        records = []
        for record in game_records:
            records.append({
                "completion_time": record.completion_time,
                "score": record.score,
                "timestamp": record.timestamp.isoformat()
            })
        
        return jsonify({
            "username": current_user,
            "level": level_id,
            "game_records": records
        }), 200
        
        
@protect_bp.route('/add_record', methods=['POST'])
@jwt_required
async def add_game_record():
    current_user = get_jwt_identity()
    data = await request.json

    level_id = data.get('level_id')
    completion_time = data.get('completion_time')
    score = data.get('score')
    difficulty = data.get('difficulty') 

    if not all([level_id, completion_time, score, difficulty]):
        return jsonify({"错误": "缺少必要的信息"}), 400

    if not isinstance(difficulty, int) or difficulty < 1:
        return jsonify({"错误": "难度必须是正整数"}), 400

    with db_session() as session:
        user = session.execute(select(User).filter_by(username=current_user)).scalar_one_or_none()
        
        if not user:
            return jsonify({"错误": "用户不存在"}), 404

        # 添加新的游戏记录
        new_record = GameRecord(
            user_id=user.id,
            level_id=level_id,
            completion_time=completion_time,
            score=score,
            difficulty=difficulty,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(new_record)

        # 更新排行榜
        # 获取当前关卡和难度的前10名
        top_10 = session.execute(
            select(Leaderboard)
            .filter_by(level_id=level_id, difficulty=difficulty)
            .order_by(Leaderboard.completion_time)
            .limit(10)
        ).scalars().all()
        # 检查新记录是否能进入前10
        if len(top_10) < 10 or completion_time < top_10[-1].completion_time:
            # 删除该用户在此关卡和难度的旧排行榜记录（如果存在）
            delete_stmt = delete(Leaderboard).where(
                (Leaderboard.user_id == user.id) &
                (Leaderboard.level_id == level_id) &
                (Leaderboard.difficulty == difficulty)
            )
            session.execute(delete_stmt)

            # 添加新的排行榜记录
            new_leaderboard_entry = Leaderboard(
                user_id=user.id,
                level_id=level_id,
                completion_time=completion_time,
                difficulty=difficulty,
                timestamp=datetime.now(timezone.utc),
                rank=0
            )
            session.add(new_leaderboard_entry)
            session.commit()

            leaderboard_entries = session.execute(
                select(Leaderboard)
                .filter_by(level_id=level_id, difficulty=difficulty)
                .order_by(Leaderboard.completion_time)
                .limit(10)
            ).scalars().all()
            for rank, entry in enumerate(leaderboard_entries, start=1):
                entry.rank = rank
                if rank > 10:
                    session.delete(entry)

        session.commit()

        return jsonify({
            "message": "游戏记录添加成功，排行榜已更新",
            "record": {
                "username": current_user,
                "level": level_id,
                "completion_time": completion_time,
                "score": score,
                "difficulty": difficulty,
                "timestamp": new_record.timestamp.isoformat()
            }
        }), 201


