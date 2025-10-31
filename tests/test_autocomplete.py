"""
Unit tests for Autocomplete System

Run: pytest tests/test_autocomplete.py -v
"""

import pytest
import sys
sys.path.insert(0, '../src')
from autocomplete import AutocompleteSystem, AutocompleteResult


class TestAutocompleteSystem:
    """Test autocomplete system functionality."""
    
    @pytest.fixture
    def system(self):
        """Create fresh autocomplete system."""
        system = AutocompleteSystem(cache_size=100)
        system.add_word("algorithm", 100)
        system.add_word("algorithms", 85)
        system.add_word("data", 95)
        system.add_word("database", 90)
        return system
    
    def test_initialization(self):
        """Test system initialization."""
        system = AutocompleteSystem(cache_size=500)
        assert system is not None
        stats = system.get_statistics()
        assert stats['cache_capacity'] == 500
    
    def test_add_word(self, system):
        """Test adding words."""
        assert system.add_word("python", 90) == True
        assert system.search_word("python") == True
    
    def test_get_suggestions(self, system):
        """Test getting suggestions."""
        result = system.get_suggestions("algo", k=5)
        
        assert isinstance(result, AutocompleteResult)
        assert len(result.suggestions) > 0
        assert result.suggestions[0][0] == "algorithm"
    
    def test_spell_correction(self, system):
        """Test spell correction."""
        result = system.get_suggestions_with_spell_check("algoritm", k=5)
        
        assert result.did_you_mean == "algorithm"
        assert len(result.suggestions) > 0
    
    def test_cache_performance(self, system):
        """Test cache improves performance."""
        # First query (cold)
        result1 = system.get_suggestions("algo", k=5)
        time1 = result1.query_time_ms
        
        # Second query (should be cached)
        result2 = system.get_suggestions("algo", k=5)
        time2 = result2.query_time_ms
        
        assert result2.from_cache == True
        assert time2 < time1 or time2 < 1.0  # Cached should be faster
    
    def test_frequency_update(self, system):
        """Test frequency updates."""
        system.update_frequency("algorithm", 200)
        result = system.get_suggestions("algo", k=1)
        assert result.suggestions[0][1] == 200
    
    def test_bulk_add(self, system):
        """Test bulk word addition."""
        words = [("test1", 10), ("test2", 20), ("test3", 30)]
        count = system.add_words_bulk(words)
        assert count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])