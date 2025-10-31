"""
Unit tests for Spell Checker

Run: pytest tests/test_spell_checker.py -v
"""

import pytest
import sys
sys.path.insert(0, '../src')
from spell_checker import SpellChecker


class TestSpellChecker:
    """Test spell checking functionality."""
    
    def test_levenshtein_distance(self):
        """Test edit distance calculation."""
        assert SpellChecker.levenshtein_distance("kitten", "sitting") == 3
        assert SpellChecker.levenshtein_distance("hello", "hello") == 0
        assert SpellChecker.levenshtein_distance("hello", "helo") == 1
    
    def test_find_similar(self):
        """Test finding similar words."""
        dictionary = [
            ("algorithm", 100),
            ("algorithms", 85),
            ("logarithm", 60)
        ]
        
        similar = SpellChecker.find_similar("algoritm", dictionary, max_distance=2, k=3)
        
        assert len(similar) > 0
        assert similar[0][0] == "algorithm"  # Closest match
    
    def test_empty_dictionary(self):
        """Test with empty dictionary."""
        similar = SpellChecker.find_similar("test", [], max_distance=2, k=5)
        assert len(similar) == 0
    
    def test_exact_match_excluded(self):
        """Test exact matches are not in suggestions."""
        dictionary = [("hello", 100), ("help", 80)]
        similar = SpellChecker.find_similar("hello", dictionary, max_distance=2, k=5)
        
        # Should not include exact match
        assert not any(word == "hello" for word, _, _ in similar)
    
    def test_optimized_distance(self):
        """Test space-optimized distance calculation."""
        dist1 = SpellChecker.levenshtein_distance("test", "best")
        dist2 = SpellChecker.levenshtein_distance_optimized("test", "best")
        assert dist1 == dist2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])