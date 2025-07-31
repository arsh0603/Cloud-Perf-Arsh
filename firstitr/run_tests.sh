#!/bin/bash

# Test runner script for Django backend
# This script sets up the environment and runs all pytest tests

echo "Setting up Django test environment..."

# Change to the Django project directory
cd /Users/ar36639/Downloads/Django/Firstprj-A/firstitr

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt

# Set up Django environment
export DJANGO_SETTINGS_MODULE=firstitr.settings

# Run migrations (if needed)
echo "Running Django migrations..."
python manage.py migrate --verbosity=0

# Run all tests with coverage
echo "Running all backend tests..."
pytest -v --cov=myapp --cov-report=html --cov-report=term-missing

# Display test results summary
echo ""
echo "Test Results Summary:"
echo "===================="
echo "Check the htmlcov/index.html file for detailed coverage report"
echo ""

# Run specific test categories
echo "Running specific test categories..."

echo "1. API Service Tests:"
pytest tests/test_api_service.py -v

echo "2. Run Service Tests:"
pytest tests/test_run_service.py -v

echo "3. Stats Service Tests:"
pytest tests/test_stats_service.py -v

echo "4. Views Tests:"
pytest tests/test_views.py -v

echo "5. Cache Manager Tests:"
pytest tests/test_cache_manager.py -v

echo ""
echo "All tests completed!"
