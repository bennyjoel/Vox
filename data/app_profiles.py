class AppProfileManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self._seed_defaults()

    def _seed_defaults(self):
        # Only seed if no profiles exist
        if not self.db.get_all_profiles():
            defaults = [
                {'app_pattern': 'slack', 'display_name': 'Slack', 'tone': 'chat', 'custom_prompt': 'Keep tone casual and friendly.'},
                {'app_pattern': 'gmail', 'display_name': 'Gmail', 'tone': 'email', 'custom_prompt': 'Professional email tone.'},
                {'app_pattern': 'code', 'display_name': 'VS Code', 'tone': 'code', 'custom_prompt': 'Preserve technical terms exactly.'},
                {'app_pattern': 'notion', 'display_name': 'Notion', 'tone': 'document', 'custom_prompt': 'Use markdown formatting.'}
            ]
            for p in defaults:
                self.db.add_profile(p['app_pattern'], p['display_name'], p['tone'], p['custom_prompt'])

    def get_profile_for_context(self, window_title: str) -> dict | None:
        if not window_title:
            return None
        return self.db.get_profile_for_app(window_title)

    def get_all(self) -> list[dict]:
        return self.db.get_all_profiles()

    def save(self, profile: dict):
        self.db.add_profile(
            profile.get('app_pattern', ''),
            profile.get('display_name', ''),
            profile.get('tone', 'general'),
            profile.get('custom_prompt', ''),
            profile.get('enabled', 1)
        )

    def delete(self, app_pattern: str):
        self.db.remove_profile(app_pattern)
