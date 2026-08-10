const router = {
    pages: ['dashboard', 'settings', 'history', 'stats', 'enrollment', 'first-run'],
    
    init() {
        this.pages.forEach(page => {
            const el = document.createElement('div');
            el.id = `page-${page}`;
            el.className = 'page';
            document.getElementById('app-container').appendChild(el);
        });
        
        stateManager.subscribe('currentPage', (page) => this.renderPage(page));
    },

    navigateTo(pageName) {
        if (this.pages.includes(pageName)) {
            stateManager.setState('currentPage', pageName);
        }
    },

    renderPage(pageName) {
        document.querySelectorAll('.page').forEach(el => {
            el.classList.remove('active', 'animate-fade-in');
        });
        
        const target = document.getElementById(`page-${pageName}`);
        if (target) {
            target.classList.add('active', 'animate-fade-in');
            // Trigger app renderer if needed
            if (window.app && window.app.renderers[pageName]) {
                window.app.renderers[pageName](target);
            }
        }
    }
};
