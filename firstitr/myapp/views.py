from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import (
    ExternalAPIService, 
    DataTransformService, 
    CompatibilityService,
    StatsProcessingService,
    RunDataService,
    GraphDataManagerService
)
from .cache_manager import api_cache

class FetchDetailsView(View):
    
    def get(self, request):
        id1 = request.GET.get('id1') or request.GET.get('id')  # Support both id1 and id parameters
        id2 = request.GET.get('id2')
        
        if not id1:
            return JsonResponse({'error': 'id1 or id parameter is required'}, status=400)
        
        try:
            if id2:
                # Comparison mode
                result = RunDataService.fetch_comparison_data(id1, id2)
            else:
                # Single mode
                result = RunDataService.fetch_single_run_data(id1)
                if not result:
                    return JsonResponse({'error': f'ID {id1} is incorrect.'}, status=400)
            
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class FetchGraphDataView(View):
    """Modular view using service classes for fetching graph data"""
    
    def get(self, request):
        id1 = request.GET.get('run_id1')
        id2 = request.GET.get('run_id2')
        
        if not id1:
            return JsonResponse({'error': 'run_id1 is required'}, status=400)
        
        try:
            if id2:
                # Comparison mode - fetch data for both runs
                result = GraphDataManagerService.fetch_comparison_graph_data(id1, id2)
            else:
                # Single mode - fetch data for one run
                result = GraphDataManagerService.fetch_single_graph_data(id1)
                print(result)
                if not result:
                    return JsonResponse({'error': f'No graph data found for run {id1}'}, status=404)
            
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CacheStatusView(View):
    """View for checking cache status"""
    
    def get(self, request):
        cache_status = api_cache.get_status()
        return JsonResponse(cache_status, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CacheManagementView(View):
    """View for managing cache operations"""
    
    def delete(self, request):
        api_cache.clear()
        return JsonResponse({'status': 'Cache cleared successfully'}, safe=False)


class FetchMultipleRunsView(View):
    """View for fetching multiple runs data using service classes"""
    
    def get(self, request):
        run_ids = request.GET.get('run_ids', '')
        
        if not run_ids:
            return JsonResponse({'error': 'run_ids parameter is required'}, status=400)
        
        try:
            run_ids_list = [rid.strip() for rid in run_ids.split(',') if rid.strip()]
            
            if len(run_ids_list) > 5:
                return JsonResponse({'error': 'Maximum 5 run IDs allowed'}, status=400)
            
            result = RunDataService.fetch_multiple_runs_data(run_ids_list)
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
