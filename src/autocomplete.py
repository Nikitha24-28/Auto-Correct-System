"""
Autocomplete Engine combining Trie, Spell Checker, and LRU Cache

This module integrates all components to provide intelligent autocomplete
with spell correction and efficient caching.

Author: [Your Name]
Date: 2024
"""

from typing import List, Tuple, Optional, Dict, Any
from trie import Trie
from spell_checker import SpellChecker
from lru_cache import LRUCache
import urllib.error
import time


class AutocompleteResult:
    """
    Container for autocomplete results with metadata.
    
    Attributes:
        suggestions: List of (word, frequency) tuples
        did_you_mean: Suggested correction for misspelled query
        query_time_ms: Time taken to process query in milliseconds
        from_cache: Whether result was served from cache
        spell_corrected: Whether spell correction was applied
    """
    
    def __init__(
        self,
        suggestions: List[Tuple[str, int]],
        did_you_mean: Optional[str] = None,
        query_time_ms: float = 0.0,
        from_cache: bool = False,
        spell_corrected: bool = False
    ):
        self.suggestions = suggestions
        self.did_you_mean = did_you_mean
        self.query_time_ms = query_time_ms
        self.from_cache = from_cache
        self.spell_corrected = spell_corrected
    
    def __repr__(self) -> str:
        return (f"AutocompleteResult(suggestions={len(self.suggestions)}, "
                f"did_you_mean={self.did_you_mean}, "
                f"query_time={self.query_time_ms:.2f}ms, "
                f"from_cache={self.from_cache})")


