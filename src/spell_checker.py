"""
Spell Checker using Levenshtein Distance (Edit Distance)

This module implements spell correction functionality using dynamic programming
to calculate edit distance between words and find similar matches.

Author: [Your Name]
Date: 2024
"""

from typing import List, Tuple, Set
import heapq


class SpellChecker:
    """
    Spell checker that finds similar words using Levenshtein distance.
    
    The Levenshtein distance measures the minimum number of single-character edits
    (insertions, deletions, substitutions) required to transform one word into another.
    
    Time Complexity:
        - levenshtein_distance: O(m × n) where m, n are word lengths
        - find_similar: O(N × m × n) where N is dictionary size
    
    Example:
        >>> checker = SpellChecker()
        >>> distance = checker.levenshtein_distance("kitten", "sitting")
        >>> print(distance)  # 3 edits
        3
    """
    
    @staticmethod
    def levenshtein_distance(word1: str, word2: str) -> int:
        """
        Calculate the Levenshtein distance between two words using Dynamic Programming.
        
        The algorithm uses a 2D DP table where dp[i][j] represents the minimum
        edit distance between word1[0...i-1] and word2[0...j-1].
        
        Args:
            word1: First word
            word2: Second word
        
        Returns:
            Minimum number of edits (insertions, deletions, substitutions) needed
        
        Time Complexity: O(m × n) where m, n are the lengths of the words
        Space Complexity: O(m × n) for the DP table
        
        Example:
            >>> SpellChecker.levenshtein_distance("algorithm", "altorithm")
            2
            >>> SpellChecker.levenshtein_distance("hello", "helo")
            1
        """
        m, n = len(word1), len(word2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Base cases: empty string transformations
        for i in range(m + 1):
            dp[i][0] = i  # Delete all characters from word1
        
        for j in range(n + 1):
            dp[0][j] = j  # Insert all characters to get word2
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    # Characters match, no operation needed
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Take minimum of three operations
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Deletion
                        dp[i][j - 1],      # Insertion
                        dp[i - 1][j - 1]   # Substitution
                    )
        
        return dp[m][n]
    
    @staticmethod
    def levenshtein_distance_optimized(word1: str, word2: str) -> int:
        """
        Space-optimized version using only two rows.
        
        Args:
            word1: First word
            word2: Second word
        
        Returns:
            Minimum edit distance
        
        Time Complexity: O(m × n)
        Space Complexity: O(min(m, n))
        """
        # Ensure word1 is the shorter word for space optimization
        if len(word1) > len(word2):
            word1, word2 = word2, word1
        
        m, n = len(word1), len(word2)
        
        # Use only two rows
        prev_row = list(range(n + 1))
        curr_row = [0] * (n + 1)
        
        for i in range(1, m + 1):
            curr_row[0] = i
            
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    curr_row[j] = prev_row[j - 1]
                else:
                    curr_row[j] = 1 + min(
                        prev_row[j],      # Deletion
                        curr_row[j - 1],  # Insertion
                        prev_row[j - 1]   # Substitution
                    )
            
            prev_row, curr_row = curr_row, prev_row
        
        return prev_row[n]
    
    @staticmethod
    def find_similar(
        word: str,
        dictionary: List[Tuple[str, int]],
        max_distance: int = 2,
        k: int = 5
    ) -> List[Tuple[str, int, int]]:
        """
        Find similar words in dictionary within max edit distance.
        
        Returns words sorted by:
        1. Edit distance (ascending)
        2. Frequency (descending)
        
        Args:
            word: The misspelled word
            dictionary: List of (word, frequency) tuples
            max_distance: Maximum edit distance to consider (default: 2)
            k: Maximum number of suggestions to return (default: 5)
        
        Returns:
            List of tuples (word, frequency, distance) sorted by relevance
        
        Time Complexity: O(N × m × n) where N is dictionary size
        
        Example:
            >>> dictionary = [("algorithm", 100), ("logarithm", 50)]
            >>> SpellChecker.find_similar("algoritm", dictionary, max_distance=2, k=3)
            [('algorithm', 100, 1), ('logarithm', 50, 2)]
        """
        word = word.lower().strip()
        similar_words = []
        
        for dict_word, frequency in dictionary:
            # Skip exact matches
            if word == dict_word.lower():
                continue
            
            distance = SpellChecker.levenshtein_distance(word, dict_word.lower())
            
            if distance <= max_distance:
                similar_words.append((dict_word, frequency, distance))
        
        # Sort by distance (ascending), then by frequency (descending)
        similar_words.sort(key=lambda x: (x[2], -x[1]))
        
        return similar_words[:k]
    
    @staticmethod
    def get_word_variations(word: str, max_distance: int = 1) -> Set[str]:
        """
        Generate all possible variations of a word within max_distance edits.
        
        This can be used for more efficient fuzzy search by pre-generating
        possible variations.
        
        Args:
            word: The original word
            max_distance: Maximum edit distance (default: 1)
        
        Returns:
            Set of possible word variations
        
        Example:
            >>> variations = SpellChecker.get_word_variations("cat", max_distance=1)
            >>> "hat" in variations  # One substitution
            True
        """
        if max_distance == 0:
            return {word}
        
        variations = {word}
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
        # Deletions
        for i in range(len(word)):
            variations.add(word[:i] + word[i+1:])
        
        # Substitutions
        for i in range(len(word)):
            for char in alphabet:
                if char != word[i]:
                    variations.add(word[:i] + char + word[i+1:])
        
        # Insertions
        for i in range(len(word) + 1):
            for char in alphabet:
                variations.add(word[:i] + char + word[i:])
        
        # Transpositions (swapping adjacent characters)
        for i in range(len(word) - 1):
            variations.add(word[:i] + word[i+1] + word[i] + word[i+2:])
        
        # Recursively generate for max_distance > 1
        if max_distance > 1:
            extended_variations = set(variations)
            for variant in list(variations):
                extended_variations.update(
                    SpellChecker.get_word_variations(variant, max_distance - 1)
                )
            variations = extended_variations
        
        return variations
    
    @staticmethod
    def suggest_corrections(
        word: str,
        dictionary: List[Tuple[str, int]],
        threshold: float = 0.7,
        k: int = 5
    ) -> List[Tuple[str, int, float]]:
        """
        Suggest corrections with confidence scores.
        
        Args:
            word: The potentially misspelled word
            dictionary: List of (word, frequency) tuples
            threshold: Minimum similarity threshold (0-1)
            k: Maximum number of suggestions
        
        Returns:
            List of tuples (word, frequency, confidence_score)
        
        Example:
            >>> suggestions = SpellChecker.suggest_corrections("algoritm", dictionary)
            >>> suggestions[0]
            ('algorithm', 100, 0.89)
        """
        word = word.lower().strip()
        suggestions = []
        
        for dict_word, frequency in dictionary:
            distance = SpellChecker.levenshtein_distance(word, dict_word.lower())
            max_len = max(len(word), len(dict_word))
            
            # Calculate similarity score (1 - normalized distance)
            similarity = 1 - (distance / max_len) if max_len > 0 else 0
            
            if similarity >= threshold:
                suggestions.append((dict_word, frequency, similarity))
        
        # Sort by similarity (descending), then frequency (descending)
        suggestions.sort(key=lambda x: (-x[2], -x[1]))
        
        return suggestions[:k]


