"""
Tests for Stats Service
Tests all functions in stats_service.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from myapp.services.stats_service import StatsProcessingService, GraphDataService


class TestStatsProcessingService:
    """Test cases for StatsProcessingService class"""

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_comprehensive_stats_success(self, mock_fetch_stats, mock_fetch_links, sample_perfweb_content):
        """Test successful comprehensive stats fetching"""
        # Setup
        mock_fetch_links.return_value = ['link1', 'link2']
        mock_fetch_stats.return_value = sample_perfweb_content

        # Execute
        result = StatsProcessingService.fetch_comprehensive_stats('123456789')

        # Assert
        assert isinstance(result, dict)
        mock_fetch_links.assert_called_once_with('123456789')
        # Should be called multiple times for different stat types
        assert mock_fetch_stats.call_count > 0

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    def test_fetch_comprehensive_stats_no_links(self, mock_fetch_links):
        """Test comprehensive stats fetching when no links available"""
        # Setup
        mock_fetch_links.return_value = []

        # Execute
        result = StatsProcessingService.fetch_comprehensive_stats('123456789')

        # Assert
        assert result == {}
        mock_fetch_links.assert_called_once_with('123456789')


class TestGraphDataService:
    """Test cases for GraphDataService class"""

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_graph_data_success(self, mock_fetch_stats, mock_fetch_links):
        """Test successful graph data fetching"""
        # Setup
        mock_fetch_links.return_value = ['link1', 'link2']
        stats_content = """
        latency:1.5us
        ops:1000/s
        write_data:1000000b/s
        """
        mock_fetch_stats.return_value = stats_content

        # Execute
        result = GraphDataService.fetch_graph_data('123456789')

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        mock_fetch_links.assert_called_once_with('123456789')

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    def test_fetch_graph_data_no_links(self, mock_fetch_links):
        """Test graph data fetching when no links available"""
        # Setup
        mock_fetch_links.return_value = []

        # Execute
        result = GraphDataService.fetch_graph_data('123456789')

        # Assert
        assert result is None
        mock_fetch_links.assert_called_once_with('123456789')

    @patch('myapp.services.stats_service.ExternalAPIService.fetch_perfweb_links')
    @patch('myapp.services.stats_service.ExternalAPIService.fetch_stats_file')
    def test_fetch_graph_data_no_valid_data(self, mock_fetch_stats, mock_fetch_links):
        """Test graph data fetching when no valid data found"""
        # Setup
        mock_fetch_links.return_value = ['link1']
        mock_fetch_stats.return_value = "no valid graph data here"

        # Execute
        result = GraphDataService.fetch_graph_data('123456789')

        # Assert
        assert result is None

    def test_extract_graph_point_valid_data(self):
        """Test extracting graph point from valid stats text"""
        # Setup
        stats_text = """
        latency:1.5us
        ops:1000/s
        write_data:1000000b/s
        """

        # Execute
        result = GraphDataService._extract_graph_point(stats_text)

        # Assert
        assert result is not None
        assert 'latency' in result
        assert 'ops' in result
        assert 'throughput' in result

    def test_extract_graph_point_invalid_data(self):
        """Test extracting graph point from invalid stats text"""
        # Setup
        stats_text = "no valid data here"

        # Execute
        result = GraphDataService._extract_graph_point(stats_text)

        # Assert
        assert result is None

    def test_extract_graph_point_partial_data(self):
        """Test extracting graph point from partial stats text"""
        # Setup
        stats_text = "latency:1.5us"  # Missing ops and throughput

        # Execute
        result = GraphDataService._extract_graph_point(stats_text)

        # Assert
        assert result is None  # Should require all three fields
