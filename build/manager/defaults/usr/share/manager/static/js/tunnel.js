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

    init() {
        // Initialize terminal
        this.initTerminal();

        // Setup event listeners
        this.setupEventListeners();

        // Initial load and auto-connect check
        this.fetchAgents().then(() => {
            this.checkAutoConnect();
        });
    }

    initTerminal() {
        // Create xterm.js terminal
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

        // Add fit addon
        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);

        // Add web links addon
        const webLinksAddon = new WebLinksAddon.WebLinksAddon();
        this.term.loadAddon(webLinksAddon);

        // Mount terminal
        this.term.open(document.getElementById('terminal'));
        this.fitAddon.fit();

        // Handle resize
        const handleResize = () => {
            try {
                this.fitAddon.fit();
                const dims = { cols: this.term.cols, rows: this.term.rows };
                // Send resize to server
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

        // Initial resize after a short delay to ensure DOM is ready
        setTimeout(handleResize, 100);

        // Also listen to term resize events directly if fitAddon triggers them
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
        // Refresh agents button
        document.getElementById('refresh-agents').addEventListener('click', () => {
            this.resetAndReload();
        });

        // Search agents
        let debounceTimer;
        document.getElementById('search-agents').addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                // For now, client-side filter due to API limitations or reload
                // Since we changed to server-side pagination, real search should hit API
                // But for simplicity/demo, let's keep it simple or trigger API search
                // this.filterAgents(e.target.value); 
                // Currently filterAgents only filters DOM which is empty if paginated.
                // NOTE: Proper implementation requires backend search support.
                // For this step, we will just Reload with query if we wanted to be correct, 
                // but let's stick to simple reload for now.
                this.resetAndReload();
            }, 500);
        });

        // Infinite Scroll
        document.getElementById('agents-list').addEventListener('scroll', (e) => {
            this.handleScroll(e);
        });

        // Agent List Delegation
        document.getElementById('agents-list').addEventListener('click', (e) => {
            this.handleAgentClick(e);
        });

        // Modal controls
        document.getElementById('modal-close').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('modal-cancel').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('modal-connect').addEventListener('click', () => {
            this.connectToAgent();
        });

        // Service selector
        document.querySelectorAll('.service-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.service-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.currentService = e.currentTarget.dataset.service;

                // Show/hide username input based on service
                const usernameInput = document.getElementById('username-input');
                if (this.currentService === 'ssh' || this.currentService === 'rdp') {
                    usernameInput.classList.remove('hidden');
                } else {
                    usernameInput.classList.add('hidden');
                }
            });
        });

        // Disconnect button
        document.getElementById('btn-disconnect').addEventListener('click', () => {
            this.disconnect();
        });

        // Fullscreen button
        document.getElementById('btn-fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Terminal input
        this.term.onData(data => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                // Convert terminal input to hex and send
                const hexData = Array.from(data)
                    .map(char => char.charCodeAt(0).toString(16).padStart(2, '0'))
                    .join('');

                this.ws.send(JSON.stringify({
                    data: hexData
                }));
            }
        });
    }

    async fetchAgents() {
        if (this.isLoading || !this.hasMore) return;

        this.isLoading = true;
        const container = document.getElementById('agents-list');
        const search = document.getElementById('search-agents').value;
        const limit = 50;

        try {
            // Add loading indicator if first page
            if (this.currentPage === 1) {
                container.innerHTML = '<div class="loading">Loading agents...</div>';
            }

            let url = `/manager/v1/public/tunnel/agents?page=${this.currentPage}&limit=${limit}`;
            if (search) {
                url += `&q=${encodeURIComponent(search)}`;
            }

            const response = await fetch(url);
            const data = await response.json();
            const newAgents = data.agents || [];

            if (this.currentPage === 1) {
                this.agents = newAgents;
                container.innerHTML = ''; // Clear loading
            } else {
                this.agents = [...this.agents, ...newAgents];
            }

            this.hasMore = newAgents.length === limit;
            this.currentPage++;

            this.appendAgents(newAgents, container);

            if (this.agents.length === 0) {
                container.innerHTML = '<div class="loading">No agents available</div>';
            }

        } catch (error) {
            console.error('Error loading agents:', error);
            if (this.currentPage === 1) {
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
        // Load more when scrolled to bottom (with 100px buffer)
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            this.fetchAgents();
        }
    }

    appendAgents(agents, container) {
        if (!agents || agents.length === 0) return;

        const html = agents.map(agent => {
            const services = agent.info?.available_services || [];
            const os = agent.info?.system || 'Unknown';
            const arch = agent.info?.architecture || '';

            return `
                <div class="agent-card" data-agent-id="${agent.agent_id}">
                    <div class="agent-header">
                        <span class="agent-name">${agent.hostname}</span>
                        <span class="agent-status"></span>
                    </div>
                    <div class="agent-info-text">
                        ${os} ${arch}
                    </div>
                    <div class="agent-info-text">
                        ID: ${agent.agent_id.substring(0, 12)}...
                    </div>
                    <div class="agent-services">
                        ${services.map(s => `<span class="service-tag">${s.toUpperCase()}</span>`).join('')}
                    </div>
                </div>
            `;
        }).join('');

        // Append HTML
        container.insertAdjacentHTML('beforeend', html);
    }

    // Helper for delegation
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

        // Populate agent info
        const infoContainer = document.getElementById('agent-info');
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

        // Show modal
        document.getElementById('agent-modal').classList.remove('hidden');
    }

    closeModal() {
        document.getElementById('agent-modal').classList.add('hidden');
    }

    connectToAgent() {
        console.log('Connect button clicked');
        if (!this.currentAgent) {
            console.error('No agent selected');
            return;
        }

        // Get username for SSH/RDP
        let username = null;
        if (this.currentService === 'ssh' || this.currentService === 'rdp') {
            const input = document.getElementById('ssh-username');
            if (input) {
                username = input.value.trim();
            }

            if (!username) {
                alert('Please enter a username');
                return;
            }
        }

        this.closeModal();

        // Open in new tab
        const params = new URLSearchParams();
        params.append('agent', this.currentAgent.agent_id);
        params.append('service', this.currentService);
        if (username) {
            params.append('user', username);
        }

        const url = `${window.location.pathname}?${params.toString()}`;
        console.log('Opening session URL:', url);

        const win = window.open(url, '_blank');
        if (!win) {
            alert('Connection failed: Pop-up blocked. Please allow pop-ups for this site to open the remote session.');
        }
    }

    checkAutoConnect() {
        const params = new URLSearchParams(window.location.search);
        const agentId = params.get('agent');

        if (!agentId) return;

        const agent = this.agents.find(a => a.agent_id === agentId);
        if (agent) {
            this.currentAgent = agent;
            this.currentService = params.get('service') || 'ssh';
            const username = params.get('user');

            this.startSession(username);
        } else {
            console.error('Agent not found:', agentId);
            this.showError('Agent not found. It may be offline.');
        }
    }

    async startSession(username) {
        // Show connection panel
        document.getElementById('welcome-screen').classList.add('hidden');
        document.getElementById('connection-panel').classList.remove('hidden');

        // Hide sidebar
        document.getElementById('sidebar').classList.add('hidden');

        // Focus terminal
        setTimeout(() => this.term.focus(), 50);

        // Update header - ONLY Hostname
        const headerText = this.currentAgent.hostname;

        document.getElementById('current-agent-name').textContent = headerText;
        document.getElementById('current-service').textContent = this.currentService.toUpperCase();

        // Update page title
        document.title = `${headerText} - Remote Access Console`;

        // Clear terminal
        this.term.clear();
        const connMsg = username ?
            `→ Connecting to ${username}@${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...` :
            `→ Connecting to ${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...`;
        this.term.writeln(`\x1b[1;32m${connMsg}\x1b[0m`);

        // Get WebSocket URL with parameters
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl = `${protocol}//${window.location.host}/manager/v1/public/tunnel/ws/agents/${this.currentAgent.agent_id}`;

        // Add query parameters
        const params = new URLSearchParams();
        params.append('service', this.currentService);
        if (username) {
            params.append('username', username);
        }
        wsUrl += `?${params.toString()}`;

        try {
            // Create WebSocket connection
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
                        // Convert hex data to Uint8Array
                        const hexData = message.data;
                        const match = hexData.match(/.{1,2}/g);
                        if (match) {
                            const bytes = new Uint8Array(match.map(byte => parseInt(byte, 16)));
                            // Use TextDecoder to handle UTF-8 properly
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

        // If we are in a dedicated session (url params present), close the tab
        const params = new URLSearchParams(window.location.search);
        if (params.has('agent')) {
            window.close();
            // If window.close() fails (e.g. not opened by script), fallback to UI update
            // but return to avoid flashing UI if it does close.
            // However, we continue just in case close() is blocked.
        }

        // Show welcome screen
        document.getElementById('connection-panel').classList.add('hidden');
        document.getElementById('welcome-screen').classList.remove('hidden');
        document.getElementById('sidebar').classList.remove('hidden');

        // Restore page title
        document.title = this.originalTitle;

        // Clear terminal
        this.term.clear();
        this.term.writeln('\x1b[1;36m╔════════════════════════════════════════════════════════════╗\x1b[0m');
        this.term.writeln('\x1b[1;36m║\x1b[0m         \x1b[1;33mRemote Access Console - WebSocket Tunnel\x1b[0m         \x1b[1;36m║\x1b[0m');
        this.term.writeln('\x1b[1;36m╚════════════════════════════════════════════════════════════╝\x1b[0m');
        this.term.writeln('');
        this.term.writeln('\x1b[90mSelect an agent from the sidebar to start a session...\x1b[0m');
        this.term.writeln('');

        this.updateConnectionStatus(false);
    }

    toggleFullscreen() {
        const panel = document.getElementById('connection-panel');
        if (!document.fullscreenElement) {
            panel.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    updateConnectionStatus(connected) {
        const badge = document.getElementById('connection-status');
        if (connected) {
            badge.textContent = 'Connected';
            badge.classList.add('connected');
        } else {
            badge.textContent = 'Disconnected';
            badge.classList.remove('connected');
        }
    }

    showError(message) {
        console.error(message);
        // You could add a toast notification here
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TunnelClient();
});
