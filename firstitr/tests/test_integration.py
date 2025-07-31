"""
Integration Tests for Backend Services
Tests the integration between different services
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from myapp.services.api_service import ExternalAPIService, DataTransformService, CompatibilityService
from myapp.services.stats_service import StatsProcessingService, GraphDataService
from myapp.services.run_service import RunDataService, GraphDataManagerService
from myapp.cache_manager import LRUCache


class TestServiceIntegration:
    """Test cases for service integration"""

    @patch('myapp.services.api_service.requests.get')
    def test_full_data_pipeline_integration(self, mock_requests):
        """Test complete data pipeline from API to transformation"""
        # Setup mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'workload': 'test_workload',
            'peak_iter': 100,
            'ontap_ver': '9.14.1',
            'peak_ops': 50000,
            'peak_lat': 1.5,
            'model': 'A800'
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response

        # Execute full pipeline
        raw_data = ExternalAPIService.fetch_run_details('123456789')
        transformed_data = DataTransformService.transform_run_data(raw_data)

        # Assert
        assert raw_data is not None
        assert transformed_data is not None
        assert 'Workload Type' in transformed_data
        assert transformed_data['Workload Type'] == 'test_workload'
        assert 'Model' in transformed_data
        assert transformed_data['Model'] == 'A800'

    def test_compatibility_check_integration(self):
        """Test compatibility checking between different data formats"""
        # Setup test data
        data1 = {
            'Workload Type': 'sequential_read',
            'Model': 'A800',
            'Peak Iteration': 100
        }
        data2 = {
            'Workload Type': 'sequential_read',
            'Model': 'A800',
            'Peak Iteration': 150
        }
        data3 = {
            'Workload Type': 'random_write',
            'Model': 'A900',
            'Peak Iteration': 80
        }

        # Test compatible runs
        result1 = CompatibilityService.check_workload_compatibility(data1, data2)
        assert result1['compatible'] == True

        # Test incompatible workload
        result2 = CompatibilityService.check_workload_compatibility(data1, data3)
        assert result2['compatible'] == False
        assert result2['error_type'] == 'workload'

        # Test incompatible model with same workload
        data4 = {
            'Workload Type': 'sequential_read',
            'Model': 'A900',
            'Peak Iteration': 80
        }
        result3 = CompatibilityService.check_workload_compatibility(data1, data4)
        assert result3['compatible'] == False
        assert result3['error_type'] == 'model'

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_stats_processing_integration(self, mock_fetch_file, mock_fetch_links):
        """Test stats processing pipeline integration"""
        # Setup
        mock_fetch_links.return_value = ['link1', 'link2']
        mock_fetch_file.return_value = """
        write_data:104857600b/s
        read_io_type.cache:75%
        read_io_type.disk:25%
        cpu_busy:42.5%
        rdma_actual_latency.WAFL_SPINNP_WRITE:125.3us
        Instance Type: Test Instance Type
        """

        # Execute
        result = StatsProcessingService.fetch_comprehensive_stats('123456789')

        # Assert
        assert isinstance(result, dict)
        # Should have processed the stats and returned aggregated results
        mock_fetch_links.assert_called_once_with('123456789')
        assert mock_fetch_file.call_count > 0

    @patch('myapp.cache_manager.settings.BASE_DIR', '/tmp')
    @patch('os.path.exists', return_value=False)
    def test_cache_integration_with_services(self, mock_exists):
        """Test cache integration with service classes"""
        # Setup
        cache = LRUCache(max_size=3)
        
        # Test cache operations
        test_data = {
            'Workload Type': 'test_workload',
            'Model': 'A800',
            'Peak Iteration': 100
        }
        
        # Put data in cache
        cache.put('test_key', test_data)
        
        # Retrieve data
        retrieved_data = cache.get('test_key')
        
        # Assert
        assert retrieved_data == test_data
        
        # Test cache status
        status = cache.get_status()
        assert status['size'] == 1
        assert 'test_key' in status['details_keys']

    def test_numeric_value_extraction_edge_cases(self):
        """Test edge cases for numeric value extraction"""
        # Test integer extraction
        text1 = "ops:12345/s and some other text"
        result1 = DataTransformService.extract_numeric_value(text1, r'ops:(\d+)/s', int)
        assert result1 == 12345

        # Test float extraction
        text2 = "latency:1.25us in microseconds"
        result2 = DataTransformService.extract_numeric_value(text2, r'latency:(\d+\.\d+)us', float)
        assert result2 == 1.25

        # Test no match
        text3 = "no matching pattern here"
        result3 = DataTransformService.extract_numeric_value(text3, r'ops:(\d+)/s', int)
        assert result3 is None

        # Test invalid format
        text4 = "ops:invalid/s"
        result4 = DataTransformService.extract_numeric_value(text4, r'ops:(\w+)/s', int)
        assert result4 is None

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_graph_data_processing_integration(self, mock_fetch_file, mock_fetch_links):
        """Test graph data processing pipeline"""
        # Setup
        mock_fetch_links.return_value = ['iteration1', 'iteration2']
        mock_fetch_file.return_value = """
        latency:1.25us
        ops:50000/s
        write_data:104857600b/s
        """

        # Execute
        result = GraphDataService.fetch_graph_data('123456789')

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2  # Two iterations
        for data_point in result:
            assert 'latency' in data_point
            assert 'ops' in data_point
            assert 'throughput' in data_point

    def test_error_handling_across_services(self):
        """Test error handling propagation across service layers"""
        # Test DataTransformService with empty data
        empty_result = DataTransformService.transform_run_data({})
        assert empty_result == {}

        # Test DataTransformService with None
        none_result = DataTransformService.transform_run_data(None)
        assert none_result == {}

        # Test CompatibilityService with missing fields
        incomplete_data1 = {'Workload Type': 'test'}
        incomplete_data2 = {'Model': 'A800'}
        
        result = CompatibilityService.check_workload_compatibility(incomplete_data1, incomplete_data2)
        assert result['compatible'] == True  # Should handle missing fields gracefully

    def test_data_transformation_field_mapping(self):
        """Test complete field mapping transformation"""
        # Setup comprehensive raw data
        raw_data = {
            'workload': 'sequential_read',
            'peak_iter': 150,
            'ontap_ver': '9.14.1P3',
            'peak_ops': 75000,
            'peak_lat': 0.95,
            'model': 'A900',
            'extra_field': 'should_be_ignored'
        }

        # Execute transformation
        transformed = DataTransformService.transform_run_data(raw_data)

        # Assert all mapped fields are present
        expected_fields = [
            'Workload Type',
            'Peak Iteration', 
            'ONTAP version',
            'Achieved Ops',
            'Peak Latency',
            'Model'
        ]
        
        for field in expected_fields:
            assert field in transformed
        
        # Assert unmapped fields are excluded
        assert 'extra_field' not in transformed
        
        # Assert correct values
        assert transformed['Workload Type'] == 'sequential_read'
        assert transformed['Model'] == 'A900'
        assert transformed['Peak Iteration'] == 150
