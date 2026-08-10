class PersonalDictionary:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_hotwords(self) -> list[str]:
        words = self.get_all()
        return [item['word'] for item in words]

    def add_word(self, word: str) -> bool:
        if not word or not isinstance(word, str):
            return False
        word = word.strip()
        if not word:
            return False
        return self.db.add_word(word)

    def remove_word(self, word: str) -> bool:
        if not word or not isinstance(word, str):
            return False
        word = word.strip()
        return self.db.remove_word(word)

    def get_all(self) -> list[dict]:
        return self.db.get_all_words()
