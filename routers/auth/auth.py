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

    def encode_token(self, username: str):
        payload = {
            'exp' : datetime.utcnow() + timedelta(minutes=self.access_token_expires_minutes),
            'iat' : datetime.utcnow(),
            'scope': 'access_token',
            'sub' : username
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, self.algorithm)
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            #여기서 새토큰 생ㅅ어?
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
        
    def encode_refresh_token(self, username: str):
        payload = {
            'exp' : datetime.utcnow() + timedelta(hours=self.refresh_token_expires_hours),
            'iat' : datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : username
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.secret_key, self.algorithm)
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
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
        hashed_password = auth_handler.encode_password(user.password)
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
    
    access_token = auth_handler.encode_token(user.username)
    refresh_token = auth_handler.encode_refresh_token(user.username)
    auth_crud.update_refresh_token(db=db, username=user.username, refresh_token=refresh_token)

    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized useddrs can access this info'
