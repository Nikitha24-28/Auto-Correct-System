"""
Trie (Prefix Tree) Implementation for Autocomplete System

This module implements a Trie data structure optimized for prefix-based searches
and autocomplete functionality with frequency tracking.

Author: [Your Name]
Date: 2024
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import heapq


class TrieNode:
    """
    Node in the Trie data structure.
    
    Attributes:
        children: Dictionary mapping characters to child TrieNodes
        is_end_of_word: Boolean indicating if this node marks the end of a valid word
        frequency: Integer representing how often this word has been searched/used
        word: The complete word if this is an end node
    """
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.frequency: int = 0
        self.word: Optional[str] = None


class Trie:
    """
    Trie (Prefix Tree) data structure for efficient prefix-based operations.
    
    The Trie supports insertion, deletion, search, and prefix matching operations
    with word frequency tracking for intelligent autocomplete suggestions.
    
    Time Complexity:
        - Insert: O(m) where m is the length of the word
        - Search: O(m)
        - StartsWith: O(m)
        - Delete: O(m)
        - GetSuggestions: O(p + n + k log k) where p=prefix length, n=nodes in subtree, k=results
    
    Space Complexity: O(ALPHABET_SIZE × N × M) where N=number of words, M=avg word length
    
    Example:
        >>> trie = Trie()
        >>> trie.insert("hello", frequency=10)
        >>> trie.insert("help", frequency=5)
        >>> trie.search("hello")
        True
        >>> trie.get_suggestions("hel", k=5)
        [('hello', 10), ('help', 5)]
    """
    
    def __init__(self):
        """Initialize an empty Trie with a root node."""
        self.root = TrieNode()
        self.total_words = 0
    
    def insert(self, word: str, frequency: int = 1) -> None:
        """
        Insert a word into the Trie with associated frequency.
        
        Args:
            word: The word to insert (case-insensitive)
            frequency: The frequency/popularity of the word (default: 1)
        
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(m) in worst case (all new nodes)
        
        Example:
            >>> trie = Trie()
            >>> trie.insert("algorithm", frequency=100)
            >>> trie.insert("algorithms", frequency=50)
        """
        if not word:
            return
        
        word = word.lower().strip()
        if not word:
            return
        
        node = self.root
        
        # Traverse/create path for each character
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end of word and store metadata
        if not node.is_end_of_word:
            self.total_words += 1
        
        node.is_end_of_word = True
        node.frequency = frequency
        node.word = word
    
    def search(self, word: str) -> bool:
        """
        Check if a complete word exists in the Trie.
        
        Args:
            word: The word to search for
        
        Returns:
            True if the word exists as a complete word, False otherwise
        
        Time Complexity: O(m) where m is the length of the word
        
        Example:
            >>> trie.search("algorithm")
            True
            >>> trie.search("algo")  # Only a prefix, not a complete word
            False
        """
        node = self._find_node(word.lower().strip())
        return node is not None and node.is_end_of_word
    
    def starts_with(self, prefix: str) -> bool:
        """
        Check if any word in the Trie starts with the given prefix.
        
        Args:
            prefix: The prefix to search for
        
        Returns:
            True if at least one word starts with the prefix, False otherwise
        
        Time Complexity: O(p) where p is the length of the prefix
        
        Example:
            >>> trie.starts_with("algo")
            True
        """
        return self._find_node(prefix.lower().strip()) is not None
    
    def delete(self, word: str) -> bool:
        """
        Delete a word from the Trie.
        
        Args:
            word: The word to delete
        
        Returns:
            True if the word was found and deleted, False otherwise
        
        Time Complexity: O(m) where m is the length of the word
        
        Example:
            >>> trie.delete("algorithm")
            True
            >>> trie.delete("nonexistent")
            False
        """
        word = word.lower().strip()
        
        def _delete_helper(node: TrieNode, word: str, index: int) -> bool:
            if index == len(word):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                node.frequency = 0
                node.word = None
                self.total_words -= 1
                return len(node.children) == 0
            
            char = word[index]
            if char not in node.children:
                return False
            
            child = node.children[char]
            should_delete_child = _delete_helper(child, word, index + 1)
            
            if should_delete_child:
                del node.children[char]
                return len(node.children) == 0 and not node.is_end_of_word
            
            return False
        
        return _delete_helper(self.root, word, 0)
    
    def get_suggestions(self, prefix: str, k: int = 10) -> List[Tuple[str, int]]:
        """
        Get top-k autocomplete suggestions for a given prefix, ranked by frequency.
        
        Args:
            prefix: The prefix to search for
            k: Maximum number of suggestions to return (default: 10)
        
        Returns:
            List of tuples (word, frequency) sorted by frequency (descending)
        
        Time Complexity: O(p + n + k log k) where:
            - p = length of prefix
            - n = number of nodes in subtree
            - k = number of results
        
        Example:
            >>> trie.get_suggestions("alg", k=5)
            [('algorithm', 100), ('algorithms', 50), ('algorithmic', 30)]
        """
        prefix = prefix.lower().strip()
        
        if not prefix:
            return []
        
        # Find the node corresponding to the prefix
        prefix_node = self._find_node(prefix)
        
        if prefix_node is None:
            return []
        
        # Collect all words in the subtree
        suggestions = []
        self._collect_words(prefix_node, suggestions)
        
        # Use heap to get top-k by frequency
        # We use negative frequency for max-heap behavior
        top_k = heapq.nlargest(k, suggestions, key=lambda x: x[1])
        
        return top_k
    
    def get_all_words(self) -> List[Tuple[str, int]]:
        """
        Get all words stored in the Trie with their frequencies.
        
        Returns:
            List of tuples (word, frequency)
        
        Time Complexity: O(n) where n is the total number of nodes
        
        Example:
            >>> all_words = trie.get_all_words()
            >>> len(all_words)
            42
        """
        all_words = []
        self._collect_words(self.root, all_words)
        return all_words
    
    def update_frequency(self, word: str, frequency: int) -> bool:
        """
        Update the frequency of an existing word.
        
        Args:
            word: The word to update
            frequency: The new frequency value
        
        Returns:
            True if the word exists and was updated, False otherwise
        
        Time Complexity: O(m) where m is the length of the word
        
        Example:
            >>> trie.update_frequency("algorithm", 200)
            True
        """
        node = self._find_node(word.lower().strip())
        
        if node is None or not node.is_end_of_word:
            return False
        
        node.frequency = frequency
        return True
    
    def _find_node(self, s: str) -> Optional[TrieNode]:
        """
        Find the node corresponding to a string (prefix or word).
        
        Args:
            s: The string to search for
        
        Returns:
            The TrieNode if found, None otherwise
        
        Time Complexity: O(len(s))
        """
        node = self.root
        
        for char in s:
            if char not in node.children:
                return None
            node = node.children[char]
        
        return node
    
    def _collect_words(self, node: TrieNode, results: List[Tuple[str, int]]) -> None:
        """
        Collect all words from a subtree using DFS.
        
        Args:
            node: Starting node for collection
            results: List to append found words to
        
        Time Complexity: O(n) where n is the number of nodes in subtree
        """
        if node.is_end_of_word:
            results.append((node.word, node.frequency))
        
        for child in node.children.values():
            self._collect_words(child, results)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the Trie.
        
        Returns:
            Dictionary with statistics (total_words, total_nodes)
        """
        def count_nodes(node: TrieNode) -> int:
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        return {
            'total_words': self.total_words,
            'total_nodes': count_nodes(self.root)
        }