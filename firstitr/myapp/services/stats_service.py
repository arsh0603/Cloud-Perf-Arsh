"""
Statistics processing service
Handles extraction and processing of performance statistics from external sources
"""
import re
from typing import Dict, Any, List, Optional
from .api_service import ExternalAPIService, DataTransformService


class StatsProcessingService:
    """Service for processing performance statistics"""
    
    STATS_PATTERNS = {
        'throughput': r'write_data:(\d+)b/s',
        'cache': r'read_io_type\.cache:(\d+)%',
        'ext_cache': r'read_io_type\.ext_cache:(\d+)%',
        'disk': r'read_io_type\.disk:(\d+)%',
        'bamboo_ssd': r'read_io_type\.bamboo_ssd:(\d+)%',
        'cpu_busy': r'cpu_busy:(\d+(?:\.\d+)?)%',
        'rdma_latency': r'rdma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us',
        'ldma_latency': r'ldma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us',
        'instance_type': r'Instance Type:\s*([^\n\r]+)'
    }
    
    STATS_FILE_TYPES = {
        'workload': 'stats_workload.txt',
        'system': 'stats_system.txt',
        'vm_instance': 'system_node_virtual_machine_instance_show.txt',
        'wafl_flexlog': 'stats_wafl_flexlog.txt'
    }
    
    @classmethod
    def fetch_comprehensive_stats(cls, run_id: str) -> Dict[str, Any]:
        """
        Fetch comprehensive statistics for a run ID
        
        Args:
            run_id: The run ID to fetch stats for
            
        Returns:
            Dictionary containing processed statistics
        """
        year_month = run_id[:4]
        links = ExternalAPIService.fetch_perfweb_links(run_id)
        
        if not links:
            return {}
        
        # Initialize collectors
        collectors = {
            'throughputs': [],
            'cache_percentages': [],
            'ext_cache_percentages': [],
            'disk_percentages': [],
            'bamboo_ssd_percentages': [],
            'rdma_stats': [],
            'ldma_stats': [],
            'cpu_busy': []
        }
        
        instance_type = None
        
        # Process each iteration link
        for link in links:
            cls._process_iteration_stats(
                year_month, run_id, link, collectors
            )
            
            # Get instance type (only need one)
            if instance_type is None:
                instance_type = cls._extract_instance_type(year_month, run_id, link)
        
        # Calculate final statistics
        return cls._calculate_final_stats(collectors, instance_type)
    
    @classmethod
    def _process_iteration_stats(
        cls, 
        year_month: str, 
        run_id: str, 
        link: str, 
        collectors: Dict[str, List]
    ) -> None:
        """Process statistics for a single iteration"""
        
        # Process workload stats
        workload_text = ExternalAPIService.fetch_stats_file(
            year_month, run_id, link, cls.STATS_FILE_TYPES['workload']
        )
        if workload_text:
            cls._extract_workload_stats(workload_text, collectors)
        
        # Process system stats
        system_text = ExternalAPIService.fetch_stats_file(
            year_month, run_id, link, cls.STATS_FILE_TYPES['system']
        )
        if system_text:
            cls._extract_system_stats(system_text, collectors)
        
        # Process WAFL stats
        wafl_text = ExternalAPIService.fetch_stats_file(
            year_month, run_id, link, cls.STATS_FILE_TYPES['wafl_flexlog']
        )
        if wafl_text:
            cls._extract_wafl_stats(wafl_text, collectors)
    
    @classmethod
    def _extract_workload_stats(cls, text: str, collectors: Dict[str, List]) -> None:
        """Extract statistics from workload stats file"""
        
        # Throughput
        throughput = DataTransformService.extract_numeric_value(
            text, cls.STATS_PATTERNS['throughput'], int
        )
        if throughput:
            collectors['throughputs'].append(throughput)
        
        # Cache percentages
        for cache_type in ['cache', 'ext_cache', 'disk', 'bamboo_ssd']:
            percentage = DataTransformService.extract_numeric_value(
                text, cls.STATS_PATTERNS[cache_type], int
            )
            if percentage is not None:
                collectors[f'{cache_type}_percentages'].append(percentage)
    
    @classmethod
    def _extract_system_stats(cls, text: str, collectors: Dict[str, List]) -> None:
        """Extract statistics from system stats file"""
        
        cpu_busy = DataTransformService.extract_numeric_value(
            text, cls.STATS_PATTERNS['cpu_busy'], float
        )
        if cpu_busy is not None:
            collectors['cpu_busy'].append(cpu_busy)
    
    @classmethod
    def _extract_wafl_stats(cls, text: str, collectors: Dict[str, List]) -> None:
        """Extract statistics from WAFL stats file"""
        
        # RDMA latency
        rdma_latency = DataTransformService.extract_numeric_value(
            text, cls.STATS_PATTERNS['rdma_latency'], float
        )
        if rdma_latency is not None:
            collectors['rdma_stats'].append(rdma_latency)
        
        # LDMA latency
        ldma_latency = DataTransformService.extract_numeric_value(
            text, cls.STATS_PATTERNS['ldma_latency'], float
        )
        if ldma_latency is not None:
            collectors['ldma_stats'].append(ldma_latency)
    
    @classmethod
    def _extract_instance_type(cls, year_month: str, run_id: str, link: str) -> Optional[str]:
        """Extract instance type from VM instance file"""
        
        vm_text = ExternalAPIService.fetch_stats_file(
            year_month, run_id, link, cls.STATS_FILE_TYPES['vm_instance']
        )
        
        if vm_text:
            match = re.search(cls.STATS_PATTERNS['instance_type'], vm_text)
            if match:
                return match.group(1).strip()
        
        return None
    
    @classmethod
    def _calculate_final_stats(cls, collectors: Dict[str, List], instance_type: Optional[str]) -> Dict[str, Any]:
        """Calculate final statistics from collected data"""
        
        stats_data = {}
        
        # Calculate maximums
        if collectors['throughputs']:
            stats_data['Maximum Throughput'] = max(collectors['throughputs']) / (1024 * 1024)
        
        if collectors['cache_percentages']:
            stats_data['Maximum Cache Percentage'] = max(collectors['cache_percentages'])
        
        if collectors['ext_cache_percentages']:
            stats_data['Maximum External Cache Percentage'] = max(collectors['ext_cache_percentages'])
        
        if collectors['disk_percentages']:
            stats_data['Maximum Disk Percentage'] = max(collectors['disk_percentages'])
        
        if collectors['bamboo_ssd_percentages']:
            stats_data['Maximum Bamboo SSD Percentage'] = max(collectors['bamboo_ssd_percentages'])
        
        if collectors['cpu_busy']:
            stats_data['Maximum System CPU Busy'] = max(collectors['cpu_busy'])
        
        if collectors['rdma_stats']:
            stats_data['Maximum WAFL RDMA Write Latency'] = max(collectors['rdma_stats'])
        
        if collectors['ldma_stats']:
            stats_data['Maximum WAFL LDMA Write Latency'] = max(collectors['ldma_stats'])
        
        if instance_type:
            stats_data['Instance Type'] = instance_type
        
        return stats_data


