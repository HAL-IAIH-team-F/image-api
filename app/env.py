import os

import dotenv

ACCESS_TOKEN_EXPIRE_MINUTES = 15
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14

dotenv.load_dotenv("./.env.local")
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
db_url = os.getenv("DB_URL")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

db_name = os.getenv("DB_NAME")


class Env:
    cors_list = os.getenv("CORS_LIST")

ENV = Env()
