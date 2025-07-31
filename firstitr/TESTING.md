# Backend Testing Documentation

## Overview
This document describes the comprehensive test suite for the Django backend performance analysis application. The tests are written using pytest and cover all major components and functions.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_api_service.py         # Tests for API service functions
├── test_run_service.py         # Tests for run data service functions
├── test_stats_service.py       # Tests for statistics service functions
├── test_views.py               # Tests for Django views
└── test_cache_manager.py       # Tests for cache manager functions
```

## Test Configuration

### pytest.ini
- Configures pytest settings
- Sets coverage reporting
- Defines test discovery patterns
- Sets minimum coverage threshold (80%)

### requirements-test.txt
- pytest>=7.0.0
- pytest-django>=4.5.0
- pytest-mock>=3.10.0
- pytest-cov>=4.0.0
- requests-mock>=1.10.0
- factory-boy>=3.2.0
- freezegun>=1.2.0

## Test Categories

### 1. API Service Tests (`test_api_service.py`)

#### ExternalAPIService Tests
- **fetch_run_details_success**: Tests successful API data fetching
- **fetch_run_details_invalid_id**: Tests handling of invalid run IDs (workload = 0)
- **fetch_run_details_network_error**: Tests network error handling
- **fetch_run_details_timeout**: Tests timeout handling
- **fetch_run_details_custom_fields**: Tests custom field parameters
- **fetch_perfweb_links_success**: Tests perfweb link extraction
- **fetch_perfweb_links_no_links**: Tests handling when no links found

#### DataTransformService Tests
- **transform_run_data_complete**: Tests complete data transformation
- **transform_run_data_missing_fields**: Tests handling of missing fields
- **transform_run_data_empty_data**: Tests empty data handling
- **extract_numeric_value_integer**: Tests integer extraction from text
- **extract_numeric_value_float**: Tests float extraction from text
- **extract_numeric_value_not_found**: Tests pattern not found scenarios
- **extract_numeric_value_invalid_format**: Tests invalid format handling

#### CompatibilityService Tests
- **check_workload_compatibility_same_workload_model**: Tests compatible runs
- **check_workload_compatibility_different_workload**: Tests incompatible workloads
- **check_workload_compatibility_different_model**: Tests incompatible models
- **check_workload_compatibility_missing_workload**: Tests missing workload data
- **check_workload_compatibility_missing_model**: Tests missing model data

### 2. Run Service Tests (`test_run_service.py`)

#### RunDataService Tests
- **fetch_single_run_data_from_cache**: Tests cache hit scenarios
- **fetch_single_run_data_from_api**: Tests API data fetching
- **fetch_single_run_data_invalid_id**: Tests invalid ID handling
- **fetch_single_run_data_stats_error**: Tests stats fetching error handling
- **fetch_single_run_data_without_stats**: Tests fetching without statistics
- **fetch_comparison_data_compatible**: Tests compatible run comparison
- **fetch_comparison_data_incompatible**: Tests incompatible run comparison
- **fetch_comparison_data_missing_run**: Tests missing run scenarios
- **fetch_multiple_runs_data_success**: Tests multiple runs fetching
- **fetch_multiple_runs_data_with_invalid**: Tests mixed valid/invalid IDs
- **fetch_multiple_runs_data_empty_list**: Tests empty input handling
- **fetch_multiple_runs_data_exception_handling**: Tests exception handling

### 3. Statistics Service Tests (`test_stats_service.py`)

#### StatsProcessingService Tests
- **fetch_comprehensive_stats_success**: Tests successful stats fetching
- **fetch_comprehensive_stats_no_links**: Tests no perfweb links scenario
- **extract_throughput_success**: Tests throughput extraction
- **extract_throughput_not_found**: Tests missing throughput data
- **extract_cache_percentages_success**: Tests cache percentage extraction
- **extract_cache_percentages_partial**: Tests partial cache data
- **extract_cpu_busy_success**: Tests CPU busy extraction
- **extract_cpu_busy_not_found**: Tests missing CPU data
- **extract_latency_metrics_success**: Tests latency metrics extraction
- **extract_latency_metrics_not_found**: Tests missing latency data
- **extract_instance_type_success**: Tests instance type extraction
- **extract_instance_type_not_found**: Tests missing instance type
- **bytes_to_mb_conversion**: Tests byte to MB conversion
- **format_percentage**: Tests percentage formatting
- **format_latency_microseconds**: Tests latency formatting

#### GraphDataService Tests
- **fetch_single_graph_data_from_cache**: Tests graph data cache hits
- **fetch_single_graph_data_from_api**: Tests graph data API fetching
- **fetch_single_graph_data_no_links**: Tests no perfweb links scenario
- **fetch_comparison_graph_data_success**: Tests comparison graph fetching
- **fetch_comparison_graph_data_missing_data**: Tests missing graph data
- **parse_iteration_data_success**: Tests iteration data parsing
- **parse_iteration_data_no_data**: Tests no iteration data scenario
- **merge_graph_datasets_success**: Tests graph dataset merging
- **merge_graph_datasets_empty**: Tests empty dataset merging
- **normalize_data_points**: Tests data point normalization
- **calculate_throughput_from_ops**: Tests throughput calculation

### 4. Views Tests (`test_views.py`)

#### FetchDetailsView Tests
- **get_single_run_success**: Tests successful single run fetching
- **get_comparison_run_success**: Tests successful comparison fetching
- **get_missing_id_parameter**: Tests missing ID parameter handling
- **get_invalid_run_id**: Tests invalid run ID handling
- **get_service_exception**: Tests service exception handling
- **get_alternative_id_parameter**: Tests alternative ID parameter

#### FetchGraphDataView Tests
- **get_single_graph_success**: Tests successful graph data fetching
- **get_comparison_graph_success**: Tests successful comparison graph fetching
- **get_missing_run_id1**: Tests missing run_id1 parameter
- **get_no_graph_data_found**: Tests no graph data scenario
- **get_service_exception**: Tests service exception handling

#### CacheStatusView Tests
- **get_cache_status**: Tests cache status retrieval

#### CacheManagementView Tests
- **delete_clear_cache**: Tests cache clearing functionality

#### FetchMultipleRunsView Tests
- **get_multiple_runs_success**: Tests successful multiple runs fetching
- **get_missing_run_ids**: Tests missing run_ids parameter
- **get_too_many_run_ids**: Tests exceeding maximum run IDs limit
- **get_whitespace_handling**: Tests whitespace handling in run IDs
- **get_service_exception**: Tests service exception handling

### 5. Cache Manager Tests (`test_cache_manager.py`)

#### LRUCache Tests
- **cache_initialization**: Tests cache initialization
- **cache_set_and_get**: Tests basic cache operations
- **cache_lru_eviction**: Tests LRU eviction when cache is full
- **cache_access_updates_order**: Tests LRU order updates on access
- **cache_update_existing_key**: Tests updating existing keys
- **cache_clear**: Tests cache clearing
- **cache_get_status**: Tests cache status retrieval
- **cache_get_size_mb**: Tests cache size calculation
- **cache_thread_safety**: Tests thread safety
- **cache_load_from_file_success**: Tests successful file loading
- **cache_load_from_file_oversized**: Tests loading oversized cache
- **cache_load_from_file_corrupted**: Tests corrupted file handling
- **cache_save_to_file**: Tests cache saving to file
- **cache_save_to_file_error**: Tests file save error handling
- **cache_contains_method**: Tests __contains__ method
- **cache_len_method**: Tests __len__ method
- **cache_keys_method**: Tests keys method

## Test Fixtures

### Global Fixtures (conftest.py)
- **sample_run_data**: Basic run data for testing
- **sample_transformed_data**: Transformed run data
- **sample_stats_data**: Statistics data
- **sample_graph_data**: Graph data with data points
- **mock_requests_get**: Mock for HTTP requests
- **mock_cache**: Mock cache for testing
- **temp_cache_file**: Temporary cache file
- **sample_perfweb_content**: Sample perfweb content for parsing
- **sample_invalid_run_data**: Invalid run data (workload = 0)
- **comparison_run_data**: Data for comparison testing
- **incompatible_run_data**: Data for incompatible runs

## Running Tests

### Install Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=myapp --cov-report=html --cov-report=term-missing
```

