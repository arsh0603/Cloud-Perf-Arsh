"""
Unit tests for Django Views
Tests all view classes and their HTTP methods
"""
import json
from unittest.mock import Mock, patch
from django.test import TestCase, RequestFactory
from myapp.views import FetchDetailsView, CacheStatusView, CacheManagementView


class TestFetchDetailsView(TestCase):
    """Test cases for FetchDetailsView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FetchDetailsView()
    
    @patch('myapp.views.RunDataService.fetch_single_run_data')
    def test_get_single_run_success(self, mock_fetch_single):
        """Test successful single run fetch"""
        mock_data = {'Workload Type': 'test_workload', 'Peak Iteration': 1000}
        mock_fetch_single.return_value = mock_data
        
        request = self.factory.get('/fetch-details/', {'id': '123456789'})
        response = self.view.get(request)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch_single.assert_called_once_with('123456789')
    
    def test_get_missing_id_parameter(self):
        """Test request with missing id parameter"""
        request = self.factory.get('/fetch-details/')
        response = self.view.get(request)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('required', response_data['error'])
    
    @patch('myapp.views.RunDataService.fetch_single_run_data')
    def test_get_single_run_not_found(self, mock_fetch_single):
        """Test single run fetch when ID is not found"""
        mock_fetch_single.return_value = None
        
        request = self.factory.get('/fetch-details/', {'id': 'invalid123'})
        response = self.view.get(request)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('incorrect', response_data['error'])


class TestCacheStatusView(TestCase):
    """Test cases for CacheStatusView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CacheStatusView()
    
    @patch('myapp.views.api_cache.get_status')
    def test_get_cache_status_success(self, mock_get_status):
        """Test successful cache status fetch"""
        mock_status = {
            'size': 5,
            'max_size': 20,
            'details_keys': ['key1', 'key2']
        }
        mock_get_status.return_value = mock_status
        
        request = self.factory.get('/cache-status/')
        response = self.view.get(request)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_status)
        mock_get_status.assert_called_once()


class TestCacheManagementView(TestCase):
    """Test cases for CacheManagementView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CacheManagementView()
    
    @patch('myapp.views.api_cache.clear')
    def test_delete_clear_cache_success(self, mock_clear):
        """Test successful cache clearing"""
        request = self.factory.delete('/cache-management/')
        response = self.view.delete(request)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('status', response_data)
        self.assertIn('cleared successfully', response_data['status'])
        mock_clear.assert_called_once()
