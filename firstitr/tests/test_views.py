"""
Tests for Views
Tests all view functions in views.py
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from myapp.views import (
    FetchDetailsView, 
    FetchGraphDataView, 
    CacheStatusView,
    CacheManagementView,
    FetchMultipleRunsView
)


class TestFetchDetailsView(TestCase):
    """Test cases for FetchDetailsView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FetchDetailsView()
    
    @patch('myapp.views.RunDataService.fetch_single_run_data')
    def test_get_single_run_success(self, mock_fetch):
        """Test successful single run details fetching"""
        # Setup
        mock_data = {'Workload Type': 'test_workload', 'Model': 'A800'}
        mock_fetch.return_value = mock_data
        
        request = self.factory.get('/fetch-details/', {'id1': '123456789'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch.assert_called_once_with('123456789')
    
    @patch('myapp.views.RunDataService.fetch_comparison_data')
    def test_get_comparison_run_success(self, mock_fetch):
        """Test successful comparison run details fetching"""
        # Setup
        mock_data = [
            {'Workload Type': 'test_workload', 'Model': 'A800'},
            {'Workload Type': 'test_workload', 'Model': 'A800'}
        ]
        mock_fetch.return_value = mock_data
        
        request = self.factory.get('/fetch-details/', {'id1': '123456789', 'id2': '987654321'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch.assert_called_once_with('123456789', '987654321')
    
    def test_get_missing_id_parameter(self):
        """Test missing id parameter"""
        # Setup
        request = self.factory.get('/fetch-details/')
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('required', response_data['error'])
    
    @patch('myapp.views.RunDataService.fetch_single_run_data')
    def test_get_invalid_run_id(self, mock_fetch):
        """Test invalid run ID"""
        # Setup
        mock_fetch.return_value = None
        
        request = self.factory.get('/fetch-details/', {'id1': '000000000'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('incorrect', response_data['error'])
    
    @patch('myapp.views.RunDataService.fetch_single_run_data')
    def test_get_service_exception(self, mock_fetch):
        """Test service exception handling"""
        # Setup
        mock_fetch.side_effect = Exception("Service error")
        
        request = self.factory.get('/fetch-details/', {'id1': '123456789'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Service error', response_data['error'])
    
    def test_get_alternative_id_parameter(self):
        """Test using 'id' parameter instead of 'id1'"""
        # Setup
        with patch('myapp.views.RunDataService.fetch_single_run_data') as mock_fetch:
            mock_fetch.return_value = {'Workload Type': 'test'}
            
            request = self.factory.get('/fetch-details/', {'id': '123456789'})
            
            # Execute
            response = self.view.get(request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            mock_fetch.assert_called_once_with('123456789')


class TestFetchGraphDataView(TestCase):
    """Test cases for FetchGraphDataView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FetchGraphDataView()
    
    @patch('myapp.views.GraphDataManagerService.fetch_single_graph_data')
    def test_get_single_graph_success(self, mock_fetch):
        """Test successful single graph data fetching"""
        # Setup
        mock_data = {'data_points': [{'iteration': 1, 'ops': 1000}]}
        mock_fetch.return_value = mock_data
        
        request = self.factory.get('/fetch-graph-data/', {'run_id1': '123456789'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch.assert_called_once_with('123456789')
    
    @patch('myapp.views.GraphDataManagerService.fetch_comparison_graph_data')
    def test_get_comparison_graph_success(self, mock_fetch):
        """Test successful comparison graph data fetching"""
        # Setup
        mock_data = {'data_points': [{'iteration': 1, 'ops1': 1000, 'ops2': 2000}]}
        mock_fetch.return_value = mock_data
        
        request = self.factory.get('/fetch-graph-data/', {
            'run_id1': '123456789', 
            'run_id2': '987654321'
        })
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch.assert_called_once_with('123456789', '987654321')
    
    def test_get_missing_run_id1(self):
        """Test missing run_id1 parameter"""
        # Setup
        request = self.factory.get('/fetch-graph-data/')
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('run_id1 is required', response_data['error'])
    
    @patch('myapp.views.GraphDataManagerService.fetch_single_graph_data')
    def test_get_no_graph_data_found(self, mock_fetch):
        """Test when no graph data is found"""
        # Setup
        mock_fetch.return_value = None
        
        request = self.factory.get('/fetch-graph-data/', {'run_id1': '123456789'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('No graph data found', response_data['error'])
    
    @patch('myapp.views.GraphDataManagerService.fetch_single_graph_data')
    def test_get_service_exception(self, mock_fetch):
        """Test service exception handling"""
        # Setup
        mock_fetch.side_effect = Exception("Graph service error")
        
        request = self.factory.get('/fetch-graph-data/', {'run_id1': '123456789'})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Graph service error', response_data['error'])


class TestCacheStatusView(TestCase):
    """Test cases for CacheStatusView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CacheStatusView()
    
    @patch('myapp.views.api_cache')
    def test_get_cache_status(self, mock_cache):
        """Test getting cache status"""
        # Setup
        mock_status = {
            'total_items': 5,
            'total_size_mb': 2.5,
            'max_size': 20
        }
        mock_cache.get_status.return_value = mock_status
        
        request = self.factory.get('/cache-status/')
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_status)
        mock_cache.get_status.assert_called_once()


class TestCacheManagementView(TestCase):
    """Test cases for CacheManagementView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CacheManagementView()
    
    @patch('myapp.views.api_cache')
    def test_delete_clear_cache(self, mock_cache):
        """Test clearing cache"""
        # Setup
        request = self.factory.delete('/cache-management/')
        
        # Execute
        response = self.view.delete(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'Cache cleared successfully')
        mock_cache.clear.assert_called_once()


class TestFetchMultipleRunsView(TestCase):
    """Test cases for FetchMultipleRunsView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FetchMultipleRunsView()
    
    @patch('myapp.views.RunDataService.fetch_multiple_runs_data')
    def test_get_multiple_runs_success(self, mock_fetch):
        """Test successful multiple runs fetching"""
        # Setup
        mock_data = [
            {'id': '123456789', 'Workload Type': 'test1'},
            {'id': '987654321', 'Workload Type': 'test2'}
        ]
        mock_fetch.return_value = mock_data
        
        request = self.factory.get('/fetch-multiple-runs/', {
            'run_ids': '123456789,987654321'
        })
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, mock_data)
        mock_fetch.assert_called_once_with(['123456789', '987654321'])
    
    def test_get_missing_run_ids(self):
        """Test missing run_ids parameter"""
        # Setup
        request = self.factory.get('/fetch-multiple-runs/')
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('run_ids parameter is required', response_data['error'])
    
    def test_get_too_many_run_ids(self):
        """Test too many run IDs (> 50)"""
        # Setup
        run_ids = ','.join([f'{i:09d}' for i in range(51)])  # 51 IDs
        request = self.factory.get('/fetch-multiple-runs/', {'run_ids': run_ids})
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Maximum 50 run IDs allowed', response_data['error'])
    
    def test_get_whitespace_handling(self):
        """Test whitespace handling in run IDs"""
        # Setup
        with patch('myapp.views.RunDataService.fetch_multiple_runs_data') as mock_fetch:
            mock_fetch.return_value = []
            
            request = self.factory.get('/fetch-multiple-runs/', {
                'run_ids': ' 123456789 , 987654321 , '
            })
            
            # Execute
            response = self.view.get(request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            mock_fetch.assert_called_once_with(['123456789', '987654321'])
    
    @patch('myapp.views.RunDataService.fetch_multiple_runs_data')
    def test_get_service_exception(self, mock_fetch):
        """Test service exception handling"""
        # Setup
        mock_fetch.side_effect = Exception("Multiple runs service error")
        
        request = self.factory.get('/fetch-multiple-runs/', {
            'run_ids': '123456789,987654321'
        })
        
        # Execute
        response = self.view.get(request)
        
        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Multiple runs service error', response_data['error'])
