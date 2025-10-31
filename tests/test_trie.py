"""
Unit tests for Trie data structure

Author: [Your Name]
Date: 2024

Run tests: python -m pytest tests/test_trie.py -v
"""

import pytest
import sys
sys.path.insert(0, '../src')
from trie import Trie, TrieNode


class TestTrieNode:
    """Test cases for TrieNode class."""
    
    def test_node_initialization(self):
        """Test TrieNode initialization."""
        node = TrieNode()
        assert node.children == {}
        assert node.is_end_of_word == False
        assert node.frequency == 0
        assert node.word is None
    
    def test_node_children_addition(self):
        """Test adding children to node."""
        node = TrieNode()
        node.children['a'] = TrieNode()
        node.children['b'] = TrieNode()
        
        assert 'a' in node.children
        assert 'b' in node.children
        assert 'c' not in node.children


class TestTrieBasicOperations:
    """Test cases for basic Trie operations."""
    
    @pytest.fixture
    def trie(self):
        """Create a fresh Trie instance for each test."""
        return Trie()
    
    def test_empty_trie(self, trie):
        """Test newly created Trie is empty."""
        assert trie.total_words == 0
        assert trie.search("anything") == False
    
    def test_insert_single_word(self, trie):
        """Test inserting a single word."""
        trie.insert("hello", frequency=10)
        
        assert trie.total_words == 1
        assert trie.search("hello") == True
        assert trie.search("hell") == False
    
    def test_insert_multiple_words(self, trie):
        """Test inserting multiple words."""
        words = [("hello", 10), ("world", 20), ("help", 15)]
        
        for word, freq in words:
            trie.insert(word, freq)
        
        assert trie.total_words == 3
        assert all(trie.search(word) for word, _ in words)
    
    def test_insert_duplicate_updates_frequency(self, trie):
        """Test inserting duplicate word updates frequency."""
        trie.insert("hello", frequency=10)
        assert trie.total_words == 1
        
        trie.insert("hello", frequency=20)
        assert trie.total_words == 1  # Should not increase
        
        suggestions = trie.get_suggestions("hel", k=1)
        assert suggestions[0][1] == 20  # Updated frequency
    
    def test_insert_with_prefix_overlap(self, trie):
        """Test inserting words with common prefixes."""
        trie.insert("car", frequency=10)
        trie.insert("card", frequency=20)
        trie.insert("care", frequency=15)
        trie.insert("careful", frequency=5)
        
        assert trie.total_words == 4
        assert trie.search("car") == True
        assert trie.search("card") == True
        assert trie.search("care") == True
        assert trie.search("careful") == True
    
    def test_insert_empty_string(self, trie):
        """Test inserting empty string does nothing."""
        trie.insert("", frequency=10)
        assert trie.total_words == 0
        
        trie.insert("   ", frequency=10)  # Whitespace only
        assert trie.total_words == 0
    
    def test_case_insensitive_insert(self, trie):
        """Test that insert is case-insensitive."""
        trie.insert("Hello", frequency=10)
        trie.insert("HELLO", frequency=20)
        
        assert trie.total_words == 1
        assert trie.search("hello") == True
        assert trie.search("Hello") == True
        assert trie.search("HELLO") == True


class TestTrieSearch:
    """Test cases for Trie search operations."""
    
    @pytest.fixture
    def populated_trie(self):
        """Create a Trie with sample data."""
        trie = Trie()
        words = ["algorithm", "algorithms", "data", "database", "structure"]
        for word in words:
            trie.insert(word, frequency=100)
        return trie
    
    def test_search_existing_word(self, populated_trie):
        """Test searching for existing words."""
        assert populated_trie.search("algorithm") == True
        assert populated_trie.search("data") == True
    
    def test_search_non_existing_word(self, populated_trie):
        """Test searching for non-existing words."""
        assert populated_trie.search("algo") == False
        assert populated_trie.search("xyz") == False
    
    def test_search_prefix_not_word(self, populated_trie):
        """Test that prefix alone is not found as complete word."""
        assert populated_trie.search("alg") == False
        assert populated_trie.search("dat") == False
    
    def test_starts_with_valid_prefix(self, populated_trie):
        """Test starts_with for valid prefixes."""
        assert populated_trie.starts_with("algo") == True
        assert populated_trie.starts_with("dat") == True
        assert populated_trie.starts_with("struct") == True
    
    def test_starts_with_invalid_prefix(self, populated_trie):
        """Test starts_with for invalid prefixes."""
        assert populated_trie.starts_with("xyz") == False
        assert populated_trie.starts_with("zzz") == False
    
    def test_starts_with_complete_word(self, populated_trie):
        """Test starts_with with complete words."""
        assert populated_trie.starts_with("algorithm") == True
        assert populated_trie.starts_with("data") == True


