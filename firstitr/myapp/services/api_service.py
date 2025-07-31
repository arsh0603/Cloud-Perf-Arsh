"""
API service for external data fetching
Handles communication with external NetApp performance systems
"""
import requests
import re
from typing import Dict, Any, Optional, List


class ExternalAPIService:
    """Service for fetching data from external APIs"""
    
    BASE_API_URL = 'http://grover.rtp.netapp.com/KO/rest/api/Runs'
    PERFWEB_BASE_URL = 'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud'
    
    DEFAULT_FIELDS = 'workload,peak_iter,ontap_ver,peak_ops,peak_lat,model'
    
    @classmethod
    def fetch_run_details(cls, run_id: str, fields: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch basic run details from external API
        
        Args:
            run_id: The run ID to fetch
            fields: Comma-separated list of fields to fetch
            
        Returns:
            Dictionary containing run data or None if not found
        """
        fields = fields or cls.DEFAULT_FIELDS
        api_url = f'{cls.BASE_API_URL}/{run_id}?req_fields={fields}'
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check if workload is 0 (indicates invalid ID)
            if data.get('workload') == 0:
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error fetching data for {run_id}: {str(e)}")
    
    @classmethod
    def fetch_perfweb_links(cls, run_id: str) -> List[str]:
        """
        Fetch perfweb links for a run ID
        
        Args:
            run_id: The run ID to fetch links for
            
        Returns:
            List of perfweb links
        """
        year_month = run_id[:4]
        base_url = f'{cls.PERFWEB_BASE_URL}/testdirview.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output'
        
        try:
            response = requests.get(base_url, timeout=15)
            if response.ok:
                text = response.text
                links = re.findall(
                    r'href="(testdirview.cgi\?p=/x/eng/perfcloud/RESULTS/[^"]+/ontap_command_output/\d+_[^"]+)"', 
                    text
                )
                return links
            return []
            
        except requests.exceptions.RequestException:
            return []
    
    @classmethod
    def fetch_stats_file(cls, year_month: str, run_id: str, link: str, stats_type: str) -> Optional[str]:
        """
        Fetch content from a specific stats file
        
        Args:
            year_month: Year-month prefix
            run_id: Run ID
            link: Link path
            stats_type: Type of stats file (e.g., 'stats_workload.txt', 'stats_system.txt')
            
        Returns:
            File content as string or None if not available
        """
        stats_url = f'{cls.PERFWEB_BASE_URL}/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/{stats_type}'
        
        try:
            response = requests.get(stats_url, timeout=10)
            if response.ok:
                return response.text
            return None
            
        except requests.exceptions.RequestException:
            return None


class DataTransformService:
    """Service for transforming and formatting data"""
    
    FIELD_MAPPINGS = {
        'workload': 'Workload Type',
        'peak_iter': 'Peak Iteration',
        'ontap_ver': 'ONTAP version',
        'peak_ops': 'Achieved Ops',
        'peak_lat': 'Peak Latency',
        'model': 'Model'
    }
    
    @classmethod
    def transform_run_data(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw API data to user-friendly format
        
        Args:
            raw_data: Raw data from external API
            
        Returns:
            Transformed data with user-friendly field names
        """
        if not raw_data:
            return {}
            
        return {
            cls.FIELD_MAPPINGS.get(key, key): value
            for key, value in raw_data.items()
            if key in cls.FIELD_MAPPINGS
        }
    
    @classmethod
    def extract_numeric_value(cls, text: str, pattern: str, value_type=int):
        """
        Extract numeric value from text using regex pattern
        
        Args:
            text: Text to search in
            pattern: Regex pattern to match
            value_type: Type to convert the value to (int, float)
            
        Returns:
            Extracted value or None if not found
        """
        match = re.search(pattern, text)
        if match:
            try:
                return value_type(match.group(1))
            except (ValueError, IndexError):
                return None
        return None


class CompatibilityService:
    """Service for checking run compatibility"""
    
    @classmethod
    def check_workload_compatibility(cls, data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if two runs are compatible for comparison
        
        Args:
            data1: First run data
            data2: Second run data
            
        Returns:
            Compatibility result with details
        """
        workload1 = data1.get('Workload Type')
        workload2 = data2.get('Workload Type')
        model1 = data1.get('Model')
        model2 = data2.get('Model')
        
        # Check workload compatibility first
        if workload1 and workload2 and workload1 != workload2:
            return {
                'compatible': False,
                'error_type': 'workload',
                'message': 'Cannot compare runs with different workload types',
                'workload1': workload1,
                'workload2': workload2,
                'model1': model1,
                'model2': model2
            }
        
        # Check model compatibility
        if model1 and model2 and model1 != model2:
            return {
                'compatible': False,
                'error_type': 'model',
                'message': 'Cannot compare runs with different model types',
                'workload1': workload1,
                'workload2': workload2,
                'model1': model1,
                'model2': model2
            }
        
        return {
            'compatible': True,
            'workload1': workload1,
            'workload2': workload2,
            'model1': model1,
            'model2': model2
        }
