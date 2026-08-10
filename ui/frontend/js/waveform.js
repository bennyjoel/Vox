class WaveformVisualizer {
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.canvas = null;
        this.ctx = null;
        this.mode = 'idle'; // idle, recording, processing
        this.data = new Array(30).fill(0.1);
        this.animationId = null;
        this.time = 0;
    }

    start() {
        this.canvas = document.getElementById(this.canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        // Resize
        const resize = () => {
            this.canvas.width = this.canvas.parentElement.clientWidth;
            this.canvas.height = this.canvas.parentElement.clientHeight;
        };
        window.addEventListener('resize', resize);
        resize();

        this.loop();
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }

    setMode(mode) {
        this.mode = mode;
    }

    setData(data) {
        // data array of floats 0 to 1
        if (data && data.length) {
            this.data = data;
        }
    }

    loop() {
        this.time += 0.05;
        this.draw();
        this.animationId = requestAnimationFrame(() => this.loop());
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        const ctx = this.ctx;
        
        ctx.clearRect(0, 0, width, height);
        
        let color = '#6366F1';
        if (this.mode === 'recording') color = '#EF4444';
        else if (this.mode === 'processing') color = '#10B981';

        ctx.beginPath();
        ctx.moveTo(0, height / 2);

        if (this.mode === 'idle') {
            for (let i = 0; i <= width; i += 5) {
                const y = Math.sin(i * 0.02 + this.time) * 10 + height / 2;
                ctx.lineTo(i, y);
            }
        } else {
            const barWidth = width / this.data.length;
            for (let i = 0; i < this.data.length; i++) {
                const val = this.data[i] * (height / 2) * 0.8;
                const x = i * barWidth;
                const y = height / 2 - val;
                ctx.lineTo(x, y);
            }
        }

        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Glow
        ctx.shadowBlur = 15;
        ctx.shadowColor = color;
        
        ctx.stroke();
        
        ctx.shadowBlur = 0; // reset
    }
}
