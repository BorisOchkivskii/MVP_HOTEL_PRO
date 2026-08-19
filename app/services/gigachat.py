import uuid
import time
from typing import Dict, Any, List

import requests
import urllib3
from app.config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_token_cache: Dict[str, Any] = {"token": None, "fetched_at": 0.0}
conversation_history: List[Dict[str, str]] = []

def get_auth_token():
    global _token_cache
    if _token_cache["token"] and (time.time() - _token_cache["fetched_at"]) < 25 * 60:
        return _token_cache["token"]

    AUTHORIZATION_KEY = Config.AUTHORIZATION_KEY
    if not AUTHORIZATION_KEY:
        raise ValueError("AUTHORIZATION_KEY не задан")

    headers = {
        "Authorization": f"Bearer {AUTHORIZATION_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
    }
    data = {"scope": Config.SCOPE}

    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}

    try:
        print("Запрашиваю access_token GigaChat...")
        response = session.post(
            Config.AUTH_URL,
            headers=headers,
            data=data,
            timeout=(10, 30),
            verify=False,
        )
        print(f"OAuth GigaChat ответил: HTTP {response.status_code}")
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Не удалось получить access_token")

        _token_cache["token"] = access_token
        _token_cache["fetched_at"] = time.time()
        return access_token
    except Exception as e:
        print(f"Ошибка получения токена GigaChat: {e}")
        raise

def send_to_gigachat(messages: List[Dict[str, str]], token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = {
        "model": Config.MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 1000,
    }

    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}

    try:
        print("Отправляю запрос в GigaChat...")
        response = session.post(
            f"{Config.GIGACHAT_API_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=(10, 30),
            verify=False,
        )
        print(f"GigaChat ответил: HTTP {response.status_code}")
        response.raise_for_status()
        result = response.json()
        if "choices" in result and result["choices"] and "message" in result["choices"][0]:
            answer = result["choices"][0]["message"].get("content")
            if answer:
                return answer.strip()
        raise ValueError(f"Неожиданная структура ответа GigaChat: {result}")
    except requests.exceptions.Timeout:
        print("Таймаут при обращении к GigaChat")
        return "Извините, сейчас ответ ИИ занимает слишком много времени. Пожалуйста, попробуйте ещё раз."
    except requests.exceptions.RequestException as e:
        print(f"Сетевая ошибка при обращении к GigaChat: {e}")
        return "Извините, сейчас не удалось связаться с ИИ. Пожалуйста, попробуйте ещё раз."
    except Exception as e:
        print(f"Ошибка при запросе к GigaChat: {e}")
        return "Извините, произошла техническая ошибка. Попробуйте позже."