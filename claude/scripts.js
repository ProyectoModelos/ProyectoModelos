// Leer el usuario desde localStorage
const loggedInUser = localStorage.getItem('loggedInUser');
const sendButton = document.getElementById('send-button');
const userQuestionInput = document.getElementById('user-question');
const chatBox = document.getElementById('chat-box');
const sendChatMessageButton = document.getElementById('send-chat-message');
const chatMessageInput = document.getElementById('chat-message');
const previousQuestionsLink = document.getElementById('previous-questions-link');

// Actualizar el saludo
if (loggedInUser) {
    document.getElementById('greeting').innerHTML = `Good evening, <span>${loggedInUser}</span>`;
} else {
    document.getElementById('greeting').innerHTML = `Good evening, <span>Guest</span>`;
}

let previousQuestions = JSON.parse(localStorage.getItem('previousQuestions')) || [];

// Manejo del envío de preguntas
sendButton.addEventListener('click', () => {
    const question = userQuestionInput.value.trim();

    if (question) {
        previousQuestions.push(question);
        localStorage.setItem('previousQuestions', JSON.stringify(previousQuestions));
        document.querySelector('.container').classList.add('hidden');
        document.querySelector('.new-screen').classList.remove('hidden');
    }
});

// Mostrar preguntas previas
previousQuestionsLink.addEventListener('click', () => {
    if (previousQuestions.length > 0) {
        alert('Preguntas previas:\n' + previousQuestions.join('\n'));
    } else {
        alert('No hay preguntas previas.');
    }
});

// Manejo del chat
function addMessage(message, isUser = true) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendChatMessageButton.addEventListener('click', () => {
    const userMessage = chatMessageInput.value.trim();
    if (userMessage) {
        addMessage(userMessage, true);
        chatMessageInput.value = '';
        setTimeout(() => {
            addMessage(`Claude responde: "${userMessage}" es una excelente pregunta.`, false);
        }, 1000);
    }
});

chatMessageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendChatMessageButton.click();
    }
});
