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

    @patch('myapp.services.api_service.requests.get')
    def test_fetch_run_details_with_real_data_structure(self, mock_get):
        """Test API call using real data structure from production cache"""
        # Real API response structure (before transformation)
        real_api_response = {
            'workload': 'rndwrite_op_rate',
            'peak_iter': '3_62900.0',
            'ontap_ver': 'R9.17.1xN_250714_0000',
            'peak_ops': '28301',
            'peak_lat': '-1',
            'model': 'AWS_M6IN_16XLARGE_LDM_DOT'
        }
        
        mock_response = Mock()
        mock_response.json.return_value = real_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the method with a real run ID format
        result = ExternalAPIService.fetch_run_details('250729hhm')
        
        # Assertions
        assert result == real_api_response
        assert result['workload'] == 'rndwrite_op_rate'
        assert result['ontap_ver'] == 'R9.17.1xN_250714_0000'
        assert result['model'] == 'AWS_M6IN_16XLARGE_LDM_DOT'
        
        # Verify the correct API URL was called
        expected_url = f'{ExternalAPIService.BASE_API_URL}/250729hhm?req_fields={ExternalAPIService.DEFAULT_FIELDS}'
        mock_get.assert_called_once_with(expected_url, timeout=30)

    @patch('myapp.services.api_service.requests.get')
    def test_fetch_run_details_real_workload_validation(self, mock_get):
        """Test workload validation with real workload types"""
        # Test with valid workload (non-zero)
        valid_response = {
            'workload': 'rndwrite_op_rate',
            'peak_iter': '2_44000.0',
            'ontap_ver': 'R9.17.1xN_250714_0000',
            'peak_ops': '28222',
            'peak_lat': '-1',
            'model': 'AWS_M6IN_16XLARGE_LDM_DOT'
        }
        
        mock_response = Mock()
        mock_response.json.return_value = valid_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = ExternalAPIService.fetch_run_details('250729hhl')
        assert result is not None
        assert result['workload'] == 'rndwrite_op_rate'
        
        # Test with invalid workload (zero - indicates invalid ID)
        invalid_response = {'workload': 0}
        mock_response.json.return_value = invalid_response
        
        result = ExternalAPIService.fetch_run_details('invalid123')
        assert result is None

    @patch('myapp.services.api_service.requests.get')
    def test_fetch_perfweb_links_real_format(self, mock_get):
        """Test perfweb links fetching with real URL patterns"""
        # Mock HTML response with real perfweb link patterns
        mock_html = '''
        <html>
        <body>
        <a href="testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2507/250729hhm/ontap_command_output/01_workload_FLEXVOL_workload_client">workload</a>
        <a href="testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2507/250729hhm/ontap_command_output/02_system_FLEXVOL_system_client">system</a>
        <a href="testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2507/250729hhm/ontap_command_output/03_wafl_FLEXVOL_wafl_client">wafl</a>
        </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        result = ExternalAPIService.fetch_perfweb_links('250729hhm')
        
        # Verify we get the expected links
        assert len(result) == 3
        assert any('workload_client' in link for link in result)
        assert any('system_client' in link for link in result)
        assert any('wafl_client' in link for link in result)
        
        # Verify the correct URL format was called
        expected_base_url = f'{ExternalAPIService.PERFWEB_BASE_URL}/testdirview.cgi?p=/x/eng/perfcloud/RESULTS/2507/250729hhm/ontap_command_output'
        mock_get.assert_called_once_with(expected_base_url, timeout=15)

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

    def test_transform_run_data_with_real_structure(self):
        """Test transformation using real API response structure from production"""
        # Real raw API response (before transformation)
        real_raw_data = {
            'workload': 'rndwrite_op_rate',
            'peak_iter': '3_62900.0',
            'ontap_ver': 'R9.17.1xN_250714_0000',
            'peak_ops': '28301',
            'peak_lat': '-1',
            'model': 'AWS_M6IN_16XLARGE_LDM_DOT'
        }
        
        result = DataTransformService.transform_run_data(real_raw_data)
        
        # Expected transformed data (matches cache structure)
        expected_transformed = {
            'Workload Type': 'rndwrite_op_rate',
            'Peak Iteration': '3_62900.0',
            'ONTAP version': 'R9.17.1xN_250714_0000',
            'Achieved Ops': '28301',
            'Peak Latency': '-1',
            'Model': 'AWS_M6IN_16XLARGE_LDM_DOT'
        }
        
        assert result == expected_transformed
        
        # Verify specific field transformations
        assert result['Workload Type'] == 'rndwrite_op_rate'
        assert result['ONTAP version'] == 'R9.17.1xN_250714_0000' 
        assert result['Model'] == 'AWS_M6IN_16XLARGE_LDM_DOT'
        assert result['Peak Latency'] == '-1'  # Real data shows -1 for some latency values


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