### Run Specific Test Files
```bash
pytest tests/test_api_service.py -v
pytest tests/test_run_service.py -v
pytest tests/test_stats_service.py -v
pytest tests/test_views.py -v
pytest tests/test_cache_manager.py -v
```

### Run Specific Test Functions
```bash
pytest tests/test_api_service.py::TestExternalAPIService::test_fetch_run_details_success -v
```

### Using the Test Runner Script
```bash
./run_tests.sh
```

## Coverage Requirements

- Minimum coverage threshold: 80%
- Generates HTML coverage report in `htmlcov/` directory
- Displays coverage report in terminal

## Mocking Strategy

### External Dependencies
- **requests.get**: Mocked for API calls
- **api_cache**: Mocked for cache operations
- **settings.BASE_DIR**: Mocked for file path operations
- **os.path.exists**: Mocked for file existence checks

### Service Dependencies
- **ExternalAPIService**: Mocked in higher-level tests
- **DataTransformService**: Mocked in integration tests
- **StatsProcessingService**: Mocked in run service tests
- **GraphDataService**: Mocked in view tests

## Test Data

### Sample Run Data
```python
{
    'workload': 'test_workload',
    'peak_iter': 100,
    'ontap_ver': '9.14.1',
    'peak_ops': 50000,
    'peak_lat': 1.5,
    'model': 'A800'
}
```

### Sample Graph Data
```python
{
    'data_points': [
        {'iteration': 1, 'ops': 1000, 'latency': 1.2, 'throughput': 80},
        {'iteration': 2, 'ops': 2000, 'latency': 1.3, 'throughput': 85},
        {'iteration': 3, 'ops': 3000, 'latency': 1.4, 'throughput': 90}
    ]
}
```

## Best Practices

### Test Organization
- One test class per service/component
- Descriptive test method names
- Setup and teardown in fixtures
- Use of meaningful assertions

### Mocking
- Mock external dependencies
- Use patch decorators for isolation
- Mock at the right level (unit vs integration)
- Verify mock calls when relevant

### Assertions
- Test both success and failure cases
- Verify data structure and content
- Check error handling and edge cases
- Validate side effects (cache updates, etc.)

### Maintainability
- Use fixtures for common test data
- Keep tests independent
- Regular updates as code changes
- Clear documentation and comments

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure DJANGO_SETTINGS_MODULE is set
2. **Database Issues**: Run migrations before tests
3. **File Permission Errors**: Use temporary files in tests
4. **Mock Issues**: Ensure correct patch targets

### Debug Tips
1. Use `-v` flag for verbose output
2. Use `--pdb` for debugging on failure
3. Run single tests for isolation
4. Check mock call counts and arguments

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Backend Tests
  run: |
    cd firstitr
    pip install -r requirements-test.txt
    python manage.py migrate
    pytest --cov=myapp --cov-report=xml
```

### Coverage Reporting
- HTML reports for local development
- XML reports for CI/CD integration
- Terminal output for quick feedback

This comprehensive test suite ensures high code quality, catches regressions early, and provides confidence in the application's reliability.
