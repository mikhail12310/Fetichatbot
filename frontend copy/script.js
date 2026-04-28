const API_URL = 'http://localhost:8000'; // Change this to your hosted URL for GitHub Pages

const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const fileUpload = document.getElementById('file-upload');
const toastContainer = document.getElementById('toast-container');

function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'system'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text || userInput.disabled) return;

    setLoadingState(true);
    addMessage(text, true);

    const loadingMsg = addMessage('Thinking...', false);
    loadingMsg.querySelector('.message-content').classList.add('loading-dots');

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        loadingMsg.remove();
        addMessage(data.response, false);
    } catch (error) {
        loadingMsg.remove();
        addMessage("Sorry, I couldn't connect to the server. Make sure the backend is running.", false);
        console.error('Error:', error);
    } finally {
        setLoadingState(false);
    }
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showToast(`Uploading ${file.name}...`);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            showToast(`Success: ${data.message}`);
            addMessage(`System: New file "${file.name}" added to the database.`, false);
        } else {
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast("Upload failed. Check backend connection.", "error");
        console.error('Error:', error);
    }
}

// Element Selectors
const btnUploadInit = document.getElementById('btn-upload-init');
const btnExampleInit = document.getElementById('btn-example-init');
const landingOptions = document.getElementById('landing-options');

const FETII_SUGGESTIONS = [
    "How many trips were completed in total?",
    "What is the average number of passengers per trip?",
    "Which pick-up address is the most popular?",
    "How many unique users have booked a trip?",
    "Show the distribution of trips by hour of the day."
];

function setLoadingState(isLoading) {
    userInput.disabled = isLoading;
    sendBtn.disabled = isLoading;
    fileUpload.disabled = isLoading;
    btnExampleInit.style.pointerEvents = isLoading ? 'none' : 'auto';
    btnUploadInit.style.pointerEvents = isLoading ? 'none' : 'auto';
    
    if (isLoading) {
        sendBtn.style.opacity = '0.5';
        userInput.placeholder = "Processing...";
    } else {
        sendBtn.style.opacity = '1';
        userInput.placeholder = "Ask a question about your data...";
        userInput.focus();
    }
}

async function initializeApp(useExample = true) {
    if (landingOptions.style.display === 'none' && !useExample) return;
    
    landingOptions.style.display = 'none';
    setLoadingState(true);
    const loadingMsg = addMessage('Initializing database and summarizing data...', false);
    loadingMsg.querySelector('.message-content').classList.add('loading-dots');
    
    try {
        const response = await fetch(`${API_URL}/init`);
        const data = await response.json();
        loadingMsg.remove();
        addMessage(data.summary, false);
        
        if (useExample) {
            showSuggestions(FETII_SUGGESTIONS);
        }
    } catch (error) {
        loadingMsg.remove();
        addMessage("Welcome! Please make sure the backend is running.", false);
        console.error('Initialization error:', error);
    } finally {
        setLoadingState(false);
    }
}

function showSuggestions(questions) {
    const container = document.getElementById('suggestions-container');
    container.innerHTML = '';
    container.classList.remove('hidden');
    
    questions.forEach(q => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';
        chip.textContent = q;
        chip.onclick = () => {
            userInput.value = q;
            handleSendMessage();
            container.classList.add('hidden'); // Hide after selection
        };
        container.appendChild(chip);
    });
}

btnExampleInit.addEventListener('click', () => initializeApp(true));

btnUploadInit.addEventListener('click', () => {
    fileUpload.click();
});

// Update handleFileUpload logic to initialize app after upload if in landing state
async function processFileUpload(event) {
    const isInLanding = landingOptions.style.display !== 'none';
    await handleFileUpload(event);
    if (isInLanding) {
        initializeApp(false);
    }
}

sendBtn.addEventListener('click', handleSendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});
fileUpload.addEventListener('change', processFileUpload);
