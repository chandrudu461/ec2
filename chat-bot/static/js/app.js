class ChatBot {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.errorToast = document.getElementById('errorToast');
        this.charCount = document.getElementById('charCount');
        this.clearChatBtn = document.getElementById('clearChat');
        this.toggleThemeBtn = document.getElementById('toggleTheme');
        
        this.isTyping = false;
        this.messageCount = 0;
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkBackendHealth();
        this.applyTheme(this.currentTheme);
        this.autoResizeTextarea();
    }
    
    setupEventListeners() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input events
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.updateSendButton();
            this.autoResizeTextarea();
        });
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // Theme toggle
        this.toggleThemeBtn.addEventListener('click', () => this.toggleTheme());
        
        // Error toast close
        this.errorToast.querySelector('.close-toast').addEventListener('click', () => {
            this.hideErrorToast();
        });
        
        // Auto-hide error toast
        setTimeout(() => this.hideErrorToast(), 5000);
    }
    
    async checkBackendHealth() {
        try {
            this.showLoading('Connecting to AI Assistant...');
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.hideLoading();
                this.updateBotStatus('online');
            } else {
                throw new Error('Backend not healthy');
            }
        } catch (error) {
            this.hideLoading();
            this.updateBotStatus('offline');
            this.showError('Failed to connect to AI Assistant. Please try again later.');
        }
    }
    
    updateBotStatus(status) {
        const statusElement = document.querySelector('.bot-status');
        statusElement.className = `bot-status ${status}`;
        statusElement.innerHTML = `
            <i class="fas fa-circle"></i>
            ${status.charAt(0).toUpperCase() + status.slice(1)}
        `;
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
        
        const counter = this.charCount.parentElement;
        counter.classList.remove('warning', 'error');
        
        if (count > 400) {
            counter.classList.add('error');
        } else if (count > 300) {
            counter.classList.add('warning');
        }
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateCharCount();
        this.updateSendButton();
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    max_length: 100,
                    temperature: 0.7
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to get response');
            }
            
            const data = await response.json();
            
            // Simulate typing delay for better UX
            await this.simulateTypingDelay(data.reply.length);
            
            this.hideTyping();
            this.addMessage(data.reply, 'bot');
            
        } catch (error) {
            this.hideTyping();
            this.showError(error.message);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }
    
    addMessage(text, sender) {
        this.messageCount++;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.style.animationDelay = '0ms';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.formatTime(new Date());
        
        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        
        // Animate text typing for bot messages
        if (sender === 'bot') {
            this.typeText(textDiv, text);
        } else {
            textDiv.textContent = text;
        }
        
        // Scroll to bottom
        setTimeout(() => this.scrollToBottom(), 100);
    }
    
    async typeText(element, text) {
        element.textContent = '';
        const words = text.split(' ');
        
        for (let i = 0; i < words.length; i++) {
            element.textContent += (i > 0 ? ' ' : '') + words[i];
            this.scrollToBottom();
            await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 50));
        }
    }
    
    async simulateTypingDelay(textLength) {
        // Simulate realistic typing delay based on text length
        const baseDelay = 1000;
        const charDelay = Math.min(textLength * 30, 2000);
        await new Promise(resolve => setTimeout(resolve, baseDelay + charDelay));
    }
    
    showTyping() {
        this.isTyping = true;
        this.typingIndicator.classList.add('show');
        this.updateSendButton();
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('show');
        this.updateSendButton();
    }
    
    showLoading(message = 'Loading...') {
        this.loadingOverlay.querySelector('p').textContent = message;
        this.loadingOverlay.classList.add('show');
    }
    
    hideLoading() {
        this.loadingOverlay.classList.remove('show');
    }
    
    showError(message) {
        this.errorToast.querySelector('.error-message').textContent = message;
        this.errorToast.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => this.hideErrorToast(), 5000);
    }
    
    hideErrorToast() {
        this.errorToast.classList.remove('show');
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    clearChat() {
        // Keep only the welcome message
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        this.messagesContainer.innerHTML = '';
        if (welcomeMessage) {
            this.messagesContainer.appendChild(welcomeMessage.cloneNode(true));
        }
        this.messageCount = 0;
        this.addMessage('Chat cleared! How can I help you?', 'bot');
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = this.toggleThemeBtn.querySelector('i');
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});

// Service Worker Registration for Better Performance
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Utility functions for enhanced UX
class ChatUtils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
    
    static sanitizeHTML(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Error boundary for better error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // Could send to logging service in production
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // Could send to logging service in production
});