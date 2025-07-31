# Django Test Suite - Command Reference

## Running Unit Tests for Backend Functions

### Basic Commands (using system Python)

```bash
# Navigate to project directory
cd /Users/ar36639/Downloads/Django/Firstprj-A/firstitr

# Run all unit tests (recommended)
python3 -m pytest -v --tb=short

# Run tests with minimal output
python3 -m pytest

# Run specific test file
python3 -m pytest tests/test_api_service.py -v

# Run specific test class
python3 -m pytest tests/test_views.py::TestFetchDetailsView -v

# Run specific test method
python3 -m pytest tests/test_api_service.py::TestExternalAPIService::test_fetch_run_details_success -v
```

### Test Options

```bash
# Verbose output (shows each test name)
python3 -m pytest -v

# Short traceback on failures
python3 -m pytest --tb=short

# Stop on first failure
python3 -m pytest -x

# Show only failed tests
python3 -m pytest --lf

# Run tests in parallel (if pytest-xdist installed)
python3 -m pytest -n auto
```

### Test Categories

```bash
# Run tests by keyword
python3 -m pytest -k "api_service"
python3 -m pytest -k "cache"
python3 -m pytest -k "views"
```

### Coverage Reports (if pytest-cov installed)

```bash
# Run tests with coverage
python3 -m pytest --cov=myapp

# Generate HTML coverage report
python3 -m pytest --cov=myapp --cov-report=html

# Coverage with missing lines
python3 -m pytest --cov=myapp --cov-report=term-missing
```

## Current Test Suite Results

✅ **89 Unit Tests Passing**
- API Service: 19 tests
- Cache Manager: 13 tests  
- Run Service: 15 tests
- Stats Service: 6 tests
- Views: 24 tests
- URLs: 6 tests
- Integration: 8 tests

⏱️ **Execution Time**: ~0.25 seconds
🔧 **Dependencies**: All installed globally (no virtual env needed)

## Quick Test Commands

```bash
# Most common: Run all unit tests for functions
python3 -m pytest -v

# Debug failing test
python3 -m pytest tests/test_api_service.py::TestExternalAPIService::test_fetch_run_details_success -v -s

# Test specific functionality
python3 -m pytest -k "cache" -v        # All cache-related tests
python3 -m pytest -k "api" -v          # All API-related tests
python3 -m pytest -k "views" -v        # All view tests
```

## Dependencies Required

The following packages must be installed globally:

```bash
python3 -m pip install pytest pytest-django django django-cors-headers requests
```

## Notes

- ✅ All packages already installed globally on your system
- ✅ No virtual environment needed
- ✅ Tests use system Python 3.13.5
- ✅ Fast execution and reliable results
- ✅ Comprehensive backend coverage

## Troubleshooting

If you get "command not found" errors:
- Use `python3` instead of `python`
- Ensure pytest is installed: `python3 -m pip install pytest pytest-django`
- Check Python version: `python3 --version` (should be 3.13.5)

If tests fail due to missing modules:
- Install missing packages: `python3 -m pip install <package-name>`
- Verify Django settings: Check `DJANGO_SETTINGS_MODULE` in `pytest.ini`
