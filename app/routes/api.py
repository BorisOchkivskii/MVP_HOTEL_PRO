from flask import Blueprint, request, jsonify, current_app
from app.services.gigachat import get_auth_token, send_to_gigachat, conversation_history

bp = Blueprint('api', __name__)

@bp.route('/api/chat', methods=['POST'])
def chat():
    if not current_app.config['AUTHORIZATION_KEY']:
        return jsonify({"error": "AUTHORIZATION_KEY не настроен"}), 500

    try:
        data = request.get_json(force=True)
        message = data.get("message", "").strip()
        passport_received = bool(data.get("passport_received", False))
        is_first_message = bool(data.get("is_first_message", True))
    except Exception:
        return jsonify({"error": "Некорректный JSON"}), 400

    if not message:
        return jsonify({"error": "Пустое сообщение"}), 400

    passport_status_text = "получен" if passport_received else "НЕ получен"

    if is_first_message:
        greeting_instruction = "Это первое сообщение гостя. Начни свой ответ с тёплого приветствия (например, «Здравствуйте!» или «Добрый день!»)."
    else:
        greeting_instruction = "Это продолжение диалога. Не нужно повторять приветствие, просто дай ответ по существу."

    system_prompt = f"""Ты — радушный и опытный менеджер отеля, который помогает гостям с заселением.
Общайся живо, по-человечески, с теплотой и лёгким юмором (если уместно). Можешь использовать эмодзи. Старайся разнообразить формулировки, не повторяй одни и те же фразы.

Текущий статус получения паспорта гостя: {passport_status_text}.

{greeting_instruction}

Твоя задача — ответить гостю, следуя правилам:
- Если статус получения паспорта гостя "НЕ получен": вежливо объясни, что для заселения сначала необходимо предоставить паспорт, и предложи перейти по ссылке: https://example.com/passport , а затем нажать кнопку "Загрузить паспорт"
- Если статус получения паспорта гостя "получен": обязательно сообщи, что паспорт уже получен, и следующим этапом будет оплата залога. После этого сообщения ТЫ ОБЯЗАН считать, что паспорт уже предоставлен. В следующих сообщениях НЕ проси его, НЕ упоминай, что он не получен, и НЕ предлагай ссылку для загрузки.

Не добавляй лишней информации, не выдумывай другие требования. Будь дружелюбен и краток."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    try:
        token = get_auth_token()
        answer = send_to_gigachat(messages, token)

        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": answer})
        # Ограничиваем историю последними 6 записями (3 пары)
        while len(conversation_history) > 6:
            conversation_history.pop(0)

        return jsonify({"response": answer})
    except Exception as e:
        print(f"Ошибка в /api/chat: {e}")
        return jsonify({"error": "Ошибка при обращении к GigaChat"}), 500