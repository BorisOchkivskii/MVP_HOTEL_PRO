import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY', '')
    GIGACHAT_API_URL = 'https://api.giga.chat/v1'
    AUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
    SCOPE = 'GIGACHAT_API_PERS'
    MODEL = 'GigaChat-2'