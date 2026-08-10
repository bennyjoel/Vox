const stateManager = {
    state: {
        currentPage: 'dashboard',
        appState: { status: 'idle', is_voice_locked: false, model_loaded: false },
        settings: null,
        history: [],
        stats: null,
        models: []
    },
    subscribers: {},

    subscribe(key, callback) {
        if (!this.subscribers[key]) this.subscribers[key] = [];
        this.subscribers[key].push(callback);
    },

    setState(key, value) {
        this.state[key] = value;
        if (this.subscribers[key]) {
            this.subscribers[key].forEach(cb => cb(value));
        }
    },

    getState(key) {
        return this.state[key];
    },

    async pollBackend() {
        const backendState = await api.getState();
        if (backendState) {
            const current = JSON.stringify(this.state.appState);
            const next = JSON.stringify(backendState);
            if (current !== next) {
                this.setState('appState', backendState);
            }
        }
        setTimeout(() => this.pollBackend(), 500);
    }
};
