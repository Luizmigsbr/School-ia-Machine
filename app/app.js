// Plataforma de Estudos com IA - JavaScript Principal

class StudyPlatformApp {
    constructor() {
        this.apiBaseUrl = '';
        this.authToken = localStorage.getItem('authToken');
        this.currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
        this.currentSession = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.loadAIServiceStatus();
        
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    setupEventListeners() {
        // Navegação
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(e.target.getAttribute('data-section'));
            });
        });
        
        // Autenticação
        document.getElementById('loginBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('loginModal')).show();
        });
        
        document.getElementById('registerBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('registerModal')).show();
        });
        
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
        
        document.getElementById('loginSubmitBtn').addEventListener('click', () => {
            this.handleLogin();
        });
        
        document.getElementById('registerSubmitBtn').addEventListener('click', () => {
            this.handleRegister();
        });
        
        // Botões de ação
        document.getElementById('getStartedBtn').addEventListener('click', () => {
            if (this.authToken) {
                this.showSection('dashboard');
            } else {
                new bootstrap.Modal(document.getElementById('loginModal')).show();
            }
        });
        
        document.getElementById('newSessionBtn').addEventListener('click', () => {
            this.createNewSession();
        });
        
        document.getElementById('startStudyBtn').addEventListener('click', () => {
            this.createNewSession();
        });
        
        document.getElementById('endSessionBtn').addEventListener('click', () => {
            this.endCurrentSession();
        });
        
        // Chat
        document.getElementById('sendChatBtn').addEventListener('click', () => {
            this.sendChatMessage();
        });
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        
        // Enter key para formulários
        document.getElementById('loginPassword').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleLogin();
            }
        });
        
        document.getElementById('registerPassword').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleRegister();
            }
        });
    }
    
    checkAuthStatus() {
        if (this.authToken && this.currentUser) {
            this.showAuthenticatedUI();
            this.loadDashboardData();
        } else {
            this.showUnauthenticatedUI();
        }
    }
    
    showAuthenticatedUI() {
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        document.getElementById('userMenu').classList.remove('d-none');
        document.getElementById('username').textContent = this.currentUser.username;
        document.getElementById('sidebar').classList.remove('d-none');
        document.getElementById('welcomeSection').style.display = 'none';
        this.showSection('dashboard');
    }
    
    showUnauthenticatedUI() {
        document.getElementById('loginBtn').style.display = 'block';
        document.getElementById('registerBtn').style.display = 'block';
        document.getElementById('userMenu').classList.add('d-none');
        document.getElementById('sidebar').classList.add('d-none');
        document.getElementById('welcomeSection').style.display = 'block';
        this.hideAllSections();
    }
    
    showSection(sectionName) {
        this.hideAllSections();
        
        // Atualizar navegação ativa
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Mostrar seção
        document.getElementById(`${sectionName}Section`).classList.remove('d-none');
        
        // Carregar dados específicos da seção
        switch(sectionName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'progress':
                this.loadProgressData();
                break;
        }
    }
    
    hideAllSections() {
        const sections = ['dashboard', 'study', 'chat', 'progress'];
        sections.forEach(section => {
            document.getElementById(`${section}Section`).classList.add('d-none');
        });
    }
    
    async handleLogin() {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');
        
        if (!username || !password) {
            this.showError(errorDiv, 'Por favor, preencha todos os campos');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.authToken = data.access_token;
                this.currentUser = data.user;
                
                localStorage.setItem('authToken', this.authToken);
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                
                bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
                this.showAuthenticatedUI();
                
                // Limpar formulário
                document.getElementById('loginForm').reset();
                errorDiv.classList.add('d-none');
                
            } else {
                this.showError(errorDiv, data.error || 'Erro no login');
            }
        } catch (error) {
            console.error('Erro no login:', error);
            this.showError(errorDiv, 'Erro de conexão');
        }
    }
    
    async handleRegister() {
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const errorDiv = document.getElementById('registerError');
        const successDiv = document.getElementById('registerSuccess');
        
        if (!username || !email || !password) {
            this.showError(errorDiv, 'Por favor, preencha todos os campos');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess(successDiv, 'Usuário registrado com sucesso! Faça login para continuar.');
                document.getElementById('registerForm').reset();
                errorDiv.classList.add('d-none');
                
                // Fechar modal após 2 segundos
                setTimeout(() => {
                    bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
                    new bootstrap.Modal(document.getElementById('loginModal')).show();
                }, 2000);
                
            } else {
                this.showError(errorDiv, data.error || 'Erro no registro');
                successDiv.classList.add('d-none');
            }
        } catch (error) {
            console.error('Erro no registro:', error);
            this.showError(errorDiv, 'Erro de conexão');
        }
    }
    
    logout() {
        this.authToken = null;
        this.currentUser = null;
        this.currentSession = null;
        
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        
        this.showUnauthenticatedUI();
    }
    
    async loadDashboardData() {
        if (!this.authToken) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/dashboard`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateDashboard(data);
            }
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        }
    }
    
    updateDashboard(data) {
        // Atualizar estatísticas
        document.getElementById('totalSessions').textContent = data.stats.total_sessions;
        document.getElementById('totalQuestions').textContent = data.stats.total_questions;
        
        // Atualizar sessões recentes
        const recentSessionsDiv = document.getElementById('recentSessions');
        if (data.recent_sessions.length === 0) {
            recentSessionsDiv.innerHTML = '<p class="text-muted">Nenhuma sessão encontrada</p>';
        } else {
            recentSessionsDiv.innerHTML = data.recent_sessions.map(session => `
                <div class="session-card card mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted">Sessão #${session.id}</small>
                                <div>Score: ${session.score}%</div>
                            </div>
                            <div class="text-end">
                                <small class="text-muted">${this.formatDate(session.start_time)}</small>
                                <div><small>${session.duration ? Math.round(session.duration / 60) + ' min' : 'Em andamento'}</small></div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Atualizar progresso por tópico
        const topicProgressDiv = document.getElementById('topicProgress');
        if (data.progress.length === 0) {
            topicProgressDiv.innerHTML = '<p class="text-muted">Nenhum progresso registrado</p>';
        } else {
            topicProgressDiv.innerHTML = data.progress.map(progress => `
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>${progress.topic}</span>
                        <span>${progress.score}%</span>
                    </div>
                    <div class="progress mt-1">
                        <div class="progress-bar" style="width: ${progress.score}%"></div>
                    </div>
                </div>
            `).join('');
        }
    }
    
    async createNewSession() {
        if (!this.authToken) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sessions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.currentSession = data.session;
                this.showStudySession();
                this.showSection('study');
            }
        } catch (error) {
            console.error('Erro ao criar sessão:', error);
        }
    }
    
    showStudySession() {
        const studyContent = document.getElementById('studyContent');
        const endSessionBtn = document.getElementById('endSessionBtn');
        
        studyContent.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Sessão de Estudo #${this.currentSession.id}</h5>
                    <p class="text-muted">Iniciada em: ${this.formatDate(this.currentSession.start_time)}</p>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6>Adicionar Pergunta</h6>
                                    <div class="mb-3">
                                        <label class="form-label">Pergunta</label>
                                        <textarea class="form-control" id="questionText" rows="3"></textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Resposta Correta</label>
                                        <textarea class="form-control" id="answerText" rows="2"></textarea>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <label class="form-label">Dificuldade</label>
                                            <select class="form-select" id="difficulty">
                                                <option value="easy">Fácil</option>
                                                <option value="medium" selected>Médio</option>
                                                <option value="hard">Difícil</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">Tópico</label>
                                            <input type="text" class="form-control" id="topic" placeholder="Ex: Matemática">
                                        </div>
                                    </div>
                                    <button class="btn btn-primary mt-3" onclick="app.addQuestion()">Adicionar Pergunta</button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6>Perguntas da Sessão</h6>
                                    <div id="sessionQuestions">
                                        <p class="text-muted">Nenhuma pergunta adicionada ainda</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        endSessionBtn.classList.remove('d-none');
    }
    
    async addQuestion() {
        const questionText = document.getElementById('questionText').value;
        const answerText = document.getElementById('answerText').value;
        const difficulty = document.getElementById('difficulty').value;
        const topic = document.getElementById('topic').value;
        
        if (!questionText || !answerText) {
            alert('Por favor, preencha a pergunta e a resposta');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sessions/${this.currentSession.id}/questions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question_text: questionText,
                    answer_text: answerText,
                    difficulty: difficulty,
                    topic: topic
                })
            });
            
            if (response.ok) {
                // Limpar formulário
                document.getElementById('questionText').value = '';
                document.getElementById('answerText').value = '';
                document.getElementById('topic').value = '';
                
                // Atualizar lista de perguntas (simplificado)
                const questionsDiv = document.getElementById('sessionQuestions');
                const currentCount = questionsDiv.children.length;
                questionsDiv.innerHTML = `<p class="text-success">${currentCount + 1} pergunta(s) adicionada(s)</p>`;
            }
        } catch (error) {
            console.error('Erro ao adicionar pergunta:', error);
        }
    }
    
    async endCurrentSession() {
        if (!this.currentSession) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sessions/${this.currentSession.id}/end`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                alert(`Sessão finalizada! Score: ${data.session.score}%`);
                
                this.currentSession = null;
                document.getElementById('endSessionBtn').classList.add('d-none');
                document.getElementById('studyContent').innerHTML = `
                    <div class="text-center">
                        <p>Sessão finalizada com sucesso!</p>
                        <button class="btn btn-primary" id="startStudyBtn">Iniciar Nova Sessão</button>
                    </div>
                `;
                
                // Reconfigurar event listener
                document.getElementById('startStudyBtn').addEventListener('click', () => {
                    this.createNewSession();
                });
                
                this.loadDashboardData();
            }
        } catch (error) {
            console.error('Erro ao finalizar sessão:', error);
        }
    }
    
    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        const messagesDiv = document.getElementById('chatMessages');
        
        // Adicionar mensagem do usuário
        this.addChatMessage(messagesDiv, message, 'user');
        input.value = '';
        
        // Mostrar indicador de digitação
        const typingDiv = this.addTypingIndicator(messagesDiv);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            // Remover indicador de digitação
            typingDiv.remove();
            
            if (response.ok) {
                this.addChatMessage(messagesDiv, data.response, 'ai', data.service_used);
            } else {
                this.addChatMessage(messagesDiv, 'Desculpe, ocorreu um erro ao processar sua mensagem.', 'ai');
            }
        } catch (error) {
            console.error('Erro no chat:', error);
            typingDiv.remove();
            this.addChatMessage(messagesDiv, 'Erro de conexão. Tente novamente.', 'ai');
        }
    }
    
    addChatMessage(container, message, sender, service = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        bubble.textContent = message;
        
        const timestamp = document.createElement('div');
        timestamp.className = 'chat-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        if (service && sender === 'ai') {
            timestamp.textContent += ` • ${service}`;
        }
        
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(timestamp);
        container.appendChild(messageDiv);
        
        // Scroll para baixo
        container.scrollTop = container.scrollHeight;
    }
    
    addTypingIndicator(container) {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai';
        typingDiv.innerHTML = `
            <div class="chat-bubble ai">
                <div class="loading-spinner"></div>
                <span class="ms-2">IA está digitando...</span>
            </div>
        `;
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;
        return typingDiv;
    }
    
    async loadAIServiceStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/ai/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateAIServiceStatus(data.services);
            }
        } catch (error) {
            console.error('Erro ao carregar status dos serviços:', error);
        }
    }
    
    updateAIServiceStatus(services) {
        const statusDiv = document.getElementById('aiServiceStatus');
        statusDiv.innerHTML = Object.entries(services).map(([name, info]) => `
            <div class="service-status">
                <div class="status-indicator ${info.available ? 'online' : 'offline'}"></div>
                <span>${name}</span>
                <span class="ms-auto">${info.available ? 'Online' : 'Offline'}</span>
            </div>
        `).join('');
    }
    
    async loadProgressData() {
        if (!this.authToken) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/progress`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderProgressChart(data.progress);
            }
        } catch (error) {
            console.error('Erro ao carregar progresso:', error);
        }
    }
    
    renderProgressChart(progressData) {
        const ctx = document.getElementById('progressChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: progressData.map(p => p.topic),
                datasets: [{
                    label: 'Progresso (%)',
                    data: progressData.map(p => p.score),
                    backgroundColor: 'rgba(13, 110, 253, 0.8)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    showError(element, message) {
        element.textContent = message;
        element.classList.remove('d-none');
    }
    
    showSuccess(element, message) {
        element.textContent = message;
        element.classList.remove('d-none');
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleString('pt-BR');
    }
}

// Inicializar aplicação
const app = new StudyPlatformApp();

