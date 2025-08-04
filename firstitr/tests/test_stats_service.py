"""
Test suite for stats_service module
Tests the StatsProcessingService and GraphDataService classes
"""
import pytest
from unittest.mock import patch, MagicMock
from myapp.services.stats_service import StatsProcessingService, GraphDataService


class TestStatsProcessingService:
    """Test cases for StatsProcessingService"""
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_comprehensive_stats_success(self, mock_fetch_file, mock_fetch_links):
        """Test successful comprehensive stats fetch"""
        # Setup mocks
        mock_fetch_links.return_value = ['link1', 'link2']
        # Each link calls: workload, system, wafl_flexlog (3 calls) + instance type tries for each link
        mock_fetch_file.side_effect = [
            'write_data:1048576b/s\nread_io_type.cache:75%\ncpu_busy:80.5%',  # link1 stats_workload.txt
            'cpu_busy:85.2%',  # link1 stats_system.txt  
            'rdma_actual_latency.WAFL_SPINNP_WRITE:125.5us',  # link1 stats_wafl_flexlog.txt
            'write_data:2097152b/s\nread_io_type.cache:80%\ncpu_busy:75.0%',  # link2 stats_workload.txt
            'cpu_busy:90.1%',  # link2 stats_system.txt
            'rdma_actual_latency.WAFL_SPINNP_WRITE:115.0us',  # link2 stats_wafl_flexlog.txt
            'Instance Type: c5.xlarge',  # link1 instance type file
            None,  # link2 instance type file (already got it from link1)
        ]
        
        result = StatsProcessingService.fetch_comprehensive_stats('202412345')
        
        # Verify structure and content
        assert isinstance(result, dict)
        assert 'Maximum Throughput' in result
        assert 'Maximum Cache Percentage' in result
        assert 'Maximum System CPU Busy' in result
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    def test_fetch_comprehensive_stats_no_links(self, mock_fetch_links):
        """Test stats fetch when no perfweb links are available"""
        mock_fetch_links.return_value = []
        
        result = StatsProcessingService.fetch_comprehensive_stats('202412345')
        
        assert result == {}
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_comprehensive_stats_no_files(self, mock_fetch_file, mock_fetch_links):
        """Test stats fetch when no stats files are available"""
        mock_fetch_links.return_value = ['link1', 'link2']
        mock_fetch_file.return_value = None  # All files return None
        
        result = StatsProcessingService.fetch_comprehensive_stats('202412345')
        
        assert result == {}
    
    def test_extract_workload_stats(self):
        """Test workload stats extraction"""
        test_data = 'write_data:1048576b/s\nread_io_type.cache:75%\nread_io_type.disk:25%'
        collectors = {
            'throughputs': [],
            'cache_percentages': [],
            'ext_cache_percentages': [],
            'disk_percentages': [],
            'bamboo_ssd_percentages': []
        }
        
        StatsProcessingService._extract_workload_stats(test_data, collectors)
        
        assert len(collectors['throughputs']) == 1
        assert collectors['throughputs'][0] == 1048576
        assert len(collectors['cache_percentages']) == 1
        assert collectors['cache_percentages'][0] == 75
    
    def test_extract_system_stats(self):
        """Test system stats extraction"""
        test_data = 'cpu_busy:85.5%'
        collectors = {'cpu_busy': []}
        
        StatsProcessingService._extract_system_stats(test_data, collectors)
        
        assert len(collectors['cpu_busy']) == 1
        assert collectors['cpu_busy'][0] == 85.5
    
    def test_extract_wafl_stats(self):
        """Test WAFL stats extraction"""
        test_data = 'rdma_actual_latency.WAFL_SPINNP_WRITE:125.5us\nldma_actual_latency.WAFL_SPINNP_WRITE:115.0us'
        collectors = {'rdma_stats': [], 'ldma_stats': []}
        
        StatsProcessingService._extract_wafl_stats(test_data, collectors)
        
        assert len(collectors['rdma_stats']) == 1
        assert collectors['rdma_stats'][0] == 125.5
        assert len(collectors['ldma_stats']) == 1
        assert collectors['ldma_stats'][0] == 115.0
    
    def test_calculate_final_stats(self):
        """Test final stats calculation"""
        collectors = {
            'throughputs': [1048576, 2097152],
            'cache_percentages': [75, 80],
            'ext_cache_percentages': [],
            'disk_percentages': [25, 20],
            'bamboo_ssd_percentages': [],
            'rdma_stats': [125.5, 115.0],
            'ldma_stats': [110.0, 120.0],
            'cpu_busy': [85.5, 90.1]
        }
        
        result = StatsProcessingService._calculate_final_stats(collectors, 'c5.xlarge')
        
        assert result['Maximum Throughput'] == 2097152 / (1024 * 1024)  # 2 MB/s
        assert result['Maximum Cache Percentage'] == 80
        assert result['Maximum Disk Percentage'] == 25
        assert result['Maximum WAFL RDMA Write Latency'] == 125.5
        assert result['Maximum WAFL LDMA Write Latency'] == 120.0
        assert result['Maximum System CPU Busy'] == 90.1
        assert result['Instance Type'] == 'c5.xlarge'
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_extract_instance_type(self, mock_fetch_file):
        """Test instance type extraction"""
        mock_fetch_file.return_value = 'Instance Type: c5.xlarge\nOther data...'
        
        result = StatsProcessingService._extract_instance_type('2024', '12345', 'link1')
        
        assert result == 'c5.xlarge'
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_extract_instance_type_not_found(self, mock_fetch_file):
        """Test instance type extraction when not found"""
        mock_fetch_file.return_value = 'Some other data without instance type'
        
        result = StatsProcessingService._extract_instance_type('2024', '12345', 'link1')
        
        assert result is None


