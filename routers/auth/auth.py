import os
import jwt
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..utils import auth_crud
from . import schemas


load_dotenv()

class Auth():
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    access_token_expires_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expires_hours = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS"))

    # Passwordをhashする
    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    # Passwordを確認する
    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user: schemas.User):
        payload = {
            'exp' : datetime.utcnow() + timedelta(minutes=self.access_token_expires_minutes),
            'iat' : datetime.utcnow(),
            'scope': 'access_token',
            'sub' : user.username,
            'user_id' : user.id,
            'is_active': user.is_active,
            'is_staff': user.is_staff
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, self.algorithm)
            if (payload['scope'] == 'access_token'):
                return {'username' : payload['sub'], 'user_id': payload['user_id']}
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            #여기서 새토큰 생ㅅ어?
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
        
    def encode_refresh_token(self, user: schemas.User):
        payload = {
            'exp' : datetime.utcnow() + timedelta(hours=self.refresh_token_expires_hours),
            'iat' : datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : user.username,
            'user_id' : user.id,
            'is_active': user.is_active,
            'is_staff': user.is_staff
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.secret_key, self.algorithm)
            if (payload['scope'] == 'refresh_token'):
                payload['exp'] = datetime.utcnow() + timedelta(minutes=self.access_token_expires_minutes)
                payload['iat'] = datetime.utcnow()
                payload['scope'] = 'access_token'
                return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
                
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')


auth_handler = Auth()
security = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401:{"user": "Not authorized"}}
)

def get_user(db: Session, username: str):
    user = auth_crud.get_user(db=db, username=username)
    if user:
        return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db=db, username=username)
    # userが存在しない場合、Exceptionを発生する
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    # Passwordが一致しない場合、Exceptionを発生する
    if not auth_handler.verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(status_code=400, detail="The passwords do not match")
    # mail認証を行なっていない場合、Exceptionを発生する
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user


@router.post("/signup/duplicate_id_check")
async def duplicate_id_check(user: schemas.UserInfoCheck, db: Session = Depends(get_db)):
    """
    <h2>会員登録</h2>
    会員登録する時、usernameを重複チェックする
    """
    
    _user = get_user(db=db, username=user.username)
    if _user:
        raise HTTPException(status_code=409, detail="username already exists")
    return {"username": user.username, "result": True}


@router.post("/signup/duplicate_email_check")
async def duplicate_id_check(user: schemas.UserInfoCheck, db: Session = Depends(get_db)):
    """
    <h2>会員登録</h2>
    会員登録する時、emailを重複チェックする
    """
    
    _user = auth_crud.get_user_for_email(db=db, email=user.email)
    if _user:
        raise HTTPException(status_code=409, detail="email already exists")
    return {"email": user.email, "result": True}


@router.post("/signup", response_model=schemas.User)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    <h2>SignUp</h2>
    会員登録を行う
    """
    if auth_crud.get_user(db=db, username=user.username) != None:
        raise HTTPException(status_code=409, detail="username already exists")

    try:
        # password暗号化して登録
        user.password = auth_handler.get_password_hash(user.password)
        return auth_crud.create_user(db=db, user=user)
    except:
        raise HTTPException(status_code=409, detail="username already exists")


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(login: schemas.Login, db: Session = Depends(get_db)):
    """
    <h2>login</h2>
    ユーザーがログインに成功した場合、<b>access token, refresh token</b>を返します。
    """
    user = authenticate_user(db=db, username=login.username, password=login.password)

    access_token = auth_handler.encode_token(user=user)
    refresh_token = auth_handler.encode_refresh_token(user=user)
    auth_crud.update_refresh_token(db=db, username=user.username, refresh_token=refresh_token)

    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return auth_handler.decode_token(token)


@router.get('/{username}/MyInfo', response_model=schemas.User)
def get_user_api(username: str
            , current_user: str = Depends(get_current_user)
            , db: Session = Depends(get_db)):
    """
    <h2>loginしているユーザー情報</h2>
    """
    return get_user(db=db, username=username)


@router.put('/{username}/MyInfo', response_model=schemas.User)
def get_user_api(username: str
            , user: schemas.UserUpdate
            , current_user: str = Depends(get_current_user)
            , db: Session = Depends(get_db)):
    """
    <h2>loginしているユーザー情報更新</h2>
    """
    return auth_crud.update_user(db=db, username=username, user=user)


@router.put('/{username}/pw')
def update_password_api(username: str
            , password: schemas.UserPassword
            , current_user: str = Depends(get_current_user)
            , db: Session = Depends(get_db)):
    """
    <h2>loginしているユーザーPASSWORD変更</h2>
    """
    user = authenticate_user(db=db, username=username, password=password.oldPassword)
    user.password = auth_handler.get_password_hash(password.password)
    return auth_crud.update_password(db=db, user=user)


@router.post("/forgot-password", response_model=schemas.User)
async def forgot_password(user: schemas.PasswordFind
                    , db: Session = Depends(get_db)):
    _user = auth_crud.get_user_for_email(db=db, email=user.email)
    if not _user:
        raise HTTPException(status_code=401, detail="登録されているEmailが存在しません。")
    # 認証メール送信
    
    return _user


@router.post("/forgot-password/auth-number", response_model=schemas.User)
async def forgot_password_authnum(user: schemas.PasswordFind
                    , db: Session = Depends(get_db)):
    _user = auth_crud.auth_num_check(db=db, user=user)
    if not _user:
        raise HTTPException(status_code=401, detail="認証番号が間違っています。")
    return _user
