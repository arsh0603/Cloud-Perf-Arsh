"""
Tests for API Service functions
Tests all functions in services/api_service.py
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from myapp.services.api_service import (
    ExternalAPIService, 
    DataTransformService, 
    CompatibilityService
)


class TestExternalAPIService:
    """Test cases for ExternalAPIService class"""
    
    def test_fetch_run_details_success(self, mock_requests_get, sample_run_data):
        """Test successful run details fetching"""
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = sample_run_data
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        # Execute
        result = ExternalAPIService.fetch_run_details('123456789')
        
        # Assert
        assert result == sample_run_data
        mock_requests_get.assert_called_once()
        assert '123456789' in mock_requests_get.call_args[0][0]
    
    def test_fetch_run_details_invalid_id(self, mock_requests_get, sample_invalid_run_data):
        """Test fetching details for invalid run ID (workload = 0)"""
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = sample_invalid_run_data
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        # Execute
        result = ExternalAPIService.fetch_run_details('000000000')
        
        # Assert
        assert result is None
    
    def test_fetch_run_details_network_error(self, mock_requests_get):
        """Test network error handling"""
        # Setup
        mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            ExternalAPIService.fetch_run_details('123456789')
        
        assert "Network error" in str(exc_info.value)
    
    def test_fetch_run_details_timeout(self, mock_requests_get):
        """Test timeout handling"""
        # Setup
        mock_requests_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            ExternalAPIService.fetch_run_details('123456789')
        
        assert "Timeout" in str(exc_info.value)
    
    def test_fetch_run_details_custom_fields(self, mock_requests_get, sample_run_data):
        """Test fetching with custom fields"""
        # Setup
        mock_response = Mock()
        mock_response.json.return_value = sample_run_data
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        custom_fields = "workload,model,peak_ops"
        
        # Execute
        result = ExternalAPIService.fetch_run_details('123456789', custom_fields)
        
        # Assert
        assert result == sample_run_data
        called_url = mock_requests_get.call_args[0][0]
        assert custom_fields in called_url
    
    @patch('myapp.services.api_service.requests.get')
    def test_fetch_perfweb_links_success(self, mock_get):
        """Test successful perfweb links fetching"""
        # Setup
        mock_response = Mock()
        # Mock HTML content that matches the actual regex pattern
        mock_response.text = '''
        <a href="testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2023/123456789/ontap_command_output/1_iteration">Iteration 1</a>
        <a href="testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2023/123456789/ontap_command_output/2_iteration">Iteration 2</a>
        '''
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        # Execute
        result = ExternalAPIService.fetch_perfweb_links('123456789')
        
        # Assert
        assert len(result) == 2
        assert all('testdirview.cgi' in link for link in result)
    
    @patch('myapp.services.api_service.requests.get')
    def test_fetch_perfweb_links_no_links(self, mock_get):
        """Test perfweb with no links found"""
        # Setup
        mock_response = Mock()
        mock_response.text = '<html><body>No files found</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Execute
        result = ExternalAPIService.fetch_perfweb_links('123456789')
        
        # Assert
        assert result == []


class TestDataTransformService:
    """Test cases for DataTransformService class"""
    
    def test_transform_run_data_complete(self, sample_run_data):
        """Test transformation of complete run data"""
        # Execute
        result = DataTransformService.transform_run_data(sample_run_data)
        
        # Assert
        assert result['Workload Type'] == 'test_workload'
        assert result['Peak Iteration'] == 100
        assert result['ONTAP version'] == '9.14.1'
        assert result['Achieved Ops'] == 50000
        assert result['Peak Latency'] == 1.5
        assert result['Model'] == 'A800'
    
    def test_transform_run_data_missing_fields(self):
        """Test transformation with missing fields"""
        # Setup
        incomplete_data = {'workload': 'test', 'model': 'A800', 'unknown_field': 'value'}
        
        # Execute
        result = DataTransformService.transform_run_data(incomplete_data)
        
        # Assert
        assert result['Workload Type'] == 'test'
        assert result['Model'] == 'A800'
        assert 'unknown_field' not in result  # Should filter out unmapped fields
        assert len(result) == 2
    
    def test_transform_run_data_empty_data(self):
        """Test transformation with empty data"""
        # Setup
        empty_data = {}
        
        # Execute
        result = DataTransformService.transform_run_data(empty_data)
        
        # Assert
        assert result == {}
    
    def test_extract_numeric_value_integer(self):
        """Test extracting integer values"""
        text = "cpu_busy:45%"
        pattern = r'cpu_busy:(\d+)%'
        
        result = DataTransformService.extract_numeric_value(text, pattern, int)
        assert result == 45
    
    def test_extract_numeric_value_float(self):
        """Test extracting float values"""
        text = "latency:1.23us"
        pattern = r'latency:(\d+\.\d+)us'
        
        result = DataTransformService.extract_numeric_value(text, pattern, float)
        assert result == 1.23
    
    def test_extract_numeric_value_not_found(self):
        """Test extracting when pattern not found"""
        text = "no match here"
        pattern = r'cpu_busy:(\d+)%'
        
        result = DataTransformService.extract_numeric_value(text, pattern, int)
        assert result is None
    
    def test_extract_numeric_value_invalid_format(self):
        """Test extracting with invalid numeric format"""
        text = "cpu_busy:invalid%"
        pattern = r'cpu_busy:(\w+)%'
        
        result = DataTransformService.extract_numeric_value(text, pattern, int)
        assert result is None


class TestCompatibilityService:
    """Test cases for CompatibilityService class"""
    
    def test_check_workload_compatibility_same_workload_model(self):
        """Test compatibility check for same workload and model"""
        # Setup
        data1 = {'Workload Type': 'test_workload', 'Model': 'A800'}
        data2 = {'Workload Type': 'test_workload', 'Model': 'A800'}
        
        # Execute
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        # Assert
        assert result['compatible'] is True
        assert result['workload1'] == 'test_workload'
        assert result['workload2'] == 'test_workload'
        assert result['model1'] == 'A800'
        assert result['model2'] == 'A800'
    
    def test_check_workload_compatibility_different_workload(self):
        """Test compatibility check for different workloads"""
        # Setup
        data1 = {'Workload Type': 'workload1', 'Model': 'A800'}
        data2 = {'Workload Type': 'workload2', 'Model': 'A800'}
        
        # Execute
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        # Assert
        assert result['compatible'] is False
        assert result['error_type'] == 'workload'
        assert 'different workload types' in result['message']
        assert result['workload1'] == 'workload1'
        assert result['workload2'] == 'workload2'
    
    def test_check_workload_compatibility_different_model(self):
        """Test compatibility check for different models"""
        # Setup
        data1 = {'Workload Type': 'same_workload', 'Model': 'A800'}
        data2 = {'Workload Type': 'same_workload', 'Model': 'A900'}
        
        # Execute
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        # Assert
        assert result['compatible'] is False
        assert result['error_type'] == 'model'
        assert 'different model types' in result['message']
        assert result['model1'] == 'A800'
        assert result['model2'] == 'A900'
    
    def test_check_workload_compatibility_missing_workload(self):
        """Test compatibility check with missing workload data"""
        # Setup
        data1 = {'Model': 'A800'}  # Missing workload
        data2 = {'Workload Type': 'test_workload', 'Model': 'A800'}
        
        # Execute
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        # Assert
        assert result['compatible'] is True  # Should be compatible if workload comparison can't be made
        assert result['workload1'] is None
        assert result['workload2'] == 'test_workload'
    
    def test_check_workload_compatibility_missing_model(self):
        """Test compatibility check with missing model data"""
        # Setup
        data1 = {'Workload Type': 'test_workload'}  # Missing model
        data2 = {'Workload Type': 'test_workload', 'Model': 'A800'}
        
        # Execute
        result = CompatibilityService.check_workload_compatibility(data1, data2)
        
        # Assert
        assert result['compatible'] is True  # Should be compatible if model comparison can't be made
        assert result['model1'] is None
        assert result['model2'] == 'A800'
