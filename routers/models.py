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


metadata.create_all(bind=engine)
