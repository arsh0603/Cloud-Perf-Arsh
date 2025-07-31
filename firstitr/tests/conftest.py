"""
Test configuration and fixtures for all tests
"""
import pytest
import json
import os
import django
from unittest.mock import Mock, patch
from django.test import TestCase
from django.conf import settings

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstitr.settings')
django.setup()


@pytest.fixture
def sample_run_data():
    """Sample run data for testing"""
    return {
        'workload': 'test_workload',
        'peak_iter': 100,
        'ontap_ver': '9.14.1',
        'peak_ops': 50000,
        'peak_lat': 1.5,
        'model': 'A800'
    }


@pytest.fixture
def sample_transformed_data():
    """Sample transformed data for testing"""
    return {
        'Workload Type': 'test_workload',
        'Peak Iteration': 100,
        'ONTAP Version': '9.14.1',
        'Peak Operations': '50,000',
        'Peak Latency (ms)': '1.50',
        'Model': 'A800'
    }


@pytest.fixture
def sample_stats_data():
    """Sample statistics data for testing"""
    return {
        'Throughput (MB/s)': '95.37',
        'CPU Busy (%)': '45.2',
        'Cache Read (%)': '78',
        'Disk Read (%)': '22',
        'Instance Type': 'Test Instance'
    }


@pytest.fixture
def sample_graph_data():
    """Sample graph data for testing"""
    return {
        'data_points': [
            {'iteration': 1, 'ops': 1000, 'latency': 1.2, 'throughput': 80},
            {'iteration': 2, 'ops': 2000, 'latency': 1.3, 'throughput': 85},
            {'iteration': 3, 'ops': 3000, 'latency': 1.4, 'throughput': 90}
        ]
    }


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_cache():
    """Mock cache for testing"""
    with patch('myapp.cache_manager.api_cache') as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None
        mock_cache.clear.return_value = None
        mock_cache.get_status.return_value = {
            'total_items': 0,
            'total_size_mb': 0,
            'max_size': 20
        }
        yield mock_cache


@pytest.fixture
def temp_cache_file(tmp_path):
    """Create a temporary cache file for testing"""
    cache_file = tmp_path / "test_cache.json"
    cache_data = {
        'cache': {},
        'access_times': {}
    }
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)
    return str(cache_file)


@pytest.fixture
def sample_perfweb_content():
    """Sample perfweb content for parsing"""
    return """
    write_data:100000000b/s
    read_io_type.cache:78%
    read_io_type.disk:22%
    cpu_busy:45.2%
    rdma_actual_latency.WAFL_SPINNP_WRITE:150.5us
    Instance Type: Test Instance Type
    """


@pytest.fixture
def sample_invalid_run_data():
    """Sample invalid run data (workload = 0)"""
    return {
        'workload': 0,
        'peak_iter': 0,
        'ontap_ver': '',
        'peak_ops': 0,
        'peak_lat': 0,
        'model': ''
    }


@pytest.fixture
def comparison_run_data():
    """Sample data for comparison testing"""
    return {
        'run1': {
            'workload': 'test_workload',
            'model': 'A800',
            'peak_ops': 50000,
            'peak_lat': 1.5
        },
        'run2': {
            'workload': 'test_workload',
            'model': 'A800',
            'peak_ops': 45000,
            'peak_lat': 1.7
        }
    }


@pytest.fixture
def incompatible_run_data():
    """Sample data for incompatible runs"""
    return {
        'run1': {
            'workload': 'workload_type_1',
            'model': 'A800',
            'peak_ops': 50000
        },
        'run2': {
            'workload': 'workload_type_2',
            'model': 'A900',
            'peak_ops': 45000
        }
    }
