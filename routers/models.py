from db.session import Base, metadata, engine
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime

# USER INFO TABLE
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    zipcode = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=False, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    auth_number = Column(String)

    user_refresh = relationship("UserRefresh", back_populates="user")
    notice = relationship("Notice", back_populates="user")
    notice_comment = relationship("NoticeComment", back_populates="user")
    notice_vote = relationship("NoticeVote", back_populates="user")


# USER REFRESH TOKEN INFO TABLE
class UserRefresh(Base):
    __tablename__ = "user_refresh"

    refresh_token_id = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    username = Column(Integer, ForeignKey("user.username"))

    user = relationship("User", back_populates="user_refresh")

# NOTICE TABLE
class Notice(Base):
    __tablename__ = "notice"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="notice")
    notice_comment = relationship("NoticeComment", back_populates="notice")
    notice_vote = relationship("NoticeVote", back_populates="notice")

# NOTICE COMMENT TABLE
class NoticeComment(Base):
    __tablename__ = "notice_comment"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    notice_id = Column(Integer, ForeignKey("notice.id"))

    user = relationship("User", back_populates="notice_comment")
    notice = relationship("Notice", back_populates="notice_comment")

# NOTICE VOTE TABLE
class NoticeVote(Base):
    __tablename__ = "notice_vote"

    id = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, default=False, nullable=False)
    hate = Column(Integer, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    notice_id = Column(Integer, ForeignKey("notice.id"))

    user = relationship("User", back_populates="notice_vote")
    notice = relationship("Notice", back_populates="notice_vote")


metadata.create_all(bind=engine)