class AdvancedSpellChecker(SpellChecker):
    """
    Advanced spell checker with additional features like phonetic matching
    and common mistake patterns.
    """
    
    # Common keyboard adjacency mistakes
    KEYBOARD_ADJACENT = {
        'q': 'wa', 'w': 'qeas', 'e': 'wrds', 'r': 'etfd', 't': 'rygf',
        'y': 'tuhg', 'u': 'yijh', 'i': 'uokj', 'o': 'iplk', 'p': 'ol',
        'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc', 'g': 'ftyhbv',
        'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
        'n': 'bhjm', 'm': 'njk'
    }
    
    @staticmethod
    def keyboard_distance(word1: str, word2: str) -> float:
        """
        Calculate distance considering keyboard layout (typos).
        
        Args:
            word1: First word
            word2: Second word
        
        Returns:
            Weighted distance considering keyboard proximity
        """
        if len(word1) != len(word2):
            return float('inf')
        
        distance = 0.0
        
        for c1, c2 in zip(word1.lower(), word2.lower()):
            if c1 == c2:
                continue
            elif c2 in AdvancedSpellChecker.KEYBOARD_ADJACENT.get(c1, ''):
                distance += 0.5  # Adjacent key, likely typo
            else:
                distance += 1.0  # Different key
        
        return distance