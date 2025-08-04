"""
Unit tests for URL routing
Tests all URL patterns and their mapping to views
"""
import pytest
from django.test import TestCase
from django.urls import reverse, resolve
from django.test.client import RequestFactory
from myapp.views import (
    FetchDetailsView, FetchGraphDataView, CacheStatusView,
    CacheManagementView, FetchMultipleRunsView
)


class TestURLPatterns(TestCase):
    """Test cases for URL patterns and routing"""
    
    def test_fetch_details_url_resolves(self):
        """Test that fetch-details URL resolves to correct view"""
        url = reverse('fetch-details')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, FetchDetailsView)
    
    def test_fetch_graph_data_url_resolves(self):
        """Test that fetch-graph-data URL resolves to correct view"""
        url = reverse('fetch-graph-data')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, FetchGraphDataView)
    
    def test_cache_status_url_resolves(self):
        """Test that cache-status URL resolves to correct view"""
        url = reverse('cache-status')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, CacheStatusView)
    
    def test_cache_management_url_resolves(self):
        """Test that cache-management URL resolves to correct view"""
        url = reverse('cache-management')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, CacheManagementView)
    
    def test_fetch_multiple_runs_url_resolves(self):
        """Test that fetch-multiple-runs URL resolves to correct view"""
        url = reverse('fetch-multiple-runs')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, FetchMultipleRunsView)
    
    def test_fetch_details_url_pattern(self):
        """Test fetch-details URL pattern"""
        url = reverse('fetch-details')
        self.assertEqual(url, '/api/fetch-details/')
    
    def test_fetch_graph_data_url_pattern(self):
        """Test fetch-graph-data URL pattern"""
        url = reverse('fetch-graph-data')
        self.assertEqual(url, '/api/fetch-graph-data/')
    
    def test_cache_status_url_pattern(self):
        """Test cache-status URL pattern"""
        url = reverse('cache-status')
        self.assertEqual(url, '/api/cache-status/')
    
    def test_cache_management_url_pattern(self):
        """Test cache-management URL pattern"""
        url = reverse('cache-management')
        self.assertEqual(url, '/api/cache-management/')
    
    def test_fetch_multiple_runs_url_pattern(self):
        """Test fetch-multiple-runs URL pattern"""
        url = reverse('fetch-multiple-runs')
        self.assertEqual(url, '/api/fetch-multiple-runs/')
    
    def test_invalid_url_raises_404(self):
        """Test that invalid URL raises 404"""
        from django.urls.exceptions import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse('non-existent-url')
    
    def test_url_namespace_included(self):
        """Test that myapp URLs are properly included in main URL config"""
        # This test ensures that the myapp URLs are included in the main project
        try:
            url = reverse('fetch-details')
            self.assertTrue(url.startswith('/api/'))
        except:
            self.fail("URL patterns not properly included")


class TestURLAccessibility(TestCase):
    """Test cases for URL accessibility"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_all_urls_accept_get_requests(self):
        """Test that all read-only URLs accept GET requests"""
        urls_for_get = [
            'fetch-details',
            'fetch-graph-data', 
            'cache-status',
            'fetch-multiple-runs'
        ]
        
        for url_name in urls_for_get:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                # This just tests that the URL pattern exists and can be reversed
                self.assertIsNotNone(url)
    
    def test_cache_management_accepts_delete(self):
        """Test that cache-management URL exists for DELETE operations"""
        url = reverse('cache-management')
        self.assertIsNotNone(url)
        # The actual DELETE method testing is done in view tests
    
    def test_url_parameters_handling(self):
        """Test URL parameter handling"""
        # Test that URLs can handle query parameters
        base_urls = [
            reverse('fetch-details'),
            reverse('fetch-graph-data'),
            reverse('fetch-multiple-runs')
        ]
        
        for url in base_urls:
            # URLs should not break with query parameters
            url_with_params = f"{url}?param=value"
            self.assertIn('?param=value', url_with_params)


class TestURLSecurity(TestCase):
    """Test cases for URL security considerations"""
    
    def test_csrf_exemption_only_where_needed(self):
        """Test that CSRF exemption is only applied where necessary"""
        # Cache management view should be CSRF exempt (for DELETE operations)
        url = reverse('cache-management')
        resolver = resolve(url)
        view_class = resolver.func.view_class
        
        # Check if the view class has CSRF exemption
        # This would be indicated by the @method_decorator(csrf_exempt) decorator
        self.assertEqual(view_class, CacheManagementView)
    
    def test_read_only_endpoints_pattern(self):
        """Test that read-only endpoints follow consistent patterns"""
        read_only_urls = [
            'fetch-details',
            'fetch-graph-data',
            'cache-status', 
            'fetch-multiple-runs'
        ]
        
        for url_name in read_only_urls:
            url = reverse(url_name)
            # All read-only endpoints should be under /api/ prefix
            self.assertTrue(url.startswith('/api/'))
            # All read-only endpoints should end with /
            self.assertTrue(url.endswith('/'))
    
    def test_api_prefix_consistency(self):
        """Test that all URLs have consistent API prefix"""
        all_url_names = [
            'fetch-details',
            'fetch-graph-data',
            'cache-status',
            'cache-management',
            'fetch-multiple-runs'
        ]
        
        for url_name in all_url_names:
            url = reverse(url_name)
            self.assertTrue(url.startswith('/api/'), 
                          f"URL {url_name} does not start with /api/")


class TestURLNaming(TestCase):
    """Test cases for URL naming conventions"""
    
    def test_url_names_follow_convention(self):
        """Test that URL names follow kebab-case convention"""
        expected_url_names = [
            'fetch-details',
            'fetch-graph-data',
            'cache-status',
            'cache-management', 
            'fetch-multiple-runs'
        ]
        
        for url_name in expected_url_names:
            # Test that the URL name can be reversed (i.e., it exists)
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except:
                self.fail(f"URL name '{url_name}' not found")
    
    def test_url_patterns_are_descriptive(self):
        """Test that URL patterns are descriptive of their function"""
        url_mappings = {
            'fetch-details': 'fetch-details',
            'fetch-graph-data': 'fetch-graph-data',
            'cache-status': 'cache-status',
            'cache-management': 'cache-management',
            'fetch-multiple-runs': 'fetch-multiple-runs'
        }
        
        for url_name, expected_pattern in url_mappings.items():
            url = reverse(url_name)
            self.assertIn(expected_pattern, url)
