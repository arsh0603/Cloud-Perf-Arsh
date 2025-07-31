"""
Run data service
Handles fetching and processing of run data with caching
"""
from typing import Dict, Any, Optional
from ..cache_manager import api_cache
from .api_service import ExternalAPIService, DataTransformService, CompatibilityService
from .stats_service import StatsProcessingService, GraphDataService


class RunDataService:
    """Service for managing run data operations"""
    
    @classmethod
    def fetch_single_run_data(cls, run_id: str, include_stats: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive data for a single run
        
        Args:
            run_id: The run ID to fetch
            include_stats: Whether to include detailed statistics
            
        Returns:
            Complete run data or None if not found
        """
        # Check cache first
        cache_key = f"details_{run_id}"
        cached_data = api_cache.get(cache_key)
        if cached_data:
            print(f"Found details data in memory cache for {run_id}")
            return cached_data
        
        # Fetch from external API
        print(f"Fetching details data from external API for {run_id}")
        
        try:
            # Get basic run details
            raw_data = ExternalAPIService.fetch_run_details(run_id)
            if not raw_data:
                return None
            
            # Transform to user-friendly format
            run_data = DataTransformService.transform_run_data(raw_data)
            
            # Add detailed statistics if requested
            if include_stats:
                try:
                    stats_data = StatsProcessingService.fetch_comprehensive_stats(run_id)
                    run_data.update(stats_data)
                except Exception as e:
                    print(f"Error fetching stats data for {run_id}: {e}")
                    run_data['stats_error'] = f"Could not fetch stats data: {str(e)}"
            
            # Cache the result
            api_cache.put(cache_key, run_data)
            
            print(f"Fetched data for {run_id}: {run_data}")
            return run_data
            
        except Exception as e:
            raise Exception(f"Error fetching data for {run_id}: {str(e)}")
    
    @classmethod
    def fetch_comparison_data(cls, id1: str, id2: str) -> Dict[str, Any]:
        """
        Fetch data for two runs and check compatibility
        
        Args:
            id1: First run ID
            id2: Second run ID
            
        Returns:
            Dictionary containing both runs' data and compatibility info
        """
        result = {}
        
        # Fetch data for both runs
        try:
            data1 = cls.fetch_single_run_data(id1)
            if data1:
                result['id1'] = data1
            else:
                result['error_id1'] = f'ID 1: {id1} is incorrect.'
        except Exception as e:
            result['error_id1'] = f'Error fetching ID 1: {str(e)}'
        
        try:
            data2 = cls.fetch_single_run_data(id2)
            if data2:
                result['id2'] = data2
            else:
                result['error_id2'] = f'ID 2: {id2} is incorrect.'
        except Exception as e:
            result['error_id2'] = f'Error fetching ID 2: {str(e)}'
        
        # Check compatibility if both runs were fetched successfully
        if 'id1' in result and 'id2' in result:
            compatibility = CompatibilityService.check_workload_compatibility(
                result['id1'], result['id2']
            )
            
            if not compatibility['compatible']:
                result['comparison_error'] = {
                    'message': compatibility['message'],
                    'error_type': compatibility['error_type'],
                    'comparison_allowed': False
                }
                
                if compatibility['error_type'] == 'workload':
                    result['comparison_error'].update({
                        'workload_id1': compatibility['workload1'],
                        'workload_id2': compatibility['workload2']
                    })
                elif compatibility['error_type'] == 'model':
                    result['comparison_error'].update({
                        'model_id1': compatibility['model1'],
                        'model_id2': compatibility['model2']
                    })
            else:
                result['comparison_allowed'] = True
        
        return result
    
    @classmethod
    def fetch_multiple_runs_data(cls, run_ids: list, max_runs: int = 50) -> Dict[str, Any]:
        """
        Fetch data for multiple run IDs
        
        Args:
            run_ids: List of run IDs to fetch
            max_runs: Maximum number of runs to process
            
        Returns:
            Dictionary containing results and errors
        """
        if len(run_ids) > max_runs:
            raise ValueError(f'Maximum {max_runs} IDs allowed per request')
        
        # Validate IDs
        invalid_ids = [id for id in run_ids if len(id) != 9]
        if invalid_ids:
            raise ValueError(f'All IDs must be exactly 9 characters long. Invalid IDs: {invalid_ids}')
        
        results = {}
        errors = {}
        
        for run_id in run_ids:
            try:
                data = cls.fetch_single_run_data(run_id)
                if data:
                    # Add perfweb link
                    year_month = run_id[:4]
                    data['Perfweb Link'] = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/cloud_test_harness.log'
                    results[run_id] = data
                else:
                    errors[run_id] = "No data available for this ID"
            except Exception as e:
                errors[run_id] = str(e)
        
        return {
            'success_count': len(results),
            'error_count': len(errors),
            'total_requested': len(run_ids),
            'results': results,
            'errors': errors if errors else None
        }


class GraphDataManagerService:
    """Service for managing graph data operations"""
    
    @classmethod
    def fetch_single_graph_data(cls, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch graph data for a single run with caching
        
        Args:
            run_id: The run ID to fetch graph data for
            
        Returns:
            Graph data or None if not available
        """
        cache_key = f"graph_{run_id}"
        
        # Check cache first
        cached_data = api_cache.get(cache_key)
        if cached_data:
            print(f"Found graph data in memory cache for {run_id}")
            return {run_id: cached_data}
        
        # Fetch from external sources
        print(f"Fetching graph data from external API for {run_id}")
        
        try:
            graph_data = GraphDataService.fetch_graph_data(run_id)
            if graph_data:
                # Cache the result
                api_cache.put(cache_key, graph_data)
                return {run_id: graph_data}
            else:
                print(f"No graph data found for {run_id}")
                return None
                
        except Exception as e:
            print(f"Error fetching graph data for {run_id}: {e}")
            return None
    
    @classmethod
    def fetch_comparison_graph_data(cls, run_id1: str, run_id2: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch graph data for one or two runs
        
        Args:
            run_id1: First run ID (required)
            run_id2: Second run ID (optional)
            
        Returns:
            Dictionary containing graph data and metadata
        """
        data_points = {}
        missing_data_messages = []
        
        # Fetch data for first run
        graph_data1 = cls.fetch_single_graph_data(run_id1)
        if graph_data1:
            data_points.update(graph_data1)
        else:
            missing_data_messages.append(f"No graph data available for run ID: {run_id1}")
        
        # Fetch data for second run if provided
        if run_id2:
            graph_data2 = cls.fetch_single_graph_data(run_id2)
            if graph_data2:
                data_points.update(graph_data2)
            else:
                missing_data_messages.append(f"No graph data available for run ID: {run_id2}")
        
        # Prepare response
        response_data = {'data_points': data_points}
        
        if missing_data_messages:
            response_data['missing_data'] = missing_data_messages
        
        # Check compatibility if both runs have data
        if run_id1 and run_id2 and run_id1 in data_points and run_id2 in data_points:
            compatibility = cls._check_graph_compatibility(run_id1, run_id2)
            if not compatibility['compatible']:
                return {
                    'error': f"Cannot generate graph comparison for runs with different {compatibility['error_type']} types",
                    'message': f"{compatibility['error_type'].title()} types must be identical for meaningful comparison",
                    'error_type': compatibility['error_type'],
                    **compatibility
                }
        
        return response_data
    
    @classmethod
    def _check_graph_compatibility(cls, run_id1: str, run_id2: str) -> Dict[str, Any]:
        """Check compatibility between two runs for graph comparison"""
        
        try:
            # Get basic run details for compatibility check
            data1 = ExternalAPIService.fetch_run_details(run_id1, 'workload,model')
            data2 = ExternalAPIService.fetch_run_details(run_id2, 'workload,model')
            
            if data1 and data2:
                workload1 = data1.get('workload')
                workload2 = data2.get('workload')
                model1 = data1.get('model')
                model2 = data2.get('model')
                
                # Check workload compatibility
                if workload1 != workload2:
                    return {
                        'compatible': False,
                        'workload_id1': workload1,
                        'workload_id2': workload2,
                        'model_id1': model1,
                        'model_id2': model2,
                        'error_type': 'workload'
                    }
                
                # Check model compatibility
                if model1 != model2:
                    return {
                        'compatible': False,
                        'workload_id1': workload1,
                        'workload_id2': workload2,
                        'model_id1': model1,
                        'model_id2': model2,
                        'error_type': 'model'
                    }
                
                return {
                    'compatible': True,
                    'workload_id1': workload1,
                    'workload_id2': workload2,
                    'model_id1': model1,
                    'model_id2': model2
                }
            
        except Exception as e:
            print(f"Error checking compatibility: {e}")
        
        # If error occurs or data unavailable, allow comparison
        return {
            'compatible': True,
            'workload_id1': 'Unknown',
            'workload_id2': 'Unknown',
            'model_id1': 'Unknown',
            'model_id2': 'Unknown'
        }
