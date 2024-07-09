from quart import Blueprint, request, jsonify
from quart_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import select
from app.database import db_session
from app.models.models import User, GameRecord, Leaderboard
from datetime import datetime, timezone

protect_bp = Blueprint('protect', __name__)


@protect_bp.route('/check_session', methods=['GET'])
@jwt_required()
async def check_session():
    current_user = get_jwt_identity()
    claims = get_jwt()
    token_session_id = claims.get('session_id')
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "用户未找到"}), 404
    if user.session_id != token_session_id:
        return jsonify({"message": "会话过期或无效", "valid": False}), 401
    return jsonify({"message": "会话有效", "valid": True}), 200


@protect_bp.route('/protected', methods=['GET'])
@jwt_required
async def protected():
    current_user = get_jwt_identity()
    
    with db_session() as session:
        user = session.execute(select(User).filter_by(username=current_user)).scalar_one_or_none()
        if not user:
            return jsonify({"错误": "用户不存在"}), 404
        
        game_records = session.execute(
            select(GameRecord).filter_by(user_id=user.id).order_by(GameRecord.timestamp.desc())
        ).scalars().all()
        
        if not game_records:
            return jsonify({
                "用户名": current_user,
                "游戏记录": [],
                "消息": "该用户还没有游戏记录"
            }), 200
        
        # 构建响应数据
        records = []
        for record in game_records:
            records.append({
                "关卡": record.level_id,
                "完成时间": record.completion_time,
                "得分": record.score,
                "时间戳": record.timestamp.isoformat()
            })
        
        return jsonify({
            "用户名": current_user,
            "游戏记录": records
        }), 200


@protect_bp.route('/level_record', methods=['POST'])
@jwt_required
async def get_level_record():
    current_user = get_jwt_identity()
    data = await request.json
    level_id = data.get('level_id')
    
    if not level_id:
        return jsonify({"错误": "缺少关卡ID"}), 400
    
    with db_session() as session:
        # 获取用户
        user = session.execute(select(User).filter_by(username=current_user)).scalar_one_or_none()
        
        if not user:
            return jsonify({"错误": "用户不存在"}), 404
        
        # 获取指定关卡的游戏记录
        game_records = session.execute(
            select(GameRecord).filter_by(user_id=user.id, level_id=level_id).order_by(GameRecord.timestamp.desc())
        ).scalars().all()
        
        # 处理没有游戏记录的情况
        if not game_records:
            return jsonify({
                "用户名": current_user,
                "关卡": level_id,
                "游戏记录": [],
                "消息": f"该用户在关卡 {level_id} 还没有游戏记录"
            }), 200
        
        # 构建响应数据
        records = []
        for record in game_records:
            records.append({
                "完成时间": record.completion_time,
                "得分": record.score,
                "时间戳": record.timestamp.isoformat()
            })
        
        return jsonify({
            "用户名": current_user,
            "关卡": level_id,
            "游戏记录": records
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

        if len(top_10) < 10 or completion_time < top_10[-1].completion_time:
            session.execute(
                select(Leaderboard)
                .filter_by(user_id=user.id, level_id=level_id, difficulty=difficulty)
                .delete()
            )

            # 添加新的排行榜记录
            new_leaderboard_entry = Leaderboard(
                user_id=user.id,
                level_id=level_id,
                completion_time=completion_time,
                difficulty=difficulty,
                rank=0  # 临时排名，稍后更新
            )
            session.add(new_leaderboard_entry)

            # 重新计算并更新排名
            leaderboard_entries = session.execute(
                select(Leaderboard)
                .filter_by(level_id=level_id, difficulty=difficulty)
                .order_by(Leaderboard.completion_time)
            ).scalars().all()

            for rank, entry in enumerate(leaderboard_entries, start=1):
                entry.rank = rank
                if rank > 10:
                    session.delete(entry)

        session.commit()

        return jsonify({
            "消息": "游戏记录添加成功，排行榜已更新",
            "记录": {
                "用户名": current_user,
                "关卡": level_id,
                "完成时间": completion_time,
                "得分": score,
                "难度": difficulty,
                "时间戳": new_record.timestamp.isoformat()
            }
        }), 201