class AutocompleteSystem:
    """
    Complete autocomplete system with Trie, caching, and spell correction.
    
    Features:
    - Fast prefix-based suggestions using Trie
    - Frequency-based ranking
    - LRU cache for repeated queries
    - Spell correction for typos
    - Query analytics and statistics
    
    Time Complexity:
        - get_suggestions (cached): O(1)
        - get_suggestions (uncached): O(p + n + k log k)
        - get_suggestions_with_spell_check: O(p + n + k log k) or O(N × m × n) for spell check
    
    Example:
        >>> system = AutocompleteSystem(cache_size=1000)
        >>> system.add_word("algorithm", frequency=100)
        >>> result = system.get_suggestions("algo")
        >>> print(result.suggestions)
        [('algorithm', 100)]
    """
    
    def __init__(self, cache_size: int = 1000, enable_spell_check: bool = True):
        """
        Initialize the autocomplete system.
        
        Args:
            cache_size: Maximum number of cached queries (default: 1000)
            enable_spell_check: Whether to enable spell correction (default: True)
        """
        self.trie = Trie()
        self.cache = LRUCache(capacity=cache_size)
        self.spell_checker = SpellChecker()
        self.enable_spell_check = enable_spell_check
        
        # Analytics
        self.query_count = 0
        self.total_query_time = 0.0
    
    def add_word(self, word: str, frequency: int = 1) -> bool:
        """
        Add a word to the autocomplete dictionary.
        
        Args:
            word: The word to add
            frequency: Usage frequency (default: 1)
        
        Returns:
            True if word was added successfully
        
        Example:
            >>> system.add_word("python", frequency=95)
            True
        """
        if not word or not word.strip():
            return False
        
        self.trie.insert(word, frequency)
        
        # Invalidate cache since dictionary changed
        self.cache.clear()
        
        return True
    
    def add_words_bulk(self, words: List[Tuple[str, int]]) -> int:
        """
        Add multiple words efficiently.
        
        Args:
            words: List of (word, frequency) tuples
        
        Returns:
            Number of words successfully added
        
        Example:
            >>> words = [("python", 95), ("java", 90), ("javascript", 88)]
            >>> system.add_words_bulk(words)
            3
        """
        count = 0
        for word, frequency in words:
            if self.add_word(word, frequency):
                count += 1
        return count
    
    def update_frequency(self, word: str, frequency: int) -> bool:
        """
        Update the frequency of an existing word.
        
        Args:
            word: The word to update
            frequency: New frequency value
        
        Returns:
            True if word exists and was updated
        """
        success = self.trie.update_frequency(word, frequency)
        if success:
            self.cache.clear()
        return success
    
    def increment_frequency(self, word: str, amount: int = 1) -> bool:
        """
        Increment word frequency (useful for click tracking).
        
        Args:
            word: The word that was selected
            amount: Amount to increment (default: 1)
        
        Returns:
            True if successful
        
        Example:
            >>> system.increment_frequency("algorithm")  # User clicked this suggestion
            True
        """
        if not self.trie.search(word):
            return False
        
        # Get all words to find current frequency
        all_words = dict(self.trie.get_all_words())
        if word.lower() in all_words:
            current_freq = all_words[word.lower()]
            return self.update_frequency(word, current_freq + amount)
        
        return False
    
    def get_suggestions(
        self,
        prefix: str,
        k: int = 10,
        use_cache: bool = True
    ) -> AutocompleteResult:
        """
        Get autocomplete suggestions for a prefix.
        
        Args:
            prefix: The prefix to search for
            k: Maximum number of suggestions (default: 10)
            use_cache: Whether to use cache (default: True)
        
        Returns:
            AutocompleteResult with suggestions and metadata
        
        Time Complexity: O(1) if cached, O(p + n + k log k) otherwise
        
        Example:
            >>> result = system.get_suggestions("algo", k=5)
            >>> for word, freq in result.suggestions:
            ...     print(f"{word}: {freq}")
            algorithm: 100
            algorithms: 85
        """
        start_time = time.time()
        self.query_count += 1
        
        if not prefix or not prefix.strip():
            return AutocompleteResult([], query_time_ms=0.0)
        
        prefix = prefix.strip()
        cache_key = f"{prefix.lower()}_{k}"
        
        # Check cache
        from_cache = False
        if use_cache and self.cache.has(cache_key):
            suggestions = self.cache.get(cache_key)
            from_cache = True
        else:
            # Get from Trie
            suggestions = self.trie.get_suggestions(prefix, k)
            
            # Cache result
            if use_cache:
                self.cache.set(cache_key, suggestions)
        
        query_time = (time.time() - start_time) * 1000
        self.total_query_time += query_time
        
        return AutocompleteResult(
            suggestions=suggestions,
            query_time_ms=query_time,
            from_cache=from_cache
        )
    
    def get_suggestions_with_spell_check(
        self,
        query: str,
        k: int = 10,
        max_edit_distance: int = 2
    ) -> AutocompleteResult:
        """
        Get suggestions with automatic spell correction for typos.
        
        If exact prefix matches are found, return those.
        Otherwise, find similar words within edit distance.
        
        Args:
            query: The search query (may contain typos)
            k: Maximum number of suggestions
            max_edit_distance: Maximum edit distance for spell correction (default: 2)
        
        Returns:
            AutocompleteResult with suggestions and spell correction info
        
        Example:
            >>> result = system.get_suggestions_with_spell_check("algoritm")
            >>> print(result.did_you_mean)
            'algorithm'
            >>> print(result.spell_corrected)
            True
        """
        start_time = time.time()
        self.query_count += 1
        
        if not query or not query.strip():
            return AutocompleteResult([], query_time_ms=0.0)
        
        query = query.strip()
        
        # First, try exact prefix match
        result = self.get_suggestions(query, k, use_cache=True)
        
        if result.suggestions:
            # Found exact matches
            query_time = (time.time() - start_time) * 1000
            self.total_query_time += query_time
            return AutocompleteResult(
                suggestions=result.suggestions,
                query_time_ms=query_time,
                from_cache=result.from_cache
            )
        
        # No exact matches, try spell correction if enabled
        if not self.enable_spell_check:
            query_time = (time.time() - start_time) * 1000
            return AutocompleteResult([], query_time_ms=query_time)
        
        # Get all words for spell checking
        all_words = self.trie.get_all_words()
        
        # Find similar words
        similar = self.spell_checker.find_similar(
            query,
            all_words,
            max_distance=max_edit_distance,
            k=k
        )
        
        # Convert to (word, frequency) format
        suggestions = [(word, freq) for word, freq, dist in similar]
        
        # Get the best correction suggestion
        did_you_mean = similar[0][0] if similar else None
        
        query_time = (time.time() - start_time) * 1000
        self.total_query_time += query_time
        
        return AutocompleteResult(
            suggestions=suggestions,
            did_you_mean=did_you_mean,
            query_time_ms=query_time,
            from_cache=False,
            spell_corrected=True
        )
    
    def search_word(self, word: str) -> bool:
        """
        Check if a word exists in the dictionary.
        
        Args:
            word: The word to search for
        
        Returns:
            True if word exists, False otherwise
        """
        return self.trie.search(word)
    
    def delete_word(self, word: str) -> bool:
        """
        Delete a word from the dictionary.
        
        Args:
            word: The word to delete
        
        Returns:
            True if word was deleted, False if not found
        """
        success = self.trie.delete(word)
        if success:
            self.cache.clear()
        return success
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics.
        
        Returns:
            Dictionary with system stats
        
        Example:
            >>> stats = system.get_statistics()
            >>> print(f"Cache hit rate: {stats['cache_hit_rate']:.2f}%")
            Cache hit rate: 78.50%
        """
        cache_stats = self.cache.get_stats()
        trie_stats = self.trie.get_stats()
        
        avg_query_time = (
            self.total_query_time / self.query_count
            if self.query_count > 0 else 0
        )
        
        return {
            # Trie stats
            'total_words': trie_stats['total_words'],
            'total_nodes': trie_stats['total_nodes'],
            
            # Cache stats
            'cache_capacity': cache_stats['capacity'],
            'cache_size': cache_stats['size'],
            'cache_hits': cache_stats['hits'],
            'cache_misses': cache_stats['misses'],
            'cache_hit_rate': cache_stats['hit_rate'],
            'cache_evictions': cache_stats['evictions'],
            
            # Query stats
            'total_queries': self.query_count,
            'avg_query_time_ms': round(avg_query_time, 2),
            'total_query_time_ms': round(self.total_query_time, 2),
            
            # Feature flags
            'spell_check_enabled': self.enable_spell_check
        }
    
    def reset_statistics(self) -> None:
        """Reset all statistics counters."""
        self.query_count = 0
        self.total_query_time = 0.0
        self.cache.reset_stats()
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self.cache.clear()
    
    def load_dictionary(self, filepath: str, delimiter: str = '\t') -> int:
        """
        Load dictionary from a file.
        
        Expected format: word<delimiter>frequency
        
        Args:
            filepath: Path to dictionary file
            delimiter: Delimiter between word and frequency (default: tab)
        
        Returns:
            Number of words loaded
        
        Example:
            >>> count = system.load_dictionary('dictionary.txt')
            >>> print(f"Loaded {count} words")
            Loaded 50000 words
        """
        count = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(delimiter)
                    
                    if len(parts) >= 2:
                        word = parts[0].strip()
                        try:
                            frequency = int(parts[1].strip())
                        except ValueError:
                            frequency = 1
                    else:
                        word = parts[0].strip()
                        frequency = 1
                    
                    if word:
                        self.add_word(word, frequency)
                        count += 1
        
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            return 0
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return count
        
        return count
    
    def load_from_api(self, limit: int = 10000) -> int:
        """
        Load dictionary from online API.
        
        Args:
            limit: Maximum number of words to load (default: 10000)
        
        Returns:
            Number of words loaded
        
        Example:
            >>> count = system.load_from_api(limit=5000)
            >>> print(f"Loaded {count} words from API")
            Loaded 5000 words from API
        """
        import urllib.request
        import random
        
        print(f"⏳ Downloading dictionary from API...")
        
        # Try multiple sources in order of preference
        sources = [
            {
                'name': 'Princeton WordNet',
                'url': 'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa.txt',
                'description': 'Top 10,000 most common English words'
            },
            {
                'name': 'MIT Word List',
                'url': 'https://www.mit.edu/~ecprice/wordlist.10000',
                'description': '10,000 common words'
            },
            {
                'name': 'English Words Repository',
                'url': 'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt',
                'description': '370,000+ English words'
            }
        ]
        
        for source in sources:
            try:
                print(f"📡 Trying {source['name']}...")
                
                response = urllib.request.urlopen(source['url'], timeout=10)
                content = response.read().decode('utf-8')
                
                # Parse words
                words = content.strip().split('\n')
                words = [w.strip().lower() for w in words if w.strip() and len(w.strip()) > 1]
                
                # Limit to requested amount
                words = words[:limit]
                
                if not words:
                    print(f"⚠️  No words found, trying next source...")
                    continue
                
                print(f"📥 Downloaded {len(words)} words from {source['name']}")
                print(f"⚙️  Adding to dictionary...")
                
                # Add words with intelligent frequency assignment
                count = 0
                for i, word in enumerate(words):
                    # Assign frequency based on:
                    # 1. Position in list (earlier = more common)
                    # 2. Word characteristics
                    
                    base_freq = 1000 - int((i / len(words)) * 700)  # 1000 to 300
                    
                    # Boost for tech/programming words
                    if any(tech in word for tech in ['data', 'code', 'algorithm', 'program', 'computer', 
                                                       'software', 'python', 'java', 'web', 'api']):
                        freq = min(1000, base_freq + 200)
                    # Boost for short common words
                    elif len(word) < 5:
                        freq = min(1000, base_freq + 100)
                    else:
                        freq = base_freq
                    
                    if self.add_word(word, freq):
                        count += 1
                    
                    # Show progress for large datasets
                    if count % 1000 == 0 and count > 0:
                        print(f"   ... {count} words added")
                
                print(f"✅ Successfully loaded {count} words from {source['name']}!")
                return count
                
            except urllib.error.URLError as e:
                print(f"⚠️  Could not connect to {source['name']}: {e}")
                print(f"   Trying next source...")
                continue
            except Exception as e:
                print(f"⚠️  Error with {source['name']}: {e}")
                print(f"   Trying next source...")
                continue
        
        # If all sources fail
        print(f"❌ Could not load dictionary from any API source")
        print(f"💡 Try option 1 (sample dictionary) or option 2 (local file) instead")
        return 0
    
    def save_dictionary(self, filepath: str, delimiter: str = '\t') -> bool:
        """
        Save current dictionary to a file.
        
        Args:
            filepath: Path to save dictionary
            delimiter: Delimiter between word and frequency
        
        Returns:
            True if successful, False otherwise
        """
        try:
            all_words = self.trie.get_all_words()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for word, frequency in sorted(all_words):
                    f.write(f"{word}{delimiter}{frequency}\n")
            
            return True
        
        except Exception as e:
            print(f"Error saving dictionary: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation of the system."""
        stats = self.get_statistics()
        return (f"AutocompleteSystem("
                f"words={stats['total_words']}, "
                f"queries={stats['total_queries']}, "
                f"cache_hit_rate={stats['cache_hit_rate']:.1f}%)")


