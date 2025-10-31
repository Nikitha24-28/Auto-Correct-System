"""
Performance tests for Autocomplete System

Run: pytest tests/test_performance.py -v --benchmark
"""

import pytest
import sys
import time
sys.path.insert(0, '../src')
from autocomplete import AutocompleteSystem
from trie import Trie


class TestPerformance:
    """Performance-focused tests."""
    
    @pytest.fixture
    def large_system(self):
        """Create system with 10K words."""
        system = AutocompleteSystem(cache_size=1000)
        for i in range(10000):
            system.add_word(f"word{i}", frequency=i)
        return system
    
    def test_insertion_speed(self):
        """Test insertion performance."""
        trie = Trie()
        
        start = time.time()
        for i in range(1000):
            trie.insert(f"test{i}", frequency=i)
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # Should complete in < 500ms
    
    def test_query_latency(self, large_system):
        """Test query latency with large dictionary."""
        start = time.time()
        result = large_system.get_suggestions("word", k=10)
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 10  # Should be < 10ms
    
    def test_cache_speedup(self, large_system):
        """Test cache provides speedup."""
        # Cold cache
        start1 = time.time()
        large_system.get_suggestions("word", k=10, use_cache=False)
        time_cold = (time.time() - start1) * 1000
        
        # Warm cache (run twice)
        large_system.get_suggestions("word", k=10, use_cache=True)
        start2 = time.time()
        large_system.get_suggestions("word", k=10, use_cache=True)
        time_warm = (time.time() - start2) * 1000
        
        speedup = time_cold / time_warm if time_warm > 0 else 0
        assert speedup > 2  # At least 2x speedup
    
    def test_memory_efficiency(self):
        """Test memory doesn't grow excessively."""
        import sys
        
        trie = Trie()
        for i in range(1000):
            trie.insert(f"test{i}", frequency=i)
        
        size = sys.getsizeof(trie)
        assert size < 10 * 1024 * 1024  # Less than 10MB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])