class TestTrieDelete:
    """Test cases for Trie delete operations."""
    
    @pytest.fixture
    def trie(self):
        """Create a Trie with sample data."""
        trie = Trie()
        trie.insert("hello", frequency=10)
        trie.insert("help", frequency=20)
        trie.insert("hero", frequency=15)
        return trie
    
    def test_delete_existing_word(self, trie):
        """Test deleting an existing word."""
        assert trie.delete("hello") == True
        assert trie.search("hello") == False
        assert trie.total_words == 2
    
    def test_delete_non_existing_word(self, trie):
        """Test deleting non-existing word."""
        assert trie.delete("world") == False
        assert trie.total_words == 3
    
    def test_delete_preserves_other_words(self, trie):
        """Test that deleting one word doesn't affect others."""
        trie.delete("hello")
        
        assert trie.search("help") == True
        assert trie.search("hero") == True
    
    def test_delete_word_with_shared_prefix(self, trie):
        """Test deleting word that shares prefix with others."""
        trie.insert("helping", frequency=25)
        trie.delete("help")
        
        assert trie.search("help") == False
        assert trie.search("helping") == True
        assert trie.starts_with("hel") == True


class TestTrieSuggestions:
    """Test cases for Trie autocomplete suggestions."""
    
    @pytest.fixture
    def trie(self):
        """Create a Trie with sample data."""
        trie = Trie()
        words = [
            ("algorithm", 100),
            ("algorithms", 80),
            ("algorithmic", 50),
            ("algebra", 90),
            ("algebraic", 60),
            ("alpha", 70),
            ("alphabet", 75)
        ]
        for word, freq in words:
            trie.insert(word, freq)
        return trie
    
    def test_get_suggestions_basic(self, trie):
        """Test basic suggestion retrieval."""
        suggestions = trie.get_suggestions("alg", k=5)
        
        assert len(suggestions) <= 5
        assert all(word.startswith("alg") for word, _ in suggestions)
    
    def test_get_suggestions_frequency_ordering(self, trie):
        """Test that suggestions are ordered by frequency."""
        suggestions = trie.get_suggestions("algo", k=10)
        
        # Should be ordered by frequency (descending)
        frequencies = [freq for _, freq in suggestions]
        assert frequencies == sorted(frequencies, reverse=True)
    
    def test_get_suggestions_respects_k(self, trie):
        """Test that k parameter limits results."""
        suggestions = trie.get_suggestions("al", k=3)
        assert len(suggestions) == 3
        
        suggestions = trie.get_suggestions("al", k=10)
        assert len(suggestions) <= 10
    
    def test_get_suggestions_empty_prefix(self, trie):
        """Test suggestions with empty prefix."""
        suggestions = trie.get_suggestions("", k=10)
        assert len(suggestions) == 0
    
    def test_get_suggestions_no_matches(self, trie):
        """Test suggestions with prefix that has no matches."""
        suggestions = trie.get_suggestions("xyz", k=10)
        assert len(suggestions) == 0
    
    def test_get_suggestions_single_match(self, trie):
        """Test suggestions when only one word matches."""
        trie_single = Trie()
        trie_single.insert("unique", frequency=100)
        
        suggestions = trie_single.get_suggestions("uni", k=10)
        assert len(suggestions) == 1
        assert suggestions[0][0] == "unique"


