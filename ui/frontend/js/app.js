window.app = {
    renderers: {},
    waveform: null,
    
    async init() {
        router.init();
        
        // Wait for pywebview
        await api._waitReady();
        
        // Load initial data
        const settings = await api.getSettings();
        stateManager.setState('settings', settings);
        
        // Polling
        stateManager.pollBackend();
        
        // Show dashboard by default
        router.navigateTo('dashboard');
        
        stateManager.subscribe('appState', (state) => {
            const statusEl = document.getElementById('status-text');
            if (statusEl) {
                statusEl.textContent = state.status.toUpperCase();
                statusEl.className = `status-text ${state.status}`;
            }
            if (this.waveform) {
                this.waveform.setMode(state.status);
            }
        });
    }
};

window.app.renderers.dashboard = async (container) => {
    container.innerHTML = `
        <div class="glass-panel flex-1 flex flex-col justify-center items-center p-6">
            <h1 id="status-text" class="status-text">IDLE</h1>
            <div class="waveform-container">
                <canvas id="waveform"></canvas>
            </div>
            
            <div class="flex gap-4 mt-4">
                <button class="glass-button" onclick="router.navigateTo('settings')">Settings</button>
                <button class="glass-button" onclick="router.navigateTo('history')">History</button>
                <button class="glass-button" onclick="router.navigateTo('stats')">Stats</button>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (!window.app.waveform) {
            window.app.waveform = new WaveformVisualizer('waveform');
            window.app.waveform.start();
        } else {
            window.app.waveform.start();
        }
    }, 100);
};

window.app.renderers.settings = async (container) => {
    const settings = stateManager.getState('settings');
    container.innerHTML = `
        <div class="glass-panel p-6 w-full h-full flex flex-col">
            <div class="flex justify-between items-center mb-6">
                <h2>Settings</h2>
                <button class="glass-button" onclick="router.navigateTo('dashboard')">Back</button>
            </div>
            <div class="settings-layout">
                <div class="settings-sidebar">
                    <div class="glass-tab active">General</div>
                    <div class="glass-tab">AI</div>
                    <div class="glass-tab">Audio</div>
                </div>
                <div class="settings-content">
                    <div class="form-group">
                        <label class="form-label">Dictation Mode</label>
                        <select class="glass-input">
                            <option ${settings?.general?.mode === 'toggle' ? 'selected' : ''}>Toggle (Press to start/stop)</option>
                            <option ${settings?.general?.mode === 'ptt' ? 'selected' : ''}>Push to Talk</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Start with Windows</label>
                        <input type="checkbox" class="glass-toggle" ${settings?.general?.startup ? 'checked' : ''}>
                    </div>
                </div>
            </div>
        </div>
    `;
};

window.app.renderers.history = async (container) => {
    const history = await api.getHistory();
    container.innerHTML = `
        <div class="glass-panel p-6 w-full h-full flex flex-col">
            <div class="flex justify-between items-center mb-6">
                <h2>History</h2>
                <button class="glass-button" onclick="router.navigateTo('dashboard')">Back</button>
            </div>
            <input type="text" class="glass-input mb-4" placeholder="Search history...">
            <div class="history-list flex-1 overflow-y-auto">
                ${history.map(item => `
                    <div class="glass-card history-item">
                        <div class="history-item-header">
                            <span>${new Date(item.timestamp).toLocaleString()}</span>
                            <span>${item.app_context}</span>
                        </div>
                        <div class="history-item-text">${item.cleaned_text}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
};

window.app.renderers.stats = async (container) => {
    const stats = await api.getStats();
    container.innerHTML = `
        <div class="glass-panel p-6 w-full h-full flex flex-col">
            <div class="flex justify-between items-center mb-6">
                <h2>Statistics</h2>
                <button class="glass-button" onclick="router.navigateTo('dashboard')">Back</button>
            </div>
            <div class="stats-grid">
                <div class="glass-card stat-card">
                    <div class="stat-label">Words Dictated</div>
                    <div class="stat-value">${stats?.total_words || 0}</div>
                </div>
                <div class="glass-card stat-card">
                    <div class="stat-label">Time Saved</div>
                    <div class="stat-value">${stats?.time_saved_minutes || 0}m</div>
                </div>
                <div class="glass-card stat-card">
                    <div class="stat-label">Dictations</div>
                    <div class="stat-value">${stats?.total_dictations || 0}</div>
                </div>
                <div class="glass-card stat-card">
                    <div class="stat-label">Top App</div>
                    <div class="stat-value" style="font-size:24px">${stats?.most_used_app || 'None'}</div>
                </div>
            </div>
        </div>
    `;
};

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app.init();
});
