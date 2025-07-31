"""
Tests for Management Commands
Tests all functions in management/commands/
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class TestCleanupCacheCommand(TestCase):
    """Test cases for cleanup_cache management command"""

    @patch('myapp.management.commands.cleanup_cache.PersistentCache')
    def test_cleanup_cache_dry_run(self, mock_cache):
        """Test cleanup cache command with dry run option"""
        # Setup
        mock_cache.get_stats.return_value = {
            'total_entries': 100,
            'details_count': 60,
            'graph_count': 40,
            'expired_count': 10
        }
        
        out = StringIO()
        
        # Execute
        call_command('cleanup_cache', '--dry-run', stdout=out)
        
        # Assert
        output = out.getvalue()
        assert 'DRY RUN' in output
        assert 'Would delete 10 expired entries' in output
        assert 'Total entries: 100' in output
        mock_cache.cleanup_expired.assert_not_called()

    @patch('myapp.management.commands.cleanup_cache.PersistentCache')
    def test_cleanup_cache_actual_cleanup(self, mock_cache):
        """Test cleanup cache command with actual cleanup"""
        # Setup
        stats_before = {
            'total_entries': 100,
            'details_count': 60,
            'graph_count': 40,
            'expired_count': 10
        }
        stats_after = {
            'total_entries': 90,
            'details_count': 55,
            'graph_count': 35,
            'expired_count': 0
        }
        
        mock_cache.get_stats.side_effect = [stats_before, stats_after]
        mock_cache.cleanup_expired.return_value = 10
        
        out = StringIO()
        
        # Execute
        call_command('cleanup_cache', stdout=out)
        
        # Assert
        output = out.getvalue()
        assert 'Successfully cleaned up 10 expired entries' in output
        assert 'Remaining entries: 90' in output
        mock_cache.cleanup_expired.assert_called_once()

    @patch('myapp.management.commands.cleanup_cache.PersistentCache')
    def test_cleanup_cache_no_expired_entries(self, mock_cache):
        """Test cleanup cache command when no expired entries"""
        # Setup
        mock_cache.get_stats.return_value = {
            'total_entries': 50,
            'details_count': 30,
            'graph_count': 20,
            'expired_count': 0
        }
        mock_cache.cleanup_expired.return_value = 0
        
        out = StringIO()
        
        # Execute
        call_command('cleanup_cache', stdout=out)
        
        # Assert
        output = out.getvalue()
        assert 'Successfully cleaned up 0 expired entries' in output
        assert 'Expired entries: 0' in output
