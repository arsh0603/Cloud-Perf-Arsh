from collections import OrderedDict
import time
import threading
import json
import os
from typing import Any, Optional, Dict
from django.conf import settings

class LRUCache:
    """
    Thread-safe LRU Cache implementation with JSON file persistence
    """
    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.access_times = {}
        self.lock = threading.RLock()
        self.cache_file = os.path.join(settings.BASE_DIR, 'cache_data.json')
        self._load_from_file()
    
    def _load_from_file(self):
        """Load cache data from JSON file if it exists"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    
                # Load cache items
                cache_items = data.get('cache', {})
                access_times = data.get('access_times', {})
                
                # If there are more than max_size items, keep only the most recent ones
                if len(cache_items) > self.max_size:
                    # Sort by access time and keep the most recent max_size items
                    sorted_items = sorted(cache_items.items(), 
                                        key=lambda x: access_times.get(x[0], 0), 
                                        reverse=True)
                    cache_items = dict(sorted_items[:self.max_size])
                    # Update access_times to match
                    access_times = {k: v for k, v in access_times.items() if k in cache_items}
                
                self.cache = OrderedDict(cache_items)
                self.access_times = access_times
                print(f"Loaded {len(self.cache)} items from cache file")
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"Error loading cache file: {e}")
                self.cache = OrderedDict()
                self.access_times = {}
    
    def _save_to_file(self):
        """Save cache data to JSON file"""
        try:
            data = {
                'cache': dict(self.cache),
                'access_times': self.access_times
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache file: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache and mark as recently used"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.access_times[key] = time.time()
                self._save_to_file()  # Save after access
                print(f"Cache HIT for key: {key}")
                return value
            print(f"Cache MISS for key: {key}")
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache, evicting LRU if necessary"""
        with self.lock:
            if key in self.cache:
                # Update existing item
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used item
                lru_key = next(iter(self.cache))
                self.cache.pop(lru_key)
                self.access_times.pop(lru_key, None)
                print(f"Cache EVICTED LRU key: {lru_key}")
            
            self.cache[key] = value
            self.access_times[key] = time.time()
            self._save_to_file()  # Save after each put
            print(f"Cache STORED key: {key}, Cache size: {len(self.cache)}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self._save_to_file()  # Save after clearing
            print("Cache cleared")
    
    def get_status(self) -> Dict:
        """Get cache status information"""
        with self.lock:
            details_keys = [k for k in self.cache.keys() if not k.startswith('graph_')]
            graph_keys = [k.replace('graph_', '') for k in self.cache.keys() if k.startswith('graph_')]
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'details_keys': details_keys,
                'graph_keys': graph_keys,
                'access_order': list(self.cache.keys()),
                'access_times': dict(self.access_times)
            }

# Global cache instance
api_cache = LRUCache(max_size=20)
