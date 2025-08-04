"""
Unit tests for Run Service
Tests RunDataService and GraphDataManagerService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from myapp.services.run_service import RunDataService, GraphDataManagerService


class TestRunDataService:
    """Test cases for RunDataService"""
    
    @patch('myapp.services.run_service.StatsProcessingService.fetch_comprehensive_stats')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_success(self, mock_cache, mock_fetch_details, mock_transform, mock_stats):
        """Test successful single run data fetch"""
        # Setup mocks
        raw_data = {'workload': 'test', 'peak_iter': 1000}
        transformed_data = {'Workload Type': 'test', 'Peak Iteration': 1000}
        stats_data = {'workload_stats': {'operation': 'read'}}
        
        mock_cache.get.return_value = None  # Not in cache
        mock_fetch_details.return_value = raw_data
        mock_transform.return_value = transformed_data
        mock_stats.return_value = stats_data
        
        # Test the method
        result = RunDataService.fetch_single_run_data('123456789')
        
        # Assertions
        expected_result = {**transformed_data, **stats_data}
        assert result == expected_result
        mock_fetch_details.assert_called_once_with('123456789')
        mock_transform.assert_called_once_with(raw_data)
        mock_stats.assert_called_once_with('123456789')
        mock_cache.put.assert_called_once()
    
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_from_cache(self, mock_cache):
        """Test fetching data from cache"""
        cached_data = {'Workload Type': 'cached_test', 'from_cache': True}
        mock_cache.get.return_value = cached_data
        
        result = RunDataService.fetch_single_run_data('123456789')
        
        assert result == cached_data
        mock_cache.get.assert_called_once_with('details_123456789')
        mock_cache.put.assert_not_called()
    
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_not_found(self, mock_cache, mock_fetch_details):
        """Test handling when run ID is not found"""
        mock_cache.get.return_value = None
        mock_fetch_details.return_value = None
        
        result = RunDataService.fetch_single_run_data('invalid123')
        
        assert result is None
        mock_fetch_details.assert_called_once_with('invalid123')
    
    @patch('myapp.services.run_service.StatsProcessingService.fetch_comprehensive_stats')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_without_stats(self, mock_cache, mock_fetch_details, mock_transform, mock_stats):
        """Test fetching run data without detailed statistics"""
        raw_data = {'workload': 'test', 'peak_iter': 1000}
        transformed_data = {'Workload Type': 'test', 'Peak Iteration': 1000}
        
        mock_cache.get.return_value = None
        mock_fetch_details.return_value = raw_data
        mock_transform.return_value = transformed_data
        
        result = RunDataService.fetch_single_run_data('123456789', include_stats=False)
        
        assert result == transformed_data
        mock_stats.assert_not_called()
    
    @patch('myapp.services.run_service.StatsProcessingService.fetch_comprehensive_stats')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_stats_error(self, mock_cache, mock_fetch_details, mock_transform, mock_stats):
        """Test handling stats fetch error"""
        raw_data = {'workload': 'test', 'peak_iter': 1000}
        transformed_data = {'Workload Type': 'test', 'Peak Iteration': 1000}
        
        mock_cache.get.return_value = None
        mock_fetch_details.return_value = raw_data
        mock_transform.return_value = transformed_data
        mock_stats.side_effect = Exception("Stats error")
        
        result = RunDataService.fetch_single_run_data('123456789')
        
        assert 'stats_error' in result
        assert 'Could not fetch stats data: Stats error' in result['stats_error']
    
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_api_error(self, mock_cache, mock_fetch_details):
        """Test handling API error"""
        mock_cache.get.return_value = None
        mock_fetch_details.side_effect = Exception("API error")
        
        with pytest.raises(Exception) as exc_info:
            RunDataService.fetch_single_run_data('123456789')
        
        assert "Error fetching data for 123456789: API error" in str(exc_info.value)
    
    @patch('myapp.services.run_service.CompatibilityService.check_workload_compatibility')
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_comparison_data_success(self, mock_fetch_single, mock_compatibility):
        """Test successful comparison data fetch"""
        data1 = {'Workload Type': 'test1', 'id': '123456789'}
        data2 = {'Workload Type': 'test2', 'id': '987654321'}
        compatibility_result = {'compatible': True, 'workload1': 'test1', 'workload2': 'test2'}
        
        mock_fetch_single.side_effect = [data1, data2]
        mock_compatibility.return_value = compatibility_result
        
        result = RunDataService.fetch_comparison_data('123456789', '987654321')
        
        assert 'id1' in result
        assert 'id2' in result
        assert 'comparison_allowed' in result
        assert result['id1'] == data1
        assert result['id2'] == data2
        assert result['comparison_allowed'] == True
    
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_comparison_data_first_id_error(self, mock_fetch_single):
        """Test comparison when first ID has error"""
        mock_fetch_single.side_effect = [None, {'Workload Type': 'test2'}]
        
        result = RunDataService.fetch_comparison_data('invalid123', '987654321')
        
        assert 'error_id1' in result
        assert 'ID 1: invalid123 is incorrect.' in result['error_id1']
        assert 'id2' in result
    
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_comparison_data_second_id_error(self, mock_fetch_single):
        """Test comparison when second ID has error"""
        mock_fetch_single.side_effect = [{'Workload Type': 'test1'}, None]
        
        result = RunDataService.fetch_comparison_data('123456789', 'invalid456')
        
        assert 'id1' in result
        assert 'error_id2' in result
        assert 'ID 2: invalid456 is incorrect.' in result['error_id2']
    
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_comparison_data_exception_handling(self, mock_fetch_single):
        """Test comparison with exception handling"""
        mock_fetch_single.side_effect = [Exception("Fetch error"), {'Workload Type': 'test2'}]
        
        result = RunDataService.fetch_comparison_data('123456789', '987654321')
        
        assert 'error_id1' in result
        assert 'Error fetching ID 1: Fetch error' in result['error_id1']
        assert 'id2' in result
    
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_success(self, mock_fetch_single):
        """Test successful multiple runs data fetch"""
        run_data = [
            {'Workload Type': 'test1', 'id': '123456789'},
            {'Workload Type': 'test2', 'id': '987654321'}
        ]
        mock_fetch_single.side_effect = run_data
        
        result = RunDataService.fetch_multiple_runs_data(['123456789', '987654321'])
        
        assert 'results' in result
        assert 'success_count' in result
        assert 'error_count' in result
        assert len(result['results']) == 2
        assert result['success_count'] == 2
        assert result['error_count'] == 0
    
    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_with_errors(self, mock_fetch_single):
        """Test multiple runs fetch with some errors"""
        mock_fetch_single.side_effect = [
            {'Workload Type': 'test1', 'id': '123456789'},
            None,  # Second run not found
            Exception("API error")  # Third run has error
        ]
        
        # Use valid 9-character IDs
        result = RunDataService.fetch_multiple_runs_data(['123456789', '987654321', '555555555'])
        
        assert 'results' in result
        assert 'errors' in result
        assert '123456789' in result['results']
        assert result['success_count'] == 1
        assert result['error_count'] == 2
    
    def test_fetch_multiple_runs_data_invalid_id_length(self):
        """Test multiple runs fetch with invalid ID lengths"""
        with pytest.raises(ValueError) as exc_info:
            RunDataService.fetch_multiple_runs_data(['123456789', 'invalid123', '555555555'])
        
        assert "All IDs must be exactly 9 characters long" in str(exc_info.value)
        assert "invalid123" in str(exc_info.value)
    
    def test_fetch_multiple_runs_data_empty_list(self):
        """Test multiple runs fetch with empty list"""
        result = RunDataService.fetch_multiple_runs_data([])
        
        assert result['success_count'] == 0
        assert result['error_count'] == 0
        assert result['total_requested'] == 0
        assert result['results'] == {}
        assert result['errors'] is None


class TestGraphDataManagerService:
    """Test cases for GraphDataManagerService"""
    
    @patch('myapp.services.run_service.GraphDataService.fetch_graph_data')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_graph_data_success(self, mock_cache, mock_fetch_graph):
        """Test successful single graph data fetch"""
        graph_data = {'timestamps': [1, 2, 3], 'values': [10, 20, 30]}
        
        mock_cache.get.return_value = None
        mock_fetch_graph.return_value = graph_data
        
        result = GraphDataManagerService.fetch_single_graph_data('123456789')
        
        # Should return wrapped data with data_points containing the run_id key
        expected = {'data_points': {'123456789': graph_data}}
        assert result == expected
        mock_fetch_graph.assert_called_once_with('123456789')
        mock_cache.put.assert_called_once()
    
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_graph_data_from_cache(self, mock_cache):
        """Test fetching graph data from cache"""
        cached_data = {'timestamps': [1, 2, 3], 'values': [10, 20, 30]}
        mock_cache.get.return_value = cached_data
        
        result = GraphDataManagerService.fetch_single_graph_data('123456789')
        
        # Should return wrapped data even from cache
        expected = {'data_points': {'123456789': cached_data}}
        assert result == expected
        mock_cache.get.assert_called_once_with('graph_123456789')
    
    @patch('myapp.services.run_service.GraphDataService.fetch_graph_data')
    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_graph_data_not_found(self, mock_cache, mock_fetch_graph):
        """Test handling when graph data is not found"""
        mock_cache.get.return_value = None
        mock_fetch_graph.return_value = None
        
        result = GraphDataManagerService.fetch_single_graph_data('invalid123')
        
        assert result is None
    
    @patch('myapp.services.run_service.GraphDataManagerService.fetch_single_graph_data')
    def test_fetch_comparison_graph_data_success(self, mock_fetch_single):
        """Test successful comparison graph data fetch"""
        graph1 = {'data_points': {'123456789': 'graph1'}}
        graph2 = {'data_points': {'987654321': 'graph2'}}
        
        mock_fetch_single.side_effect = [graph1, graph2]
        
        result = GraphDataManagerService.fetch_comparison_graph_data('123456789', '987654321')
        
        expected = {
            'data_points': {
                '123456789': 'graph1',
                '987654321': 'graph2'
            }
        }
        assert result == expected
    
    @patch('myapp.services.run_service.GraphDataManagerService.fetch_single_graph_data')
    def test_fetch_comparison_graph_data_partial_success(self, mock_fetch_single):
        """Test comparison graph data with partial success"""
        graph1 = {'data_points': {'123456789': 'graph1'}}
        
        mock_fetch_single.side_effect = [graph1, None]
        
        result = GraphDataManagerService.fetch_comparison_graph_data('123456789', 'invalid123')
        
        expected = {
            'data_points': {'123456789': 'graph1'},
            'missing_data': ['No graph data available for run ID: invalid123']
        }
        assert result == expected
    
    @patch('myapp.services.run_service.GraphDataManagerService.fetch_single_graph_data')
    def test_fetch_comparison_graph_data_both_missing(self, mock_fetch_single):
        """Test comparison graph data when both are missing"""
        mock_fetch_single.return_value = None
        
        result = GraphDataManagerService.fetch_comparison_graph_data('invalid123', 'invalid456')
        
        expected = {
            'data_points': {},
            'missing_data': [
                'No graph data available for run ID: invalid123',
                'No graph data available for run ID: invalid456'
            ]
        }
        assert result == expected
    
    @patch('myapp.services.run_service.GraphDataManagerService.fetch_single_graph_data')
    def test_fetch_comparison_graph_data_single_run(self, mock_fetch_single):
        """Test comparison graph data with single run (no second ID)"""
        graph1 = {'data_points': {'123456789': 'graph1'}}
        
        mock_fetch_single.return_value = graph1
        
        result = GraphDataManagerService.fetch_comparison_graph_data('123456789')
        
        assert result == graph1
