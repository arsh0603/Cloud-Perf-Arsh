"""
Tests for Run Service
Tests all functions in run_service.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from myapp.services.run_service import RunDataService, GraphDataManagerService


class TestRunDataService:
    """Test cases for RunDataService class"""

    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_run_data_from_cache(self, mock_cache, sample_transformed_data):
        """Test fetching single run data from cache"""
        # Setup
        mock_cache.get.return_value = sample_transformed_data

        # Execute
        result = RunDataService.fetch_single_run_data('123456789')

        # Assert
        assert result == sample_transformed_data
        mock_cache.get.assert_called_once_with('details_123456789')

    @patch('myapp.services.run_service.api_cache')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    @patch('myapp.services.run_service.StatsProcessingService.fetch_comprehensive_stats')
    def test_fetch_single_run_data_from_api(self, mock_stats, mock_transform, mock_api, mock_cache, sample_run_data, sample_transformed_data, sample_stats_data):
        """Test fetching single run data from API"""
        # Setup
        mock_cache.get.return_value = None  # Not in cache
        mock_api.return_value = sample_run_data
        mock_transform.return_value = sample_transformed_data
        mock_stats.return_value = sample_stats_data

        expected_result = {**sample_transformed_data, **sample_stats_data}

        # Execute
        result = RunDataService.fetch_single_run_data('123456789')

        # Assert
        assert result == expected_result
        mock_cache.get.assert_called_once_with('details_123456789')
        mock_api.assert_called_once_with('123456789')
        mock_transform.assert_called_once_with(sample_run_data)
        mock_stats.assert_called_once_with('123456789')
        mock_cache.put.assert_called_once()

    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    def test_fetch_single_run_data_invalid_id(self, mock_api):
        """Test fetching single run data with invalid ID"""
        # Setup
        mock_api.return_value = None  # Invalid ID returns None

        # Execute
        result = RunDataService.fetch_single_run_data('000000000')

        # Assert
        assert result is None
        mock_api.assert_called_once_with('000000000')

    @patch('myapp.services.run_service.api_cache')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    @patch('myapp.services.run_service.StatsProcessingService.fetch_comprehensive_stats')
    def test_fetch_single_run_data_stats_error(self, mock_stats, mock_transform, mock_api, mock_cache, sample_run_data, sample_transformed_data):
        """Test fetching single run data when stats fetching fails"""
        # Setup
        mock_cache.get.return_value = None
        mock_api.return_value = sample_run_data
        mock_transform.return_value = sample_transformed_data
        mock_stats.side_effect = Exception("Stats fetch error")

        # Execute
        result = RunDataService.fetch_single_run_data('123456789')

        # Assert
        assert 'stats_error' in result
        assert "Could not fetch stats data" in result['stats_error']

    @patch('myapp.services.run_service.api_cache')
    @patch('myapp.services.run_service.ExternalAPIService.fetch_run_details')
    @patch('myapp.services.run_service.DataTransformService.transform_run_data')
    def test_fetch_single_run_data_without_stats(self, mock_transform, mock_api, mock_cache, sample_run_data, sample_transformed_data):
        """Test fetching single run data without stats"""
        # Setup
        mock_cache.get.return_value = None
        mock_api.return_value = sample_run_data
        mock_transform.return_value = sample_transformed_data

        # Execute
        result = RunDataService.fetch_single_run_data('123456789', include_stats=False)

        # Assert
        assert result == sample_transformed_data
        assert 'stats_error' not in result

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    @patch('myapp.services.run_service.CompatibilityService.check_workload_compatibility')
    def test_fetch_comparison_data_compatible(self, mock_compatibility, mock_single_fetch, sample_transformed_data):
        """Test fetching comparison data for compatible runs"""
        # Setup
        data1 = {**sample_transformed_data, 'id': '123456789'}
        data2 = {**sample_transformed_data, 'id': '987654321'}

        mock_single_fetch.side_effect = [data1, data2]
        mock_compatibility.return_value = {'compatible': True}

        # Execute
        result = RunDataService.fetch_comparison_data('123456789', '987654321')

        # Assert
        assert 'id1' in result
        assert 'id2' in result
        assert result['comparison_allowed'] == True
        assert result['id1'] == data1
        assert result['id2'] == data2

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    @patch('myapp.services.run_service.CompatibilityService.check_workload_compatibility')
    def test_fetch_comparison_data_incompatible(self, mock_compatibility, mock_single_fetch, sample_transformed_data):
        """Test fetching comparison data for incompatible runs"""
        # Setup
        data1 = {**sample_transformed_data, 'Workload Type': 'workload1'}
        data2 = {**sample_transformed_data, 'Workload Type': 'workload2'}

        mock_single_fetch.side_effect = [data1, data2]
        mock_compatibility.return_value = {
            'compatible': False,
            'error_type': 'workload',
            'message': 'Different workload types',
            'workload1': 'workload1',
            'workload2': 'workload2'
        }

        # Execute
        result = RunDataService.fetch_comparison_data('123456789', '987654321')

        # Assert
        assert 'comparison_error' in result
        assert result['comparison_error']['comparison_allowed'] == False
        assert result['comparison_error']['error_type'] == 'workload'

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_comparison_data_missing_run(self, mock_single_fetch):
        """Test fetching comparison data when one run is missing"""
        # Setup
        mock_single_fetch.side_effect = [None, {'id': '987654321'}]  # First run not found

        # Execute
        result = RunDataService.fetch_comparison_data('123456789', '987654321')

        # Assert
        assert 'error_id1' in result
        assert 'id2' in result
        assert 'ID 1: 123456789 is incorrect' in result['error_id1']

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_success(self, mock_single_fetch, sample_transformed_data):
        """Test fetching multiple runs data successfully"""
        # Setup
        run_ids = ['123456789', '987654321', '555666777']
        data1 = {**sample_transformed_data, 'id': '123456789'}
        data2 = {**sample_transformed_data, 'id': '987654321'}
        data3 = {**sample_transformed_data, 'id': '555666777'}

        mock_single_fetch.side_effect = [data1, data2, data3]

        # Execute
        result = RunDataService.fetch_multiple_runs_data(run_ids)

        # Assert
        assert result['success_count'] == 3
        assert result['error_count'] == 0
        assert result['total_requested'] == 3
        assert '123456789' in result['results']
        assert '987654321' in result['results']
        assert '555666777' in result['results']

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_with_invalid(self, mock_single_fetch, sample_transformed_data):
        """Test fetching multiple runs data with some invalid IDs"""
        # Setup
        run_ids = ['123456789', '000000000', '555666777']  # Middle one is invalid
        data1 = {**sample_transformed_data, 'id': '123456789'}
        data3 = {**sample_transformed_data, 'id': '555666777'}

        mock_single_fetch.side_effect = [data1, None, data3]  # Middle returns None

        # Execute
        result = RunDataService.fetch_multiple_runs_data(run_ids)

        # Assert
        assert result['success_count'] == 2
        assert result['error_count'] == 1
        assert '123456789' in result['results']
        assert '555666777' in result['results']
        assert '000000000' in result['errors']

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_empty_list(self, mock_single_fetch):
        """Test fetching multiple runs data with empty list"""
        # Execute
        result = RunDataService.fetch_multiple_runs_data([])

        # Assert
        assert result['success_count'] == 0
        assert result['error_count'] == 0
        assert result['total_requested'] == 0
        assert result['results'] == {}

    @patch('myapp.services.run_service.RunDataService.fetch_single_run_data')
    def test_fetch_multiple_runs_data_exception_handling(self, mock_single_fetch, sample_transformed_data):
        """Test fetching multiple runs data with exception handling"""
        # Setup
        run_ids = ['123456789', '987654321']
        data1 = {**sample_transformed_data, 'id': '123456789'}

        mock_single_fetch.side_effect = [data1, Exception("Network error")]

        # Execute
        result = RunDataService.fetch_multiple_runs_data(run_ids)

        # Assert
        assert result['success_count'] == 1
        assert result['error_count'] == 1
        assert '123456789' in result['results']
        assert '987654321' in result['errors']
        assert result['errors']['987654321'] == 'Network error'

    def test_fetch_multiple_runs_data_too_many_ids(self):
        """Test fetching multiple runs data with too many IDs"""
        # Setup
        run_ids = [f'{i:09d}' for i in range(55)]  # 55 IDs (over limit of 50)

        # Execute & Assert
        with pytest.raises(ValueError) as exc_info:
            RunDataService.fetch_multiple_runs_data(run_ids)
        
        assert 'Maximum 50 IDs allowed' in str(exc_info.value)

    def test_fetch_multiple_runs_data_invalid_id_length(self):
        """Test fetching multiple runs data with invalid ID lengths"""
        # Setup
        run_ids = ['12345', '1234567890']  # Wrong lengths

        # Execute & Assert
        with pytest.raises(ValueError) as exc_info:
            RunDataService.fetch_multiple_runs_data(run_ids)
        
        assert 'All IDs must be exactly 9 characters long' in str(exc_info.value)


class TestGraphDataManagerService:
    """Test cases for GraphDataManagerService class"""

    @patch('myapp.services.run_service.api_cache')
    def test_fetch_single_graph_data_from_cache(self, mock_cache, sample_graph_data):
        """Test fetching single graph data from cache"""
        # Setup
        mock_cache.get.return_value = sample_graph_data

        # Execute
        result = GraphDataManagerService.fetch_single_graph_data('123456789')

        # Assert
        assert result is not None
        assert 'data_points' in result
        assert '123456789' in result['data_points']
        mock_cache.get.assert_called_once_with('graph_123456789')

    @patch('myapp.services.run_service.api_cache')
    @patch('myapp.services.run_service.GraphDataService.fetch_graph_data')
    def test_fetch_single_graph_data_from_api(self, mock_graph_service, mock_cache, sample_graph_data):
        """Test fetching single graph data from API"""
        # Setup
        mock_cache.get.return_value = None  # Not in cache
        mock_graph_service.return_value = sample_graph_data

        # Execute
        result = GraphDataManagerService.fetch_single_graph_data('123456789')

        # Assert
        assert result is not None
        assert 'data_points' in result
        mock_cache.put.assert_called_once()

    @patch('myapp.services.run_service.api_cache')
    @patch('myapp.services.run_service.GraphDataService.fetch_graph_data')
    def test_fetch_single_graph_data_no_data(self, mock_graph_service, mock_cache):
        """Test fetching single graph data when no data available"""
        # Setup
        mock_cache.get.return_value = None  # Not in cache
        mock_graph_service.return_value = None  # No data available

        # Execute
        result = GraphDataManagerService.fetch_single_graph_data('123456789')

        # Assert
        assert result is None
