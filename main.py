from fastapi import FastAPI
from routers.menu import menu
from routers.auth import auth
from routers.notice import notice
from routers.stock import stock
from routers.faq import faq
from routers.finance import finance
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:3000',
    'localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(menu.router, prefix="/app/v1")
app.include_router(auth.router, prefix="/app/v1")
app.include_router(notice.router, prefix="/app/v1")
app.include_router(stock.router, prefix="/app/v1")
app.include_router(faq.router, prefix="/app/v1")
app.include_router(finance.router, prefix="/app/v1")
