const api = {
    _waitReady: function() {
        return new Promise(resolve => {
            if (window.pywebview && window.pywebview.api) {
                resolve();
            } else {
                window.addEventListener('pywebviewready', resolve);
            }
        });
    },

    async call(method, ...args) {
        await this._waitReady();
        try {
            return await window.pywebview.api[method](...args);
        } catch (e) {
            console.error(`API Error calling ${method}:`, e);
            return null;
        }
    },

    async getState() { return await this.call('get_state'); },
    async startRecording() { return await this.call('start_recording'); },
    async stopRecording() { return await this.call('stop_recording'); },
    async getSettings() { return await this.call('get_settings'); },
    async saveSettings(settings) { return await this.call('save_settings', settings); },
    async getHistory(limit=50, offset=0) { return await this.call('get_history', limit, offset); },
    async searchHistory(query) { return await this.call('search_history', query); },
    async deleteHistoryItem(id) { return await this.call('delete_history_item', id); },
    async getStats() { return await this.call('get_stats'); },
    async testMicrophone() { return await this.call('test_microphone'); },
    async getMicrophones() { return await this.call('get_microphones'); },
    async setMicrophone(id) { return await this.call('set_microphone', id); },
    async startEnrollment() { return await this.call('start_enrollment'); },
    async submitEnrollmentSample(idx) { return await this.call('submit_enrollment_sample', idx); },
    async finishEnrollment() { return await this.call('finish_enrollment'); },
    async testVoiceMatch() { return await this.call('test_voice_match'); },
    async deleteVoiceprint() { return await this.call('delete_voiceprint'); },
    async getEnrollmentSentences() { return await this.call('get_enrollment_sentences'); },
    async isModelDownloaded(model) { return await this.call('is_model_downloaded', model); },
    async downloadModel(model) { return await this.call('download_model', model); },
    async getAvailableModels() { return await this.call('get_available_models'); },
    async testGeminiKey(key) { return await this.call('test_gemini_key', key); },
    async getSnippets() { return await this.call('get_snippets'); },
    async addSnippet(t, e) { return await this.call('add_snippet', t, e); },
    async deleteSnippet(t) { return await this.call('delete_snippet', t); },
    async getDictionaryWords() { return await this.call('get_dictionary_words'); },
    async addDictionaryWord(w) { return await this.call('add_dictionary_word', w); },
    async removeDictionaryWord(w) { return await this.call('remove_dictionary_word', w); },
    async getAppProfiles() { return await this.call('get_app_profiles'); },
    async saveAppProfile(p) { return await this.call('save_app_profile', p); },
    async deleteAppProfile(p) { return await this.call('delete_app_profile', p); },
    async quitApp() { return await this.call('quit_app'); }
};
