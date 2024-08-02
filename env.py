import os

import dotenv

dotenv.load_dotenv("./.env.local")
dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