class TestGraphDataService:
    """Test cases for GraphDataService"""
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_graph_data_success(self, mock_fetch_file, mock_fetch_links):
        """Test successful graph data fetch"""
        mock_fetch_links.return_value = ['link1', 'link2']
        mock_fetch_file.side_effect = [
            'latency:2.5us\nops:50000/s\nwrite_data:1048576b/s',
            'latency:2.3us\nops:55000/s\nwrite_data:1073741824b/s'
        ]
        
        result = GraphDataService.fetch_graph_data('202412345')
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['latency'] == 2.5
        assert result[0]['ops'] == 50000
        assert result[0]['throughput'] == 1048576
        assert result[1]['latency'] == 2.3
        assert result[1]['ops'] == 55000
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    def test_fetch_graph_data_no_links(self, mock_fetch_links):
        """Test graph data fetch when no perfweb links are available"""
        mock_fetch_links.return_value = []
        
        result = GraphDataService.fetch_graph_data('202412345')
        
        assert result is None
    
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_graph_data_no_time_series(self, mock_fetch_file, mock_fetch_links):
        """Test graph data fetch when no time series files are available"""
        mock_fetch_links.return_value = ['link1']
        mock_fetch_file.return_value = None
        
        result = GraphDataService.fetch_graph_data('202412345')
        
        assert result is None
    
    def test_extract_graph_point_success(self):
        """Test successful graph point extraction"""
        stats_text = 'latency:2.5us\nops:50000/s\nwrite_data:1048576b/s'
        
        result = GraphDataService._extract_graph_point(stats_text)
        
        assert result is not None
        assert result['latency'] == 2.5
        assert result['ops'] == 50000
        assert result['throughput'] == 1048576
    
    def test_extract_graph_point_incomplete_data(self):
        """Test graph point extraction with incomplete data"""
        stats_text = 'latency:2.5us\nops:50000/s'  # Missing throughput
        
        result = GraphDataService._extract_graph_point(stats_text)
        
        assert result is None
    
    def test_extract_graph_point_empty_data(self):
        """Test graph point extraction with empty data"""
        stats_text = ''
        
        result = GraphDataService._extract_graph_point(stats_text)
        
        assert result is None
