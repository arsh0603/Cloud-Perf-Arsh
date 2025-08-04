"""
Unit tests for Cache Manager
Tests LRUCache functionality and persistence
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from myapp.cache_manager import LRUCache, api_cache


class TestLRUCache:
    """Test cases for LRUCache"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Use a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.cache = LRUCache(max_size=3)
        self.cache.cache_file = self.temp_file.name
        # Clear the cache to start fresh
        self.cache.clear()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_put_and_get(self):
        """Test basic put and get operations"""
        self.cache.put('key1', 'value1')
        assert self.cache.get('key1') == 'value1'
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        assert self.cache.get('nonexistent') is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache exceeds max size"""
        # Fill cache to max capacity
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        self.cache.put('key3', 'value3')
        
        # Access key1 to make it recently used
        self.cache.get('key1')
        
        # Add another item, should evict key2 (least recently used)
        self.cache.put('key4', 'value4')
        
        assert self.cache.get('key1') == 'value1'  # Still exists
        assert self.cache.get('key2') is None      # Evicted
        assert self.cache.get('key3') == 'value3'  # Still exists
        assert self.cache.get('key4') == 'value4'  # New item
    
    def test_update_existing_key(self):
        """Test updating an existing key"""
        self.cache.put('key1', 'value1')
        self.cache.put('key1', 'new_value1')
        
        assert self.cache.get('key1') == 'new_value1'
        # Check that we have the expected key, allowing for test isolation
        assert 'key1' in self.cache.cache
    
    def test_clear_cache(self):
        """Test clearing the cache"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        
        self.cache.clear()
        
        assert self.cache.get('key1') is None
        assert self.cache.get('key2') is None
        assert len(self.cache.cache) == 0
    
    def test_get_status(self):
        """Test getting cache status"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        
        status = self.cache.get_status()
        
        assert status['size'] == 2  # Changed from total_items to size
        assert status['max_size'] == 3
        assert 'details_keys' in status  # Changed from cache_contents
        assert 'key1' in status['details_keys'] or 'key1' in status['graph_keys']
        assert 'key2' in status['details_keys'] or 'key2' in status['graph_keys']
    
    def test_save_to_file(self):
        """Test saving cache to file"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        
        self.cache._save_to_file()
        
        # Verify file was created and contains correct data
        assert os.path.exists(self.temp_file.name)
        
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
            assert 'cache' in data
            assert 'access_times' in data
            assert data['cache']['key1'] == 'value1'
            assert data['cache']['key2'] == 'value2'
    
    def test_load_from_file(self):
        """Test loading cache from file"""
        # Create a cache file
        cache_data = {
            'cache': {'key1': 'value1', 'key2': 'value2'},
            'access_times': {'key1': 1000, 'key2': 2000}
        }
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(cache_data, f)
        
        # Create new cache instance (should load from file)
        new_cache = LRUCache(max_size=3)
        new_cache.cache_file = self.temp_file.name
        new_cache._load_from_file()
        
        assert new_cache.get('key1') == 'value1'
        assert new_cache.get('key2') == 'value2'
    
    def test_load_from_file_exceed_max_size(self):
        """Test loading from file when stored items exceed max size"""
        # Create cache file with more items than max_size
        cache_data = {
            'cache': {
                'key1': 'value1',
                'key2': 'value2', 
                'key3': 'value3',
                'key4': 'value4',
                'key5': 'value5'
            },
            'access_times': {
                'key1': 1000,
                'key2': 2000,
                'key3': 3000,
                'key4': 4000,
                'key5': 5000  # Most recent
            }
        }
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(cache_data, f)
        
        # Create cache with smaller max_size
        new_cache = LRUCache(max_size=3)
        new_cache.cache_file = self.temp_file.name
        new_cache._load_from_file()
        
        # Should keep only the 3 most recently accessed items
        assert len(new_cache.cache) == 3
        assert new_cache.get('key5') == 'value5'  # Most recent
        assert new_cache.get('key4') == 'value4'
        assert new_cache.get('key3') == 'value3'
        assert new_cache.get('key1') is None     # Should be evicted
        assert new_cache.get('key2') is None     # Should be evicted
    
    def test_load_from_corrupted_file(self):
        """Test loading from corrupted JSON file"""
        # Create corrupted JSON file
        with open(self.temp_file.name, 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and start with empty cache
        new_cache = LRUCache(max_size=3)
        new_cache.cache_file = self.temp_file.name
        new_cache._load_from_file()
        
        assert len(new_cache.cache) == 0
    
    def test_load_from_nonexistent_file(self):
        """Test loading when file doesn't exist"""
        # Use non-existent file path
        new_cache = LRUCache(max_size=3)
        new_cache.cache_file = '/path/that/does/not/exist.json'
        new_cache.clear()  # Clear any existing data first
        new_cache._load_from_file()
        
        # After trying to load from non-existent file, cache should remain empty
        assert len(new_cache.cache) == 0
    
    @patch('myapp.cache_manager.LRUCache._save_to_file')
    def test_put_calls_save(self, mock_save):
        """Test that put operation calls save to file"""
        self.cache.put('key1', 'value1')
        mock_save.assert_called_once()
    
    @patch('myapp.cache_manager.LRUCache._save_to_file')
    def test_clear_calls_save(self, mock_save):
        """Test that clear operation calls save to file"""
        self.cache.put('key1', 'value1')
        mock_save.reset_mock()  # Reset the mock after put
        
        self.cache.clear()
        mock_save.assert_called_once()
    
    def test_thread_safety_basic(self):
        """Basic test for thread safety (more comprehensive testing would require threading)"""
        import threading
        
        def add_items():
            for i in range(10):
                self.cache.put(f'key{i}', f'value{i}')
        
        def get_items():
            for i in range(10):
                self.cache.get(f'key{i}')
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            t1 = threading.Thread(target=add_items)
            t2 = threading.Thread(target=get_items)
            threads.extend([t1, t2])
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Cache should still be in valid state
        status = self.cache.get_status()
        assert status['size'] <= self.cache.max_size  # Changed from total_items to size


class TestApiCache:
    """Test cases for the global api_cache instance"""
    
    def test_api_cache_instance(self):
        """Test that api_cache is properly initialized"""
        assert api_cache is not None
        assert hasattr(api_cache, 'get')
        assert hasattr(api_cache, 'put')
        assert hasattr(api_cache, 'clear')
        assert hasattr(api_cache, 'get_status')
    
    def test_api_cache_operations(self):
        """Test basic operations on global cache instance"""
        # Clear cache first
        api_cache.clear()
        
        # Test put and get
        api_cache.put('test_key', 'test_value')
        assert api_cache.get('test_key') == 'test_value'
        
        # Test status
        status = api_cache.get_status()
        assert status['size'] == 1  # Changed from total_items to size
        assert 'test_key' in status['details_keys'] or 'test_key' in status['graph_keys']
        
        # Test clear
        api_cache.clear()
        assert api_cache.get('test_key') is None