class GraphDataService:
    """Service for processing graph data"""
    
    GRAPH_PATTERNS = {
        'latency': r'latency:(\d+\.\d+)us',
        'ops': r'ops:(\d+)/s',
        'throughput': r'write_data:(\d+)b/s'
    }
    
    @classmethod
    def fetch_graph_data(cls, run_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch graph data for a run ID
        
        Args:
            run_id: The run ID to fetch graph data for
            
        Returns:
            List of data points or None if no data available
        """
        year_month = run_id[:4]
        links = ExternalAPIService.fetch_perfweb_links(run_id)
        
        if not links:
            return None
        
        graph_data = []
        
        for link in links:
            stats_text = ExternalAPIService.fetch_stats_file(
                year_month, run_id, link, 'stats_workload.txt'
            )
            
            if stats_text:
                data_point = cls._extract_graph_point(stats_text)
                if data_point:
                    graph_data.append(data_point)
        
        return graph_data if graph_data else None
    
    @classmethod
    def _extract_graph_point(cls, stats_text: str) -> Optional[Dict[str, Any]]:
        """Extract a single graph data point from stats text"""
        
        latency = DataTransformService.extract_numeric_value(
            stats_text, cls.GRAPH_PATTERNS['latency'], float
        )
        ops = DataTransformService.extract_numeric_value(
            stats_text, cls.GRAPH_PATTERNS['ops'], int
        )
        throughput = DataTransformService.extract_numeric_value(
            stats_text, cls.GRAPH_PATTERNS['throughput'], int
        )
        
        if latency and ops and throughput:
            return {
                'latency': latency,
                'ops': ops,
                'throughput': throughput
            }
        
        return None
