from sqlalchemy.orm import Session
from .. import models
from ..auth import schemas
from datetime import datetime

# User Info取得
def get_user(db: Session, username: str):
    return db.query(models.USER)\
            .filter(models.USER.username == username)\
            .first()

def get_user_for_email(db: Session, email: str):
    return db.query(models.USER)\
            .filter(models.USER.email == email)\
            .first()

# User Insert
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.USER(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db=db, username=db_user.username)

# User Update
def update_user(db: Session, username: str, user: schemas.UserUpdate):
    db_user = db.query(models.USER).filter(models.USER.username == username).first()
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.zipcode = user.zipcode
    db_user.address1 = user.address1
    db_user.address2 = user.address2
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db=db, username=db_user.username)

# User password update
def update_password(db: Session, user: models.USER):
    db.add(user)
    db.commit()
    db.refresh(user)
    return get_user(db=db, username=user.username)

# RefreshToekn Info取得
def get_refresh_token(db: Session, username: str):
    return db.query(models.USER_REFRESH_TOKEN)\
            .filter(models.USER_REFRESH_TOKEN.username == username)\
            .first()

# RefreshToekn Update or Insert
def update_refresh_token(db: Session, username: str, refresh_token: str):
    if get_refresh_token(db=db, username=username):
        db_user = db.query(models.USER_REFRESH_TOKEN).filter(models.USER_REFRESH_TOKEN.username == username).first()
        db_user.refresh_token = refresh_token
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return get_user(db=db, username=db_user.username)

    db_user = models.USER_REFRESH_TOKEN(username=username, refresh_token=refresh_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db=db, username=db_user.username)


def auth_num_check(db: Session, user: schemas.PasswordFind):
    return db.query(models.USER)\
            .filter(models.USER.email == user.email)\
            .filter(models.USER.auth_number == user.authNum)\
            .first()
