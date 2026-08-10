import logging
import re

logger = logging.getLogger(__name__)

class SnippetEngine:
    """Manages and expands text snippets/templates."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.snippets = {}
        self.load_snippets()

    def load_snippets(self):
        """Loads snippets from DB if available."""
        if self.db_manager:
            # Assume db_manager has a method to get all snippets
            try:
                self.snippets = self.db_manager.get_snippets()
            except AttributeError:
                logger.warning("db_manager does not have get_snippets method.")
        else:
            self.snippets = {}

    def check_and_expand(self, text: str) -> str:
        """Scans text for trigger phrases and replaces them."""
        if not text or not self.snippets:
            return text
            
        expanded_text = text
        # Simple string replacement for phrases
        # Sort by length descending to replace longer phrases first
        sorted_triggers = sorted(self.snippets.keys(), key=len, reverse=True)
        
        for trigger in sorted_triggers:
            expansion = self.snippets[trigger]
            # Use regex for case-insensitive exact word matching
            # Escape trigger to avoid regex errors
            pattern = re.compile(r'\b' + re.escape(trigger) + r'\b', re.IGNORECASE)
            expanded_text = pattern.sub(expansion, expanded_text)
            
        return expanded_text

    def add_snippet(self, trigger: str, expansion: str):
        """Adds a new snippet."""
        self.snippets[trigger] = expansion
        if self.db_manager:
            try:
                self.db_manager.add_snippet(trigger, expansion)
            except AttributeError:
                pass

    def remove_snippet(self, trigger: str):
        """Removes a snippet."""
        if trigger in self.snippets:
            del self.snippets[trigger]
            if self.db_manager:
                try:
                    self.db_manager.remove_snippet(trigger)
                except AttributeError:
                    pass

    def get_all_snippets(self) -> dict:
        """Returns all registered snippets."""
        return self.snippets
