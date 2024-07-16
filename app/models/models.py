from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.database import Base
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    register_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    session_id = Column(String(255), default=None)  # 新添加的字段

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class GameRecord(Base):
    __tablename__ = 'game_record'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    level_id = Column(Integer, nullable=False)
    completion_time = Column(Float, nullable=False)  
    score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship('User', backref=backref('game_records', lazy='dynamic'))

    def __repr__(self):
        return f'<GameRecord {self.id} User {self.user_id} Level {self.level_id}>'


class Leaderboard(Base):
    __tablename__ = 'leaderboard'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    level_id = Column(Integer, nullable=False)
    completion_time = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 改为整数
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship('User', backref=backref('leaderboard_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<Leaderboard Entry {self.id} User {self.user_id} Level {self.level_id} Rank {self.rank} Difficulty {self.difficulty}>'
