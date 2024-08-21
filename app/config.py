import os
from dotenv import load_dotenv

load_dotenv()

ENGINE = os.environ['ENGINE']
ECHO = False
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", 'secret')
JWT_TOKEN_LOCATION = ["headers"]

SMS_ON = bool(int(os.environ['SMS_ON']))
SMSAERO_EMAIL = os.environ['SMSAERO_EMAIL']
SMSAERO_API_KEY = os.environ['SMSAERO_API_KEY']