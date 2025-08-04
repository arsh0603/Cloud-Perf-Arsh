"""
Test configuration and fixtures for the myapp tests
Provides shared fixtures and configuration for all tests
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.test.client import RequestFactory


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch('requests.get') as mock_get:
        yield mock_get


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


@pytest.fixture
def sample_run_data():
    """Sample run data for testing"""
    return {
        'workload': 'test_workload',
        'peak_iter': 1000,
        'ontap_ver': '9.14.1',
        'peak_ops': 50000,
        'peak_lat': 2.5,
        'model': 'FAS8300'
    }


@pytest.fixture
def sample_transformed_data():
    """Sample transformed run data matching actual service output"""
    return {
        'Workload Type': 'test_workload',
        'Peak Iteration': 1000,
        'ONTAP version': '9.14.1',
        'Achieved Ops': 50000,
        'Peak Latency': 2.5,
        'Model': 'FAS8300'
    }


@pytest.fixture
def sample_graph_data():
    """Sample graph data for testing"""
    return {
        'data_points': {
            '123456789': {
                'timestamps': [1000, 2000, 3000],
                'throughput': [50000, 55000, 48000],
                'latency': [2.5, 2.3, 2.8],
                'cpu_usage': [75, 78, 72]
            }
        }
    }


@pytest.fixture
def sample_stats_data():
    """Sample stats data for testing"""
    return {
        'workload_stats': {
            'operation': 'read',
            'throughput': '50,000 ops/sec',
            'latency': '2.5 ms',
            'iops': 50000
        },
        'system_stats': {
            'cpu_usage': '75%',
            'memory_usage': '60%',
            'disk_usage': '45%',
            'network_io': '1000 MB/s'
        }
    }


@pytest.fixture
def request_factory():
    """Django request factory for view testing"""
    return RequestFactory()


@pytest.fixture
def temp_cache_file():
    """Create a temporary cache file for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        self.factory = RequestFactory()
        # Any common setup can go here


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    import django
    from django.conf import settings
    
    if not settings.configured:
        # This shouldn't be needed with DJANGO_SETTINGS_MODULE but just in case
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstitr.settings')
        django.setup()
