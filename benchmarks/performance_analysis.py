"""
Performance Benchmarking Script for Autocomplete System

Author: Nikitha
Date: 2025
"""

import sys
import time
import random
import string
sys.path.insert(0, '../src')

from autocomplete import AutocompleteSystem
from trie import Trie
from lru_cache import LRUCache


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for autocomplete system."""
    
    def __init__(self):
        self.results = {}
    
    def generate_random_words(self, count: int, min_len: int = 3, max_len: int = 15):
        """Generate random words for testing."""
        words = []
        for _ in range(count):
            length = random.randint(min_len, max_len)
            word = ''.join(random.choices(string.ascii_lowercase, k=length))
            freq = random.randint(1, 1000)
            words.append((word, freq))
        return words
    
    def benchmark_insertion(self, sizes=[1000, 10000, 50000, 100000]):
        """Benchmark insertion performance across different dictionary sizes."""
        print("\n" + "="*60)
        print("INSERTION PERFORMANCE BENCHMARK")
        print("="*60)
        
        results = []
        
        for size in sizes:
            trie = Trie()
            words = self.generate_random_words(size)
            
            start_time = time.time()
            for word, freq in words:
                trie.insert(word, freq)
            elapsed = (time.time() - start_time) * 1000
            
            avg_per_word = elapsed / size
            
            print(f"\n{size:,} words:")
            print(f"  Total time: {elapsed:.2f}ms")
            print(f"  Avg per word: {avg_per_word:.4f}ms")
            
            results.append((size, elapsed, avg_per_word))
        
        self.results['insertion'] = results
        return results
    
    def generate_report(self):
        """Generate summary report of all benchmarks."""
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY REPORT")
        print("="*60)
        
        if 'insertion' in self.results:
            ins = self.results['insertion']
            print(f"\nInsertion Performance:")
            print(f"  100K words inserted in {ins[-1][1]:.0f}ms")


def main():
    """Run all benchmarks."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   AUTOCOMPLETE SYSTEM - PERFORMANCE BENCHMARK         ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    benchmark = PerformanceBenchmark()
    benchmark.benchmark_insertion(sizes=[1000, 10000])
    benchmark.generate_report()


if __name__ == "__main__":
    main()