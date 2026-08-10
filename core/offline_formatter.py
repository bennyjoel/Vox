import re

class OfflineFormatter:
    """Basic rule-based formatter for when offline or API is unavailable."""
    
    def __init__(self):
        self.filler_words = [
            r'\bum\b', r'\buh\b', r'\buh huh\b', r'\blike\b', 
            r'\byou know\b', r'\bbasically\b', r'\bactually\b', 
            r'\bI mean\b', r'\bso yeah\b', r'\byou see\b', 
            r'\bsort of\b', r'\bkind of\b', r'\bwell\b'
        ]
        self.filler_regex = re.compile('|'.join(self.filler_words), re.IGNORECASE)

    def format_text(self, raw_text: str) -> str:
        if not raw_text or not raw_text.strip():
            return raw_text
            
        text = raw_text
        
        # Remove filler words
        text = self.filler_regex.sub('', text)
        
        # Clean up punctuation and spacing issues caused by removal
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s([?.!,"](?:\s|$))', r'\1', text)
        text = text.strip()
        
        if not text:
            return ""
            
        # Capitalize first letter of sentences
        sentences = re.split(r'([.!?]\s+)', text)
        capitalized_sentences = []
        for s in sentences:
            if s and not re.match(r'^[.!?]\s+$', s):
                capitalized_sentences.append(s[0].upper() + s[1:])
            else:
                capitalized_sentences.append(s)
                
        text = ''.join(capitalized_sentences)
        
        # Capitalize standalone 'i'
        text = re.sub(r'\bi\b', 'I', text)
        
        # Ensure it starts with a capital letter if it has content
        if text and len(text) > 0 and text[0].isalpha():
            text = text[0].upper() + text[1:]
            
        return text
