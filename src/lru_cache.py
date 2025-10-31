"""
LRU (Least Recently Used) Cache Implementation

This module implements an efficient LRU cache using a hash map and doubly linked list
for O(1) get and set operations.

Author: [Your Name]
Date: 2024
"""

from typing import Any, Optional, Dict
from collections import OrderedDict


class DLLNode:
    """
    Doubly Linked List Node for LRU Cache.
    
    Attributes:
        key: The cache key
        value: The cached value
        prev: Reference to previous node
        next: Reference to next node
    """
    
    def __init__(self, key: Any = None, value: Any = None):
        self.key = key
        self.value = value
        self.prev: Optional['DLLNode'] = None
        self.next: Optional['DLLNode'] = None


class LRUCache:
    """
    LRU (Least Recently Used) Cache implementation.
    
    Uses a combination of:
    - Hash map for O(1) lookups
    - Doubly linked list for O(1) insertion/deletion
    
    The most recently used items are at the front (head),
    and least recently used items are at the back (tail).
    
    Time Complexity:
        - get: O(1)
        - set: O(1)
        - delete: O(1)
    
    Space Complexity: O(capacity)
    
    Example:
        >>> cache = LRUCache(capacity=3)
        >>> cache.set("key1", "value1")
        >>> cache.set("key2", "value2")
        >>> cache.get("key1")
        'value1'
        >>> cache.set("key3", "value3")
        >>> cache.set("key4", "value4")  # This evicts "key2" (LRU)
    """
    
    def __init__(self, capacity: int):
        """
        Initialize LRU Cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        
        Raises:
            ValueError: If capacity is less than 1
        """
        if capacity < 1:
            raise ValueError("Cache capacity must be at least 1")
        
        self.capacity = capacity
        self.cache: Dict[Any, DLLNode] = {}
        
        # Dummy head and tail nodes for easier list manipulation
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get value from cache and mark as recently used.
        
        Args:
            key: The key to look up
        
        Returns:
            The cached value if found, None otherwise
        
        Time Complexity: O(1)
        
        Example:
            >>> cache.get("existing_key")
            'cached_value'
            >>> cache.get("non_existent_key")
            None
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        self.hits += 1
        node = self.cache[key]
        
        # Move to front (most recently used)
        self._remove_node(node)
        self._add_to_front(node)
        
        return node.value
    
    def set(self, key: Any, value: Any) -> None:
        """
        Set a key-value pair in the cache.
        
        If key exists, update value and move to front.
        If cache is full, evict least recently used item.
        
        Args:
            key: The key to set
            value: The value to cache
        
        Time Complexity: O(1)
        
        Example:
            >>> cache.set("key", "value")
            >>> cache.set("key", "new_value")  # Updates existing key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            
            # Move to front
            self._remove_node(node)
            self._add_to_front(node)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Evict LRU item (from tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
                self.evictions += 1
            
            # Create and add new node
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def delete(self, key: Any) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: The key to delete
        
        Returns:
            True if key was found and deleted, False otherwise
        
        Time Complexity: O(1)
        
        Example:
            >>> cache.delete("existing_key")
            True
            >>> cache.delete("non_existent_key")
            False
        """
        if key not in self.cache:
            return False
        
        node = self.cache[key]
        self._remove_node(node)
        del self.cache[key]
        return True
    
    def clear(self) -> None:
        """
        Clear all items from the cache.
        
        Time Complexity: O(1)
        
        Example:
            >>> cache.clear()
            >>> len(cache)
            0
        """
        self.cache.clear()
        self.head.next = self.tail
        self.tail.prev = self.head
        
        # Keep statistics but could reset if desired
    
    def has(self, key: Any) -> bool:
        """
        Check if a key exists in the cache without updating LRU order.
        
        Args:
            key: The key to check
        
        Returns:
            True if key exists, False otherwise
        
        Time Complexity: O(1)
        """
        return key in self.cache
    
    def size(self) -> int:
        """
        Get current number of items in cache.
        
        Returns:
            Number of cached items
        """
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        
        Example:
            >>> stats = cache.get_stats()
            >>> print(stats['hit_rate'])
            0.75
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'capacity': self.capacity,
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': round(hit_rate, 2),
            'utilization': round((len(self.cache) / self.capacity * 100), 2)
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics counters."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _add_to_front(self, node: DLLNode) -> None:
        """
        Add node to front of list (most recently used position).
        
        Args:
            node: The node to add
        
        Time Complexity: O(1)
        """
        node.next = self.head.next
        node.prev = self.head
        
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: DLLNode) -> None:
        """
        Remove node from its current position in the list.
        
        Args:
            node: The node to remove
        
        Time Complexity: O(1)
        """
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def __len__(self) -> int:
        """Support len() function."""
        return len(self.cache)
    
    def __contains__(self, key: Any) -> bool:
        """Support 'in' operator."""
        return key in self.cache
    
    def __repr__(self) -> str:
        """String representation of the cache."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}: {current.value}")
            current = current.next
        return f"LRUCache(capacity={self.capacity}, items=[{', '.join(items)}])"


class SimpleLRUCache:
    """
    Simplified LRU Cache using OrderedDict.
    
    This is a simpler implementation using Python's OrderedDict,
    which maintains insertion order and allows moving items to the end.
    
    Time Complexity: O(1) for all operations
    
    Example:
        >>> cache = SimpleLRUCache(capacity=3)
        >>> cache.set("key1", "value1")
    """
    
    def __init__(self, capacity: int):
        """
        Initialize simple LRU Cache.
        
        Args:
            capacity: Maximum number of items
        """
        if capacity < 1:
            raise ValueError("Cache capacity must be at least 1")
        
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: Any) -> Optional[Any]:
        """Get value and move to end (most recent)."""
        if key not in self.cache:
            return None
        
        # Move to end
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: Any, value: Any) -> None:
        """Set key-value pair."""
        if key in self.cache:
            # Update and move to end
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all items."""
        self.cache.clear()
    
    def __len__(self) -> int:
        return len(self.cache)
    
    def __contains__(self, key: Any) -> bool:
        return key in self.cache