from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.database import Base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    register_time = Column(DateTime, default=datetime.utcnow)

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
    completion_time = Column(Float, nullable=False)  # 以秒为单位
    score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

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
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', backref=backref('leaderboard_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<Leaderboard Entry {self.id} User {self.user_id} Level {self.level_id} Rank {self.rank}>'