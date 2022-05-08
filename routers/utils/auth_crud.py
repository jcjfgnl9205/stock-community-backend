from sqlalchemy.orm import Session
from .. import models
from ..auth import schemas
from datetime import datetime

# User Info取得
def get_user(db: Session, username: str):
    return db.query(models.User)\
            .filter(models.User.username == username)\
            .first()

# User Insert
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db=db, username=db_user.username)

# RefreshToekn Info取得
def get_refresh_token(db: Session, username: str):
    return db.query(models.UserRefresh)\
            .filter(models.UserRefresh.username == username)\
            .first()

# RefreshToekn Update or Insert
def update_refresh_token(db: Session, username: str, refresh_token: str):
    if get_refresh_token(db=db, username=username):
        db_user = db.query(models.UserRefresh).filter(models.UserRefresh.username == username).first()
        db_user.refresh_token = refresh_token
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return get_user(db=db, username=db_user.username)

    db_user = models.UserRefresh(username=username, refresh_token=refresh_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db=db, username=db_user.username)
