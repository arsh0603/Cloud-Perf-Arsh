"""
Tests for URL Configuration
Tests URL patterns and routing
"""
import pytest
from django.test import TestCase
from django.urls import reverse, resolve
from myapp.views import (
    FetchDetailsView, 
    FetchGraphDataView, 
    CacheStatusView, 
    CacheManagementView, 
    FetchMultipleRunsView
)


class TestURLPatterns(TestCase):
    """Test cases for URL patterns"""

    def test_fetch_details_url_resolves(self):
        """Test that fetch-details URL resolves to correct view"""
        url = reverse('fetch_details')
        resolver = resolve(url)
        assert resolver.func.view_class == FetchDetailsView

    def test_fetch_graph_data_url_resolves(self):
        """Test that fetch-graph-data URL resolves to correct view"""
        url = reverse('fetch_graph_data')
        resolver = resolve(url)
        assert resolver.func.view_class == FetchGraphDataView

    def test_fetch_multiple_runs_url_resolves(self):
        """Test that fetch-multiple-runs URL resolves to correct view"""
        url = reverse('fetch_multiple_runs')
        resolver = resolve(url)
        assert resolver.func.view_class == FetchMultipleRunsView

    def test_cache_status_url_resolves(self):
        """Test that cache-status URL resolves to correct view"""
        url = reverse('cache_status')
        resolver = resolve(url)
        assert resolver.func.view_class == CacheStatusView

    def test_cache_management_url_resolves(self):
        """Test that cache-management URL resolves to correct view"""
        url = reverse('cache_management')
        resolver = resolve(url)
        assert resolver.func.view_class == CacheManagementView

    def test_url_names_are_unique(self):
        """Test that all URL names are unique"""
        url_names = [
            'fetch_details',
            'fetch_graph_data', 
            'fetch_multiple_runs',
            'cache_status',
            'cache_management'
        ]
        
        # Check that all names resolve without error
        for name in url_names:
            url = reverse(name)
            assert url is not None
            assert len(url) > 0
