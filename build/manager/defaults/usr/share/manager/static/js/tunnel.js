// Remote Access Console - WebSocket Terminal Client
// Handles SSH/VNC/RDP connections through WebSocket tunnel

class TunnelClient {
    constructor() {
        this.ws = null;
        this.term = null;
        this.fitAddon = null;
        this.currentAgent = null;
        this.currentService = 'ssh';
        this.agents = [];
        this.originalTitle = document.title;
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;

        this.init();
    }

    async init() {
        this.initTerminal();
        this.setupEventListeners();

        // Await agents load BEFORE auto-connect check
        await this.fetchAgents();
        this.checkAutoConnect();
    }

    initTerminal() {
        this.term = new Terminal({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: '"Cascadia Code", "Fira Code", "Consolas", monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#aeafad',
                black: '#000000',
                red: '#cd3131',
                green: '#0dbc79',
                yellow: '#e5e510',
                blue: '#2472c8',
                magenta: '#bc3fbc',
                cyan: '#11a8cd',
                white: '#e5e5e5',
                brightBlack: '#666666',
                brightRed: '#f14c4c',
                brightGreen: '#23d18b',
                brightYellow: '#f5f543',
                brightBlue: '#3b8eea',
                brightMagenta: '#d670d6',
                brightCyan: '#29b8db',
                brightWhite: '#e5e5e5'
            },
            allowProposedApi: true
        });

        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);

        const webLinksAddon = new WebLinksAddon.WebLinksAddon();
        this.term.loadAddon(webLinksAddon);

        this.term.open(document.getElementById('terminal'));
        this.fitAddon.fit();

        const handleResize = () => {
            try {
                this.fitAddon.fit();
                const dims = { cols: this.term.cols, rows: this.term.rows };
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'resize',
                        ...dims
                    }));
                }
            } catch (e) {
                console.error('Error resizing:', e);
            }
        };

        window.addEventListener('resize', handleResize);
        setTimeout(handleResize, 100);

        this.term.onResize((size) => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'resize',
                    cols: size.cols,
                    rows: size.rows
                }));
            }
        });

        // Welcome message
        this.term.writeln('\x1b[1;36m╔════════════════════════════════════════════════════════════╗\x1b[0m');
        this.term.writeln('\x1b[1;36m║\x1b[0m         \x1b[1;33mRemote Access Console - WebSocket Tunnel\x1b[0m         \x1b[1;36m║\x1b[0m');
        this.term.writeln('\x1b[1;36m╚════════════════════════════════════════════════════════════╝\x1b[0m');
        this.term.writeln('');
        this.term.writeln('\x1b[90mSelect an agent from the sidebar to start a session...\x1b[0m');
        this.term.writeln('');
    }

    setupEventListeners() {
        // Solo configurar listeners si los elementos existen (página principal)
        const refreshBtn = document.getElementById('refresh-agents');
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.resetAndReload());

        const searchInput = document.getElementById('search-agents');
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => this.resetAndReload(), 500);
            });
        }

        const agentsList = document.getElementById('agents-list');
        if (agentsList) {
            agentsList.addEventListener('scroll', (e) => this.handleScroll(e));
            agentsList.addEventListener('click', (e) => this.handleAgentClick(e));
        }

        const modalClose = document.getElementById('modal-close');
        if (modalClose) modalClose.addEventListener('click', () => this.closeModal());

        const modalCancel = document.getElementById('modal-cancel');
        if (modalCancel) modalCancel.addEventListener('click', () => this.closeModal());

        const modalConnect = document.getElementById('modal-connect');
        if (modalConnect) modalConnect.addEventListener('click', () => this.connectToAgent());

        document.querySelectorAll('.service-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.service-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.currentService = e.currentTarget.dataset.service;

                const usernameInput = document.getElementById('username-input');
                if (usernameInput) {
                    if (this.currentService === 'ssh' || this.currentService === 'rdp') {
                        usernameInput.classList.remove('hidden');
                    } else {
                        usernameInput.classList.add('hidden');
                    }
                }
            });
        });

        const disconnectBtn = document.getElementById('btn-disconnect');
        if (disconnectBtn) disconnectBtn.addEventListener('click', () => this.disconnect());

        const fullscreenBtn = document.getElementById('btn-fullscreen');
        if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        this.term.onData(data => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                const hexData = Array.from(data)
                    .map(char => char.charCodeAt(0).toString(16).padStart(2, '0'))
                    .join('');
                this.ws.send(JSON.stringify({ data: hexData }));
            }
        });
    }

    async fetchAgents() {
        if (this.isLoading || !this.hasMore) return;

        this.isLoading = true;
        const container = document.getElementById('agents-list');
        const search = document.getElementById('search-agents')?.value || '';
        const limit = 50;

        try {
            if (this.currentPage === 1 && container) {
                container.innerHTML = '<div class="loading">Loading agents...</div>';
            }

            let url = `/manager/v1/public/tunnel/agents?page=${this.currentPage}&limit=${limit}`;
            if (search) url += `&q=${encodeURIComponent(search)}`;

            const response = await fetch(url);
            const data = await response.json();
            const newAgents = data.agents || [];

            if (this.currentPage === 1) {
                this.agents = newAgents;
                if (container) container.innerHTML = '';
            } else {
                this.agents = [...this.agents, ...newAgents];
            }

            this.hasMore = newAgents.length === limit;
            this.currentPage++;

            this.appendAgents(newAgents, container);

            if (this.agents.length === 0 && container) {
                container.innerHTML = '<div class="loading">No agents available</div>';
            }

        } catch (error) {
            console.error('Error loading agents:', error);
            if (this.currentPage === 1 && container) {
                this.showError('Failed to load agents');
                container.innerHTML = '<div class="loading">Error loading data</div>';
            }
        } finally {
            this.isLoading = false;
        }
    }

    resetAndReload() {
        this.currentPage = 1;
        this.agents = [];
        this.hasMore = true;
        this.fetchAgents();
    }

    handleScroll(e) {
        const { scrollTop, scrollHeight, clientHeight } = e.target;
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            this.fetchAgents();
        }
    }

    appendAgents(agents, container) {
        if (!agents || agents.length === 0 || !container) return;

        const html = agents.map(agent => {
            const services = agent.info?.available_services || [];
            const project = agent.info?.project || 'Unknown';
            return `
                <div class="agent-card" data-agent-id="${agent.agent_id}">
                    <div class="agent-header">
                        <span class="agent-name">${agent.hostname}</span>
                        <span class="agent-status"></span>
                    </div>
                    <div class="agent-services">
                        ${project} ${services.map(s => `<span class="service-tag">${s.toUpperCase()}</span>`).join('')}
                    </div>
                </div>
            `;
        }).join('');

        container.insertAdjacentHTML('beforeend', html);
    }

    handleAgentClick(e) {
        const card = e.target.closest('.agent-card');
        if (card) {
            const agentId = card.dataset.agentId;
            this.showAgentModal(agentId);
        }
    }

    showAgentModal(agentId) {
        const agent = this.agents.find(a => a.agent_id === agentId);
        if (!agent) return;

        this.currentAgent = agent;

        const infoContainer = document.getElementById('agent-info');
        if (!infoContainer) return;

        infoContainer.innerHTML = `
            <div class="info-row">
                <span class="info-label">Hostname:</span>
                <span>${agent.hostname}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Agent ID:</span>
                <span>${agent.agent_id}</span>
            </div>
            <div class="info-row">
                <span class="info-label">OS:</span>
                <span>${agent.info?.system || 'Unknown'} ${agent.info?.architecture || ''}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Services:</span>
                <span>${(agent.info?.available_services || []).join(', ')}</span>
            </div>
        `;

        const modal = document.getElementById('agent-modal');
        if (modal) modal.classList.remove('hidden');
    }

    closeModal() {
        const modal = document.getElementById('agent-modal');
        if (modal) modal.classList.add('hidden');
    }

    connectToAgent() {
        console.log('Connect button clicked');
        if (!this.currentAgent) {
            console.error('No agent selected');
            return;
        }

        let username = null;
        if (this.currentService === 'ssh' || this.currentService === 'rdp') {
            const input = document.getElementById('ssh-username');
            if (input) username = input.value.trim();
            if (!username) {
                alert('Please enter a username');
                return;
            }
        }

        this.closeModal();

        const params = new URLSearchParams();
        params.append('agent', this.currentAgent.agent_id);
        params.append('service', this.currentService);
        if (username) params.append('user', username);

        const url = `${window.location.pathname}?${params.toString()}`;
        console.log('Opening session URL:', url);

        const win = window.open(url, '_blank');
        if (!win) {
            alert('Pop-up blocked. Please allow pop-ups to open remote sessions.');
        }
    }

    async checkAutoConnect(retries = 10) {
        console.log('Checking for auto-connect...');
        const params = new URLSearchParams(window.location.search);
        const agentId = params.get('agent');

        if (!agentId) return;

        console.log(`Auto-connect: Looking for agent ${agentId}`);

        for (let i = 0; i < retries; i++) {
            const agent = this.agents.find(a => a.agent_id === agentId);
            if (agent) {
                console.log(`✅ Agent found: ${agent.hostname}`);
                this.currentAgent = agent;
                this.currentService = params.get('service') || 'ssh';
                const username = params.get('user');
                await this.startSession(username);
                return;
            }

            if (i === retries - 1) {
                console.error('❌ Agent not found after retries');
                this.showError(`Agent ${agentId} not found. It may be offline.`);
                return;
            }

            console.log(`Retry ${i + 1}/${retries}: Agent not loaded yet...`);
            await new Promise(r => setTimeout(r, 500));
        }
    }

    async startSession(username) {
        console.log('Starting session for:', this.currentAgent?.hostname);

        // ✅ Ocultar TODOS los elementos de la UI cuando se conecta
        const welcomeScreen = document.getElementById('welcome-screen');
        const connectionPanel = document.getElementById('connection-panel');
        const sidebar = document.getElementById('sidebar');
        const agentList = document.getElementById('agents-list'); // ✅ AGENT-LIST OCULTO
        const header = document.getElementById('header-content'); // ✅ Header OCULTO


        // ✅ Ocultar los elementos
        if (welcomeScreen) welcomeScreen.classList.add('hidden');
        if (connectionPanel) connectionPanel.classList.remove('hidden');
        if (sidebar) sidebar.classList.add('hidden');
        if (agentList) agentList.style.display = 'none'; // ✅ OCULTAR agent-list   
        if (header) header.style.display = 'none'; // ✅ OCULTAR header    


        setTimeout(() => this.term.focus(), 50);

        // Actualizar headers SOLO si existen
        const agentNameEl = document.getElementById('current-agent-name');
        const serviceEl = document.getElementById('current-service');
        if (agentNameEl) agentNameEl.textContent = this.currentAgent.hostname;
        if (serviceEl) serviceEl.textContent = this.currentService.toUpperCase();

        document.title = `${this.currentAgent.hostname} - Remote Access Console`;

        this.term.clear();
        const connMsg = username ?
            `→ Connecting to ${username}@${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...` :
            `→ Connecting to ${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...`;
        this.term.writeln(`\x1b[1;32m${connMsg}\x1b[0m`);

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl = `${protocol}//${window.location.host}/manager/v1/public/tunnel/ws/agents/${this.currentAgent.agent_id}`;

        const params = new URLSearchParams();
        params.append('service', this.currentService);
        if (username) params.append('username', username);
        wsUrl += `?${params.toString()}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.term.writeln('\x1b[1;32m✓ Connected!\x1b[0m');
                this.term.writeln('');
                this.updateConnectionStatus(true);
                this.term.focus();
            };

            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'data' && message.data) {
                        const hexData = message.data;
                        const match = hexData.match(/.{1,2}/g);
                        if (match) {
                            const bytes = new Uint8Array(match.map(byte => parseInt(byte, 16)));
                            const text = new TextDecoder("utf-8").decode(bytes);
                            this.term.write(text);
                        }
                    } else if (message.status === 'closed') {
                        this.term.writeln('\r\n\x1b[1;33m✗ Connection closed by remote host\x1b[0m');
                        this.disconnect();
                    } else if (message.error) {
                        this.term.writeln(`\r\n\x1b[1;31m✗ Error: ${message.error}\x1b[0m`);
                    }
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.term.writeln('\r\n\x1b[1;31m✗ Connection error\x1b[0m');
                this.updateConnectionStatus(false);
            };

            this.ws.onclose = () => {
                this.term.writeln('\r\n\x1b[1;33m✗ Disconnected\x1b[0m');
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('Connection error:', error);
            this.term.writeln(`\r\n\x1b[1;31m✗ Failed to connect: ${error.message}\x1b[0m`);
            this.updateConnectionStatus(false);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        const params = new URLSearchParams(window.location.search);
        if (params.has('agent')) {
            window.close();
        }

        // ✅ Restaurar TODOS los elementos de la UI
        const connectionPanel = document.getElementById('connection-panel');
        const welcomeScreen = document.getElementById('welcome-screen');
        const sidebar = document.getElementById('sidebar');
        const agentList = document.getElementById('agents-list'); // ✅ AGENT-LIST VISIBLE
        const header = document.getElementById('header-content'); // ✅ Header VISIBLE

        if (connectionPanel) connectionPanel.classList.add('hidden');
        if (welcomeScreen) welcomeScreen.classList.remove('hidden');
        if (sidebar) sidebar.classList.remove('hidden');
        if (agentList) agentList.style.display = ''; // ✅ MOSTRAR agent-list
        if (header) header.classList.remove('hidden'); // ✅ MOSTRAR header

        document.title = this.originalTitle;
        this.term.clear();
        this.term.writeln('\x1b[1;36m╔════════════════════════════════════════════════════════════╗\x1b[0m');
        this.term.writeln('\x1b[1;36m║\x1b[0m         \x1b[1;33mRemote Access Console - WebSocket Tunnel\x1b[0m         \x1b[1;36m║\x1b[0m');
        this.term.writeln('\x1b[1;36m╚════════════════════════════════════════════════════════════╝\x1b[0m');
        this.term.writeln('');
        this.term.writeln('\x1b[90mSession disconnected. Close this tab or refresh for new connection.\x1b[0m');
        this.updateConnectionStatus(false);
    }

    toggleFullscreen() {
        const panel = document.getElementById('connection-panel');
        if (panel) {
            if (!document.fullscreenElement) {
                panel.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
    }

    updateConnectionStatus(connected) {
        const badge = document.getElementById('connection-status');
        if (badge) {
            if (connected) {
                badge.textContent = 'Connected';
                badge.classList.add('connected');
            } else {
                badge.textContent = 'Disconnected';
                badge.classList.remove('connected');
            }
        }
    }

    showError(message) {
        console.error(message);
        this.term.writeln(`\r\n\x1b[1;31m✗ ${message}\x1b[0m`);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TunnelClient();
});
