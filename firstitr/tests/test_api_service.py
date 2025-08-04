"""
Unit tests for API services
Tests ExternalAPIService, DataTransformService, and CompatibilityService
"""
import pytest
from unittest.mock import Mock, patch
import requests
from requests.exceptions import RequestException
from myapp.services.api_service import ExternalAPIService, DataTransformService, CompatibilityService


class TestExternalAPIService:
    """Test cases for ExternalAPIService"""
    
    @patch('myapp.services.api_service.requests.get')
    def test_fetch_run_details_success(self, mock_get):
        """Test successful API call for run details"""
        # Setup mock response
        sample_data = {
            'workload': 'test_workload',
            'peak_iter': 1000,
            'ontap_ver': '9.14.1',
            'peak_ops': 50000,
            'peak_lat': 2.5,
            'model': 'FAS8300'
        }
        
        mock_response = Mock()
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the method
        result = ExternalAPIService.fetch_run_details('123456789')
        
        # Assertions
        assert result == sample_data
        mock_get.assert_called_once()
    
    @patch('myapp.services.api_service.requests.get')
    def test_fetch_run_details_invalid_workload(self, mock_get):
        """Test API response with workload=0 (invalid ID)"""
        mock_response = Mock()
        mock_response.json.return_value = {'workload': 0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = ExternalAPIService.fetch_run_details('invalid123')
        
        assert result is None
    
    @patch('myapp.services.api_service.requests.get')
    def test_fetch_run_details_network_error(self, mock_get):
        """Test API call with network error"""
        mock_get.side_effect = RequestException("Network error")
        
        with pytest.raises(Exception) as exc_info:
            ExternalAPIService.fetch_run_details('123456789')
        
        assert "Network error fetching data for 123456789" in str(exc_info.value)


class TestDataTransformService:
    """Test cases for DataTransformService"""
    
    def test_transform_run_data(self):
        """Test basic data transformation"""
        raw_data = {
            'workload': 'test_workload',
            'peak_iter': 1000,
            'ontap_ver': '9.14.1',
            'peak_ops': 50000,
            'peak_lat': 2.5,
            'model': 'FAS8300'
        }
        
        result = DataTransformService.transform_run_data(raw_data)
        
        # Check that transformation uses the FIELD_MAPPINGS
        expected = {
            'Workload Type': 'test_workload',
            'Peak Iteration': 1000,
            'ONTAP version': '9.14.1',
            'Achieved Ops': 50000,
            'Peak Latency': 2.5,
            'Model': 'FAS8300'
        }
        
        assert result == expected
    
    def test_transform_run_data_empty_input(self):
        """Test transformation with empty input"""
        result = DataTransformService.transform_run_data({})
        assert result == {}
    
    def test_transform_run_data_none_input(self):
        """Test transformation with None input"""
        result = DataTransformService.transform_run_data(None)
        assert result == {}


class TestCompatibilityService:
    """Test cases for CompatibilityService"""
    
    def test_check_workload_compatibility_same_workload(self):
        """Test compatibility check with same workload"""
        data1 = {'Workload Type': 'test_workload', 'Model': 'FAS8300'}
        data2 = {'Workload Type': 'test_workload', 'Model': 'FAS8300'}
        
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        assert result['compatible'] is True
        assert result['workload1'] == 'test_workload'
        assert result['workload2'] == 'test_workload'
    
    def test_check_workload_compatibility_different_workload(self):
        """Test compatibility check with different workloads"""
        data1 = {'Workload Type': 'workload_a', 'Model': 'FAS8300'}
        data2 = {'Workload Type': 'workload_b', 'Model': 'FAS8300'}
        
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        assert result['compatible'] is False
        assert result['error_type'] == 'workload'
        assert 'different workload types' in result['message']
    
    def test_check_workload_compatibility_different_model(self):
        """Test compatibility check with different models"""
        data1 = {'Workload Type': 'test_workload', 'Model': 'FAS8300'}
        data2 = {'Workload Type': 'test_workload', 'Model': 'FAS8700'}
        
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        assert result['compatible'] is False
        assert result['error_type'] == 'model'
        assert 'different model types' in result['message']
