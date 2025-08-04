"""
Test configuration and fixtures for the myapp tests
Provides shared fixtures and configuration for all tests
"""
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_cache():
    """Mock cache for testing"""
    with patch('myapp.cache_manager.api_cache') as mock_cache_instance:
        mock_cache_instance.get.return_value = None
        mock_cache_instance.put.return_value = None
        mock_cache_instance.clear.return_value = None
        mock_cache_instance.get_status.return_value = {
            'size': 0,
            'max_size': 20,
            'details_keys': [],
            'graph_keys': []
        }
        yield mock_cache_instance

# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    import django
    from django.conf import settings
    
    if not settings.configured:
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstitr.settings')
        django.setup()
