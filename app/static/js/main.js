let passportReceived = false;
let isFirstMessage = true;

const passportButton = document.getElementById('passportButton');
const passportStatus = document.getElementById('passportStatus');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const answerBox = document.getElementById('answerBox');

passportButton.addEventListener('click', () => {
    if (!passportReceived) {
        passportReceived = true;
        passportStatus.textContent = 'Паспорт загружен';
        passportButton.disabled = true;
    }
});

function showStatus(text) {
    answerBox.textContent = text;
}

function showAnswer(text) {
    const linkedText = text.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank">$1</a>'
    );
    answerBox.innerHTML = linkedText;
}

sendButton.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    if (!message) {
        alert('Введите сообщение');
        return;
    }

    sendButton.disabled = true;
    messageInput.disabled = true;

    showStatus('Читаю');
    setTimeout(() => showStatus('Думаю'), 1000);
    setTimeout(() => showStatus('Пишу'), 2000);

    setTimeout(async () => {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: message,
                    passport_received: passportReceived,
                    is_first_message: isFirstMessage
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            showAnswer(data.response || 'Нет ответа');
            if (isFirstMessage) {
                isFirstMessage = false;
            }
        } catch (error) {
            console.error('Ошибка:', error);
            showAnswer('Извините, произошла ошибка при обращении к ИИ.');
        } finally {
            sendButton.disabled = false;
            messageInput.disabled = false;
        }
    }, 3000);
});