class TestTrieFrequencyManagement:
    """Test cases for frequency tracking and updates."""
    
    @pytest.fixture
    def trie(self):
        """Create a Trie instance."""
        return Trie()
    
    def test_frequency_tracking(self, trie):
        """Test that frequency is properly tracked."""
        trie.insert("word", frequency=50)
        suggestions = trie.get_suggestions("wor", k=1)
        
        assert suggestions[0][1] == 50
    
    def test_update_frequency_existing_word(self, trie):
        """Test updating frequency of existing word."""
        trie.insert("word", frequency=50)
        assert trie.update_frequency("word", 100) == True
        
        suggestions = trie.get_suggestions("wor", k=1)
        assert suggestions[0][1] == 100
    
    def test_update_frequency_non_existing_word(self, trie):
        """Test updating frequency of non-existing word."""
        assert trie.update_frequency("nonexistent", 100) == False
    
    def test_frequency_affects_ranking(self, trie):
        """Test that frequency affects suggestion ranking."""
        trie.insert("apple", frequency=50)
        trie.insert("application", frequency=100)
        trie.insert("apply", frequency=75)
        
        suggestions = trie.get_suggestions("app", k=3)
        
        # Should be ordered: application (100), apply (75), apple (50)
        assert suggestions[0][0] == "application"
        assert suggestions[1][0] == "apply"
        assert suggestions[2][0] == "apple"


class TestTrieEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_single_character_words(self):
        """Test with single character words."""
        trie = Trie()
        trie.insert("a", frequency=10)
        trie.insert("i", frequency=20)
        
        assert trie.search("a") == True
        assert trie.search("i") == True
        assert trie.total_words == 2
    
    def test_very_long_word(self):
        """Test with very long words."""
        trie = Trie()
        long_word = "a" * 1000
        
        trie.insert(long_word, frequency=10)
        assert trie.search(long_word) == True
    
    def test_special_characters(self):
        """Test with special characters."""
        trie = Trie()
        trie.insert("hello-world", frequency=10)
        trie.insert("test_case", frequency=20)
        
        assert trie.search("hello-world") == True
        assert trie.search("test_case") == True
    
    def test_numbers_in_words(self):
        """Test words containing numbers."""
        trie = Trie()
        trie.insert("test123", frequency=10)
        trie.insert("abc456", frequency=20)
        
        assert trie.search("test123") == True
        assert trie.search("abc456") == True
    
    def test_unicode_characters(self):
        """Test with unicode characters."""
        trie = Trie()
        trie.insert("café", frequency=10)
        trie.insert("naïve", frequency=20)
        
        assert trie.search("café") == True
        assert trie.search("naïve") == True


class TestTrieStatistics:
    """Test Trie statistics and metadata."""
    
    def test_get_all_words(self):
        """Test retrieving all words from Trie."""
        trie = Trie()
        words = [("hello", 10), ("world", 20), ("test", 15)]
        
        for word, freq in words:
            trie.insert(word, freq)
        
        all_words = trie.get_all_words()
        assert len(all_words) == 3
        assert set(word for word, _ in all_words) == {"hello", "world", "test"}
    
    def test_get_stats(self):
        """Test getting Trie statistics."""
        trie = Trie()
        trie.insert("hello", frequency=10)
        trie.insert("help", frequency=20)
        
        stats = trie.get_stats()
        
        assert stats['total_words'] == 2
        assert stats['total_nodes'] > 0


class TestTriePerformance:
    """Test performance characteristics."""
    
    def test_large_dictionary_insertion(self):
        """Test inserting large number of words."""
        trie = Trie()
        
        # Insert 10,000 words
        for i in range(10000):
            trie.insert(f"word{i}", frequency=i)
        
        assert trie.total_words == 10000
    
    def test_large_dictionary_search(self):
        """Test searching in large dictionary."""
        trie = Trie()
        
        # Insert 1,000 words
        for i in range(1000):
            trie.insert(f"test{i}", frequency=i)
        
        # Search should still be fast
        assert trie.search("test500") == True
        assert trie.search("test999") == True
        assert trie.search("test1000") == False
    
    def test_suggestions_performance(self):
        """Test suggestion retrieval with many words."""
        trie = Trie()
        
        # Insert many words with same prefix
        for i in range(100):
            trie.insert(f"prefix{i}", frequency=100-i)
        
        suggestions = trie.get_suggestions("pre", k=10)
        
        # Should return top 10 by frequency
        assert len(suggestions) == 10
        assert suggestions[0][1] == 100  # Highest frequency


if __name__ == "__main__":
    pytest.main([__file__, "-v"])