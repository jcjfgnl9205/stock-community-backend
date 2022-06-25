from db.session import Base, metadata, engine
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime

# USER INFO TABLE
class USER(Base):
    __tablename__ = "USER"

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

    USER_REFRESH_TOKEN = relationship("USER_REFRESH_TOKEN", back_populates="USER")
    NOTICE_DETAIL_DAT = relationship("NOTICE_DETAIL_DAT", back_populates="USER")
    NOTICE_DETAIL_COMMENT_DAT = relationship("NOTICE_DETAIL_COMMENT_DAT", back_populates="USER")
    NOTICE_DETAIL_VOTE_DAT = relationship("NOTICE_DETAIL_VOTE_DAT", back_populates="USER")
    
    STOCK_MST = relationship("STOCK_MST", back_populates="USER")
    STOCK_DETAIL_DAT = relationship("STOCK_DETAIL_DAT", back_populates="USER")
    STOCK_DETAIL_COMMENT_DAT = relationship("STOCK_DETAIL_COMMENT_DAT", back_populates="USER")
    STOCK_DETAIL_VOTE_DAT = relationship("STOCK_DETAIL_VOTE_DAT", back_populates="USER")


# USER REFRESH TOKEN INFO TABLE
class USER_REFRESH_TOKEN(Base):
    __tablename__ = "USER_REFRESH_TOKEN"

    refresh_token_id = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    username = Column(Integer, ForeignKey("USER.username"))

    USER = relationship("USER", back_populates="USER_REFRESH_TOKEN")

# NOTICE TABLE
class NOTICE_DETAIL_DAT(Base):
    __tablename__ = "NOTICE_DETAIL_DAT"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("USER.id"))

    USER = relationship("USER", back_populates="NOTICE_DETAIL_DAT")
    NOTICE_DETAIL_COMMENT_DAT = relationship("NOTICE_DETAIL_COMMENT_DAT", back_populates="NOTICE_DETAIL_DAT")
    NOTICE_DETAIL_VOTE_DAT = relationship("NOTICE_DETAIL_VOTE_DAT", back_populates="NOTICE_DETAIL_DAT")

# NOTICE COMMENT TABLE
class NOTICE_DETAIL_COMMENT_DAT(Base):
    __tablename__ = "NOTICE_DETAIL_COMMENT_DAT"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("USER.id"))
    notice_id = Column(Integer, ForeignKey("NOTICE_DETAIL_DAT.id"))

    USER = relationship("USER", back_populates="NOTICE_DETAIL_COMMENT_DAT")
    NOTICE_DETAIL_DAT = relationship("NOTICE_DETAIL_DAT", back_populates="NOTICE_DETAIL_COMMENT_DAT")

# NOTICE VOTE TABLE
class NOTICE_DETAIL_VOTE_DAT(Base):
    __tablename__ = "NOTICE_DETAIL_VOTE_DAT"

    id = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, default=False, nullable=False)
    hate = Column(Integer, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("USER.id"))
    notice_id = Column(Integer, ForeignKey("NOTICE_DETAIL_DAT.id"))

    USER = relationship("USER", back_populates="NOTICE_DETAIL_VOTE_DAT")
    NOTICE_DETAIL_DAT = relationship("NOTICE_DETAIL_DAT", back_populates="NOTICE_DETAIL_VOTE_DAT")


# FAQ TABLE
class FAQ_MST(Base):
    __tablename__ = "FAQ_MST"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    flg = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)


class STOCK_MST(Base):
    __tablename__ = "STOCK_MST"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    show_name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = user_id = Column(Integer, ForeignKey("USER.id"))

    USER = relationship("USER", back_populates="STOCK_MST")
    STOCK_DETAIL_DAT = relationship("STOCK_DETAIL_DAT", back_populates="STOCK_MST")


class STOCK_DETAIL_DAT(Base):
    __tablename__ = "STOCK_DETAIL_DAT"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("USER.id"))
    stock_mst_id = Column(Integer, ForeignKey("STOCK_MST.id"))

    USER = relationship("USER", back_populates="STOCK_DETAIL_DAT")
    STOCK_MST = relationship("STOCK_MST", back_populates="STOCK_DETAIL_DAT")
    STOCK_DETAIL_COMMENT_DAT = relationship("STOCK_DETAIL_COMMENT_DAT", back_populates="STOCK_DETAIL_DAT")
    STOCK_DETAIL_VOTE_DAT = relationship("STOCK_DETAIL_VOTE_DAT", back_populates="STOCK_DETAIL_DAT")


class STOCK_DETAIL_COMMENT_DAT(Base):
    __tablename__ = "STOCK_DETAIL_COMMENT_DAT"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    user_id = Column(Integer, ForeignKey("USER.id"))
    stock_id = Column(Integer, ForeignKey("STOCK_DETAIL_DAT.id"))

    USER = relationship("USER", back_populates="STOCK_DETAIL_COMMENT_DAT")
    STOCK_DETAIL_DAT = relationship("STOCK_DETAIL_DAT", back_populates="STOCK_DETAIL_COMMENT_DAT")


class STOCK_DETAIL_VOTE_DAT(Base):
    __tablename__ = "STOCK_DETAIL_VOTE_DAT"

    id = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, default=False, nullable=False)
    hate = Column(Integer, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("USER.id"))
    stock_id = Column(Integer, ForeignKey("STOCK_DETAIL_DAT.id"))

    USER = relationship("USER", back_populates="STOCK_DETAIL_VOTE_DAT")
    STOCK_DETAIL_DAT = relationship("STOCK_DETAIL_DAT", back_populates="STOCK_DETAIL_VOTE_DAT")


class MENU_MST(Base):
    __tablename__ = "MENU_MST"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_sub = Column(String, nullable=False)
    path = Column(String, nullable=False)
    show_order = Column(Integer, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    MENU_SUB_MST = relationship("MENU_SUB_MST", back_populates="MENU_MST")

class MENU_SUB_MST(Base):
    __tablename__ = "MENU_SUB_MST"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_sub = Column(String, nullable=False)
    path = Column(String, nullable=False)
    show_order = Column(Integer, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    menu_id = Column(Integer, ForeignKey("MENU_MST.id"))
    
    MENU_MST = relationship("MENU_MST", back_populates="MENU_SUB_MST")

metadata.create_all(bind=engine)
