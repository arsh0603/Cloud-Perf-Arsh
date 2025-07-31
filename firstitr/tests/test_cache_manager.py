"""
Tests for Cache Manager
Tests all functions in cache_manager.py
"""
import pytest
import json
import os
import tempfile
import threading
import time
from unittest.mock import Mock, patch, mock_open
from myapp.cache_manager import LRUCache


class TestLRUCache:
    """Test cases for LRUCache class"""
    
    def test_cache_initialization(self):
        """Test cache initialization"""
        # Setup with mock settings to avoid file operations
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=5)

        # Assert
        assert len(cache.cache) == 0
        assert cache.max_size == 5

    def test_cache_put_and_get(self):
        """Test basic cache put and get operations"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=5)

        # Execute
        cache.put('key1', 'value1')
        result = cache.get('key1')

        # Assert
        assert result == 'value1'
        assert cache.get('nonexistent') is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=2)

        # Execute
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        cache.put('key3', 'value3')  # Should evict key1

        # Assert
        assert cache.get('key1') is None  # Evicted
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'

    def test_cache_access_updates_order(self):
        """Test that accessing items updates their position in LRU order"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=2)

        # Execute
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        cache.get('key1')  # Access key1, making it more recent
        cache.put('key3', 'value3')  # Should evict key2, not key1

        # Assert
        assert cache.get('key1') == 'value1'  # Should still be there
        assert cache.get('key2') is None  # Should be evicted
        assert cache.get('key3') == 'value3'

    def test_cache_update_existing_key(self):
        """Test updating an existing key"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=3)

        # Execute
        cache.put('key1', 'value1')
        cache.put('key1', 'updated_value')

        # Assert
        assert cache.get('key1') == 'updated_value'
        assert len(cache.cache) == 1

    def test_cache_clear(self):
        """Test cache clearing"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=3)

        cache.put('key1', 'value1')
        cache.put('key2', 'value2')

        # Execute
        cache.clear()

        # Assert
        assert len(cache.cache) == 0
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_get_status(self):
        """Test getting cache status"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=5)

        cache.put('key1', 'value1')
        cache.put('graph_123', 'graph_value')

        # Execute
        status = cache.get_status()

        # Assert
        assert status['size'] == 2
        assert status['max_size'] == 5
        assert 'key1' in status['details_keys']
        assert '123' in status['graph_keys']
        assert 'access_order' in status
        assert 'access_times' in status

    def test_cache_thread_safety(self):
        """Test cache thread safety"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=10)

        results = []

        def worker(worker_id):
            for i in range(10):
                cache.put(f'key_{worker_id}_{i}', f'value_{worker_id}_{i}')
                results.append(cache.get(f'key_{worker_id}_{i}'))

        # Execute
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Assert
        assert len(results) == 30  # 3 workers * 10 operations each
        # Check that all results are valid
        assert all(result is not None for result in results)

    def test_cache_load_from_file_success(self):
        """Test successful loading from cache file"""
        # Setup mock data
        cache_data = {
            'cache': {'key1': 'value1', 'key2': 'value2'},
            'access_times': {'key1': 1234567890, 'key2': 1234567891}
        }

        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=json.dumps(cache_data))):
                    cache = LRUCache(max_size=5)

        # Assert
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'

    def test_cache_load_from_file_oversized(self):
        """Test loading from cache file when cache exceeds max size"""
        # Setup oversized cache data
        cache_data = {
            'cache': {f'key{i}': f'value{i}' for i in range(10)},
            'access_times': {f'key{i}': 1234567890 + i for i in range(10)}
        }

        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=json.dumps(cache_data))):
                    cache = LRUCache(max_size=5)

        # Assert - should only have 5 most recent items
        assert len(cache.cache) <= 5

    def test_cache_load_from_file_corrupted(self):
        """Test loading from corrupted cache file"""
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='invalid json')):
                    cache = LRUCache(max_size=5)

        # Assert - should initialize empty cache
        assert len(cache.cache) == 0

    def test_cache_save_to_file(self):
        """Test saving cache to file"""
        # Setup
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = os.path.join(temp_dir, 'test_cache.json')

            with patch('myapp.cache_manager.settings.BASE_DIR', temp_dir):
                with patch('myapp.cache_manager.os.path.join', return_value=cache_file):
                    cache = LRUCache(max_size=5)

                    cache.put('key1', 'value1')
                    cache.put('key2', 'value2')

                    # File should be saved automatically
                    assert os.path.exists(cache_file)

                    # Load and verify contents
                    with open(cache_file, 'r') as f:
                        saved_data = json.load(f)

                    assert 'cache' in saved_data
                    assert 'access_times' in saved_data
                    assert saved_data['cache']['key1'] == 'value1'
                    assert saved_data['cache']['key2'] == 'value2'

    def test_cache_save_to_file_error(self):
        """Test saving cache to file with write error"""
        # Setup
        with patch('myapp.cache_manager.settings.BASE_DIR', '/tmp'):
            with patch('os.path.exists', return_value=False):
                cache = LRUCache(max_size=5)
                cache.put('key1', 'value1')

            # Mock file write error
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                # Should not raise exception, just log error
                cache.put('key2', 'value2')

        # Assert - cache should still work despite save error
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'
