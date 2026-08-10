window.app = {
    waveform: null,
    
    async init() {
        // Wait for pywebview API to inject
        await new Promise(resolve => {
            const check = () => window.pywebview ? resolve() : setTimeout(check, 100);
            check();
        });

        // Initialize waveform
        this.waveform = new WaveformVisualizer('waveform');
        this.waveform.start();

        // Start polling state
        this.pollState();
    },

    async pollState() {
        if (!window.api) return;
        
        try {
            const state = await window.api.get_state();
            this.updateUI(state);
        } catch (e) {
            console.error("Failed to fetch state", e);
        }

        setTimeout(() => this.pollState(), 200); // 5fps poll is fine for widget
    },

    updateUI(state) {
        const container = document.getElementById('widget-container');
        const statusText = document.getElementById('status-text');
        const waveContainer = document.getElementById('waveform-container');

        // Reset classes
        container.className = 'glass-pill pywebview-drag-region';
        
        if (state.status === 'recording') {
            container.classList.add('recording');
            statusText.textContent = 'Listening...';
            waveContainer.style.display = 'block';
            this.waveform.setMode('recording');
        } else if (state.status === 'processing') {
            container.classList.add('processing');
            statusText.textContent = 'Processing...';
            waveContainer.style.display = 'none';
        } else {
            // Idle
            statusText.textContent = 'Press ⇧ + ⌥ + Space to Dictate';
            waveContainer.style.display = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.app.init();
});
