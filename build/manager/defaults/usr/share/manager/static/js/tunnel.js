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

        // Check for VNC DOM container
        if (!document.getElementById('vnc-container')) {
            const vncDiv = document.createElement('div');
            vncDiv.id = 'vnc-container';
            vncDiv.className = 'vnc-container hidden';
            document.getElementById('terminal').parentNode.appendChild(vncDiv);

            // Add Styles for VNC
            const style = document.createElement('style');
            style.textContent = `
                .vnc-container { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background: #222; overflow: auto; }
                .vnc-container.hidden { display: none; }
                #terminal.hidden { display: none; }
            `;
            document.head.appendChild(style);
        }

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

        // Service select listener REMOVED


        const disconnectBtn = document.getElementById('btn-disconnect');
        if (disconnectBtn) disconnectBtn.addEventListener('click', () => this.disconnect());

        const vncMenuBtn = document.getElementById('btn-vnc-menu');
        if (vncMenuBtn) vncMenuBtn.addEventListener('click', () => this.toggleVNCMenu());

        const fullscreenBtn = document.getElementById('btn-fullscreen');

        if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        // HIDE HEADER ON FULLSCREEN
        document.addEventListener('fullscreenchange', () => {
            const header = document.querySelector('.panel-header');
            if (header) {
                if (document.fullscreenElement) {
                    header.style.display = 'none';
                } else {
                    header.style.display = '';
                }
            }
        });

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

            let url = `/manager/v1/private/tunnel/agents?page=${this.currentPage}&limit=${limit}`;
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
                        <a href="/computers/results/${agent.agent_id.substring(4)}" class="agent-name-link" target="_blank" title="View Computer">
                            <span class="agent-name">${agent.hostname}</span>
                        </a>
                        <span class="agent-status"></span>
                    </div>
                    <div class="agent-services">
                        ${project} ${services.map(s => `<span class="service-tag" data-service="${s.toLowerCase()}">${s.toUpperCase()}</span>`).join('')}
                    </div>
                </div>
            `;
        }).join('');

        container.insertAdjacentHTML('beforeend', html);
    }

    handleAgentClick(e) {
        // Check if clicked ON a service tag
        const serviceTag = e.target.closest('.service-tag');
        const card = e.target.closest('.agent-card');

        if (serviceTag && card) {
            e.preventDefault(); // Prevent bubbling usually
            const agentId = card.dataset.agentId;
            const service = serviceTag.dataset.service;
            this.showAgentModal(agentId, service);
        }
        // Explicitly DO NOTHING if clicked on the card generally
    }

    showAgentModal(agentId, serviceType = null) {
        const agent = this.agents.find(a => a.agent_id === agentId);
        if (!agent) return;

        this.currentAgent = agent;

        // Determine service: use passed type, or default to SSH, or first available
        const availableServices = (agent.info?.available_services || []).map(s => s.toLowerCase());

        if (serviceType && availableServices.includes(serviceType)) {
            this.currentService = serviceType;
        } else if (availableServices.includes('ssh')) {
            this.currentService = 'ssh';
        } else if (availableServices.length > 0) {
            this.currentService = availableServices[0];
        } else {
            this.currentService = 'ssh'; // Fallback
        }

        const infoContainer = document.getElementById('agent-info');
        if (!infoContainer) return;

        // Clean hostname (remove [AgentID] suffix if present)
        const cleanHostname = agent.hostname.split(' [')[0];

        // Update Modal Title
        const modalTitle = document.getElementById('modal-title');
        if (modalTitle) {
            modalTitle.textContent = serviceType
                ? `${serviceType.toUpperCase()} to ${agent.agent_id}`
                : `${agent.agent_id}`;
        }

        infoContainer.innerHTML = `
            <div class="info-row">
                <span class="info-label">Hostname:</span>
                <span><strong class="hostname-text">${cleanHostname}</strong></span>
            </div>
             <div class="info-row">
                <span class="info-label">Project:</span>
                <span>${agent.info?.project || 'Unknown'}</span>
            </div>
        `;

        const modal = document.getElementById('agent-modal');
        if (modal) {
            modal.classList.remove('hidden');

            // Removed Select Logic population here

            this.updateInputFields();

            // Set focus to Connect button by default
            const connectBtn = document.getElementById('modal-connect');
            if (connectBtn) {
                setTimeout(() => connectBtn.focus(), 50);
            }
        }
    }

    updateInputFields() {
        const usernameInput = document.getElementById('username-input');

        if (usernameInput) {
            const inputField = document.getElementById('ssh-username');
            const hint = document.querySelector('.input-hint');

            // Reset input value to prevent password leakage when switching
            if (inputField) {
                if (this.currentService === 'ssh' || this.currentService === 'rdp') {
                    // Default to root for SSH, do NOT keep VNC password
                    inputField.value = 'root';
                } else {
                    // Start empty for VNC
                    inputField.value = '';
                }
            }

            if (this.currentService === 'ssh' || this.currentService === 'rdp') {
                usernameInput.classList.remove('hidden');
                if (inputField) {
                    inputField.placeholder = "Enter username (e.g., root)";
                    inputField.type = "text";
                }
                if (hint) hint.classList.remove('hidden');
            } else if (this.currentService === 'vnc') {
                usernameInput.classList.remove('hidden');
                if (inputField) {
                    inputField.placeholder = "Enter VNC Password";
                    inputField.type = "password";
                    if (inputField.value === 'root') inputField.value = ''; // Clear default
                }
                if (hint) hint.classList.add('hidden');
            } else {
                usernameInput.classList.add('hidden');
            }
        }
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
        const input = document.getElementById('ssh-username');

        if (this.currentService === 'ssh' || this.currentService === 'rdp') {
            if (input) username = input.value.trim();
            if (!username) {
                alert('Please enter a username');
                return;
            }
        } else if (this.currentService === 'vnc') {
            // Re-use username variable for password in VNC context
            if (input) username = input.value.trim();
            if (!username) {
                alert('Please enter a VNC password');
                return;
            }
        }

        this.closeModal();

        const params = new URLSearchParams();
        params.append('agent', this.currentAgent.agent_id);
        params.append('service', this.currentService);

        let hashParams = '';
        if (username) {
            if (this.currentService === 'vnc') {
                // For VNC, pass password in HASH to avoid server logs/history visibility
                // URL params are NOT encrypted in GET requests logs, but fragments (#) are not sent to server.
                hashParams = `#password=${encodeURIComponent(username)}`;
            } else {
                // For SSH/RDP, 'user' can be in URL
                params.append('user', username);
            }
        }

        const url = `${window.location.pathname}?${params.toString()}${hashParams}`;
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
                this.currentAgent = agent;
                this.currentService = params.get('service') || 'ssh';
                const username = params.get('user');

                // Try to get password from URL parameters OR Hash
                let password = params.get('password'); // Legacy support
                if (!password && window.location.hash) {
                    const hash = window.location.hash.substring(1); // remove #
                    const hashSearchParams = new URLSearchParams(hash);
                    password = hashSearchParams.get('password');

                    // Clear the hash from address bar for security/aesthetics
                    if (password) {
                        history.replaceState(null, null, window.location.pathname + window.location.search);
                    }
                }

                await this.startSession(username || password); // Pass password if VNC
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

        // Update Connection Panel Header
        const agentNameEl = document.getElementById('current-agent-name');
        const serviceEl = document.getElementById('current-service');
        if (agentNameEl) agentNameEl.textContent = this.currentAgent.hostname;
        if (serviceEl) serviceEl.textContent = this.currentService.toUpperCase();

        const termDiv = document.getElementById('terminal');
        const vncDiv = document.getElementById('vnc-container');
        const rdpDiv = document.getElementById('rdp-container');

        if (this.currentService === 'vnc') {
            if (termDiv) termDiv.classList.add('hidden');
            if (vncDiv) vncDiv.classList.remove('hidden');
            if (rdpDiv) rdpDiv.classList.add('hidden');
            this.startVNC(username);
        } else if (this.currentService === 'rdp') {
            if (termDiv) termDiv.classList.add('hidden');
            if (vncDiv) vncDiv.classList.add('hidden');
            if (rdpDiv) rdpDiv.classList.remove('hidden');
            this.startRDP(username);
        } else {
            if (termDiv) termDiv.classList.remove('hidden');
            if (vncDiv) vncDiv.classList.add('hidden');
            if (rdpDiv) rdpDiv.classList.add('hidden');
            this.startSSH(username);
        }
    }

    async startVNC(username) {
        document.title = `${this.currentAgent.hostname} - VNC Remote`;
        const vncDiv = document.getElementById('vnc-container');
        vncDiv.innerHTML = ''; // Clean previous
        vncDiv.classList.add('scaling-active'); // Enable scaling CSS

        // Show VNC Menu Button
        const vncBtn = document.getElementById('btn-vnc-menu');
        if (vncBtn) vncBtn.style.display = 'inline-flex';

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl = `${protocol}//${window.location.host}/manager/v1/private/tunnel/ws/agents/${this.currentAgent.agent_id}`;
        const params = new URLSearchParams();
        params.append('service', 'vnc'); // or this.currentService
        wsUrl += `?${params.toString()}`;

        try {
            // Wait for library if not yet loaded (race condition with module script)
            if (!window.RFB) {
                console.log("Waiting for noVNC library...");
                for (let i = 0; i < 10; i++) {
                    if (window.RFB) break;
                    await new Promise(r => setTimeout(r, 200));
                }
            }
            // Fallback: Try dynamic import if still missing
            if (!window.RFB) {
                console.log("Attempting dynamic import of noVNC...");
                const module = await import('/manager/static/novnc/core/rfb.js');
                window.RFB = module.default;
            }

            if (!window.RFB) throw new Error('noVNC library not loaded');

            // ✅ Ensure DOM is laid out BEFORE initializing RFB
            // This is critical for scaleViewport to calculate dimensions correctly
            await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));

            this.rfb = new window.RFB(vncDiv, wsUrl, {
                credentials: { password: username } // if needed, often ignored for tunnel
            });

            this.rfb.addEventListener("connect", () => {
                this.updateConnectionStatus(true);
                this.rfb.focus();

                // Set scaling options AFTER connection or init
                this.rfb.scaleViewport = true;
                this.rfb.resizeSession = false; // Disable remote resizing support

                // Add Focus Listener to capture keyboard
                this.rfb.focus();
            });

            this.rfb.addEventListener("disconnect", (e) => {
                this.updateConnectionStatus(false);
                if (e.detail.clean) {
                    this.disconnect();
                } else {
                    console.error("VNC Disconnect", e);
                    this.disconnect();
                }
            });

            // Clean previous listeners if any (though instance is new)
            this.setupVNCTools();

        } catch (e) {
            console.error(e);
            alert("Error starting VNC: " + e.message);
            this.disconnect();
        }
    }

    startRDP(username) {
        document.title = `${this.currentAgent.hostname} - RDP Info`;

        const cmdCode = document.getElementById('rdp-command');
        // Command format: python3 client.py <user> -t rdp -a <agent_id> -m <manager_url>
        // We use window.location.origin for manager url
        const managerUrl = window.location.origin;
        const userPart = username ? ` ${username}` : '';
        const command = `migasfree-connect -t rdp -a ${this.currentAgent.agent_id} -m ${managerUrl} ${userPart}`;

        if (cmdCode) cmdCode.textContent = command;

        // Hide VNC menu button just in case
        const vncBtn = document.getElementById('btn-vnc-menu');
        if (vncBtn) vncBtn.style.display = 'none';

        // Setup Copy Button logic here (lazy bind or idempotent)
        const btnCopy = document.getElementById('btn-copy-rdp');
        if (btnCopy) {
            // Remove old listener to avoid duplicates if re-entering
            const newBtn = btnCopy.cloneNode(true);
            btnCopy.parentNode.replaceChild(newBtn, btnCopy);

            newBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(command).then(() => {
                    const originalText = newBtn.textContent;
                    newBtn.textContent = 'Copied!';
                    setTimeout(() => newBtn.textContent = originalText, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy to clipboard');
                });
            });
        }
    }

    setupVNCTools() {
        // Remove existing listener to prevent duplicates if any
        document.removeEventListener('keydown', this._vncKeyHandler);

        this._vncKeyHandler = (e) => {
            if (!this.rfb) return;

            // F8 Key to toggle menu
            if (e.code === 'F8') {
                console.log('F8 Pressed - Toggling Menu');
                e.preventDefault();
                e.stopPropagation(); // Stop noVNC from processing it
                this.toggleVNCMenu();
            }
        };

        // Use capture phase to intercept before noVNC
        document.addEventListener('keydown', this._vncKeyHandler, true);

        // Setup Menu Buttons
        const btnCad = document.getElementById('btn-cad');
        if (btnCad) {
            btnCad.replaceWith(btnCad.cloneNode(true)); // remove old listeners
            document.getElementById('btn-cad').addEventListener('click', () => {
                this.rfb.sendCtrlAltDel();
                this.toggleVNCMenu();
            });
        }

        const btnWin = document.getElementById('btn-win-key');
        if (btnWin) {
            btnWin.replaceWith(btnWin.cloneNode(true));
            document.getElementById('btn-win-key').addEventListener('click', () => {
                // 0xFFEB is XK_Super_L (Left Windows Key)
                this.rfb.sendKey(0xFFEB);
                this.toggleVNCMenu();
            });
        }

        const btnScaling = document.getElementById('btn-scaling');
        if (btnScaling) {
            btnScaling.replaceWith(btnScaling.cloneNode(true));
            document.getElementById('btn-scaling').addEventListener('click', () => {
                this.rfb.scaleViewport = !this.rfb.scaleViewport;
                this.toggleVNCMenu();
            });
        }

        const btnClipboard = document.getElementById('btn-send-clipboard');
        if (btnClipboard) {
            btnClipboard.replaceWith(btnClipboard.cloneNode(true));
            document.getElementById('btn-send-clipboard').addEventListener('click', () => {
                const input = document.getElementById('vnc-clipboard-input');
                if (input && input.value) {
                    this.rfb.clipboardPasteFrom(input.value);
                    input.value = ''; // Clear after sending
                    this.toggleVNCMenu();
                }
            });
        }

        const btnClose = document.getElementById('vnc-tools-close');
        if (btnClose) {
            btnClose.replaceWith(btnClose.cloneNode(true));
            document.getElementById('vnc-tools-close').addEventListener('click', () => this.toggleVNCMenu());
        }

        const btnDisc = document.getElementById('btn-disconnect-vnc');
        if (btnDisc) {
            btnDisc.replaceWith(btnDisc.cloneNode(true));
            document.getElementById('btn-disconnect-vnc').addEventListener('click', () => this.disconnect());
        }
    }

    toggleVNCMenu() {
        const modal = document.getElementById('vnc-tools-modal');
        if (modal) {
            if (modal.classList.contains('hidden')) {
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
                if (this.rfb) this.rfb.focus(); // Return focus to VNC
            }
        }
    }

    async startSSH(username) {


        setTimeout(() => this.term.focus(), 50);

        document.title = `${this.currentAgent.hostname} - Remote Access Console`;

        this.term.clear();

        // Hide VNC Menu Button (if switching or lingering)
        const vncBtn = document.getElementById('btn-vnc-menu');
        if (vncBtn) vncBtn.style.display = 'none';

        const connMsg = username ?
            `→ Connecting to ${username}@${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...` :
            `→ Connecting to ${this.currentAgent.hostname} (${this.currentService.toUpperCase()})...`;
        this.term.writeln(`\x1b[1;32m${connMsg}\x1b[0m`);

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl = `${protocol}//${window.location.host}/manager/v1/private/tunnel/ws/agents/${this.currentAgent.agent_id}`;

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
        if (this.rfb) {
            this.rfb.disconnect();
            this.rfb = null;
        }
        if (this._vncKeyHandler) {
            document.removeEventListener('keydown', this._vncKeyHandler);
            this._vncKeyHandler = null;
        }

        const params = new URLSearchParams(window.location.search);
        if (params.has('agent')) {
            window.close(); // Auto-close tab on disconnect
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