class MultiLanguageAutocomplete:
    """
    Extended autocomplete system supporting multiple languages.
    
    Each language has its own Trie but shares the cache system.
    """
    
    def __init__(self, cache_size: int = 1000):
        """
        Initialize multi-language system.
        
        Args:
            cache_size: Shared cache size across all languages
        """
        self.systems: Dict[str, AutocompleteSystem] = {}
        self.cache_size = cache_size
        self.default_language = 'en'
    
    def add_language(self, language_code: str) -> None:
        """
        Add support for a new language.
        
        Args:
            language_code: ISO language code (e.g., 'en', 'es', 'fr')
        """
        if language_code not in self.systems:
            self.systems[language_code] = AutocompleteSystem(
                cache_size=self.cache_size
            )
    
    def get_suggestions(
        self,
        prefix: str,
        language: str = 'en',
        k: int = 10
    ) -> AutocompleteResult:
        """Get suggestions for a specific language."""
        if language not in self.systems:
            self.add_language(language)
        
        return self.systems[language].get_suggestions(prefix, k)
    
    def add_word(self, word: str, language: str = 'en', frequency: int = 1) -> bool:
        """Add word to specific language dictionary."""
        if language not in self.systems:
            self.add_language(language)
        
        return self.systems[language].add_word(word, frequency)