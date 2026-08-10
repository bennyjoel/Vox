import re
import logging
from config import (
    GIBBERISH_LOGPROB_THRESHOLD,
    GIBBERISH_COMPRESSION_THRESHOLD,
    GIBBERISH_DICT_VALIDITY_THRESHOLD,
    GIBBERISH_REPETITION_THRESHOLD
)

logger = logging.getLogger(__name__)

# A small subset of common English words for validation without external dependencies
COMMON_WORDS = set([
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
    # Add some common dictation words
    "hello", "test", "testing", "dictation", "period", "comma", "new", "line", "paragraph"
])

class GibberishFilter:
    """Filters out hallucinations and gibberish from transcriptions."""
    
    @staticmethod
    def is_gibberish(text: str, avg_logprob: float, compression_ratio: float) -> tuple[bool, str]:
        """
        Checks if text is gibberish based on multiple heuristics.
        Returns True if ANY 2+ stages fail.
        """
        if not text or not text.strip():
            return True, "empty"
            
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        if len(words) == 0:
            return True, "empty_after_clean"
            
        failures = []
        
        # Stage 1: Logprob
        if avg_logprob < GIBBERISH_LOGPROB_THRESHOLD:
            failures.append('low_confidence')
            
        # Stage 2: Compression
        if compression_ratio > GIBBERISH_COMPRESSION_THRESHOLD:
            failures.append('repetitive')
            
        # Stage 3: Dictionary validity
        valid_words = sum(1 for w in words if w in COMMON_WORDS)
        validity_ratio = valid_words / len(words)
        
        # We only apply dictionary check if it's longer text, otherwise short rare words fail
        if len(words) > 3 and validity_ratio < GIBBERISH_DICT_VALIDITY_THRESHOLD:
            # We relax this heavily because our dictionary is tiny
            if validity_ratio < (GIBBERISH_DICT_VALIDITY_THRESHOLD * 0.5):
                failures.append('invalid_words')
                
        # Stage 4: Repetition
        if len(words) > 5:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            if repetition_ratio < GIBBERISH_REPETITION_THRESHOLD:
                failures.append('extreme_repetition')
                
        is_gibberish = len(failures) >= 2
        reason = ", ".join(failures) if is_gibberish else ""
        
        if is_gibberish:
            logger.debug(f"Filtered gibberish: {text} | Reasons: {reason}")
            
        return is_gibberish, reason
