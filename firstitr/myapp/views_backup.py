from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import (
    ExternalAPIService, 
    DataTransformService, 
    CompatibilityService,
    StatsProcessingService,
    RunDataService
)
from .cache_manager import api_cache

class FetchDetailsView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_service = ExternalAPIService()
        self.transform_service = DataTransformService()
        self.compatibility_service = CompatibilityService()
        self.run_service = RunDataService()
        
    def get(self, request):
        id1 = request.GET.get('id1') or request.GET.get('id')  # Support both id1 and id parameters
        id2 = request.GET.get('id2')
        
        if not id1:
            return JsonResponse({'error': 'id1 or id parameter is required'}, status=400)
        
        try:
            if id2:
                # Comparison mode
                result = self._fetch_comparison_data(id1, id2)
            else:
                # Single mode
                result = self._fetch_single_data(id1)
            
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _fetch_single_data(self, run_id):
        """Fetch data for a single run using services"""
        data = self.run_service.fetch_single_run_with_cache(run_id)
        if not data:
            raise Exception(f'ID {run_id} is incorrect.')
        return data
    
    def _fetch_comparison_data(self, id1, id2):
        """Fetch data for comparison using services"""
        combined_data = {}
        
        try:
            data1 = self.run_service.fetch_single_run_with_cache(id1)
            if data1:
                combined_data['id1'] = data1
            else:
                combined_data['error_id1'] = f'ID 1: {id1} is incorrect.'
        except Exception as e:
            combined_data['error_id1'] = f'Error fetching ID 1: {str(e)}'
        
        try:
            data2 = self.run_service.fetch_single_run_with_cache(id2)
            if data2:
                combined_data['id2'] = data2
            else:
                combined_data['error_id2'] = f'ID 2: {id2} is incorrect.'
        except Exception as e:
            combined_data['error_id2'] = f'Error fetching ID 2: {str(e)}'
        
        # Check compatibility
        combined_data = self.compatibility_service.validate_workload_compatibility(combined_data)
        
        return combined_data
    
    def _fetch_single_run_with_cache(self, run_id):
        """Fetch data for a single run ID with caching (similar to FetchSingleDetailsView)"""
        cache_key = f"details_{run_id}"
        cached_data = api_cache.get(cache_key)
        if cached_data:
            print(f"Found details data in memory cache for {run_id}")
            return cached_data
        
        print(f"Fetching details data from external API for {run_id}")
        api_url = f'http://grover.rtp.netapp.com/KO/rest/api/Runs/{run_id}?req_fields=workload,peak_iter,ontap_ver,peak_ops,model,peak_lat'
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('workload') == 0:
                return None  
            
            renamed_data = {
                'Workload Type': data.get('workload'),
                'Peak Iteration': data.get('peak_iter'),
                'ONTAP version': data.get('ontap_ver'),
                'Achieved Ops': data.get('peak_ops'),
                'Model': data.get('model'),
                'Peak Latency': data.get('peak_lat'),
            }

            try:
                stats_data = self.fetch_stats_data(run_id)
                renamed_data.update(stats_data)
            except Exception as e:
                print(f"Error fetching stats data: {e}")
                renamed_data['stats_error'] = f"Could not fetch stats data: {str(e)}"
            finally:
                api_cache.put(cache_key, renamed_data)

            print(f"Fetched data for {run_id}: {renamed_data}")
            return renamed_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    
    def _validate_workload_compatibility(self, combined_data):
        """Check if workloads and models are compatible for comparison"""
        if 'id1' in combined_data and 'id2' in combined_data:
            workload1 = combined_data['id1'].get('Workload Type')
            workload2 = combined_data['id2'].get('Workload Type')
            model1 = combined_data['id1'].get('Model')
            model2 = combined_data['id2'].get('Model')
            
            if workload1 and workload2 and workload1 != workload2:
                combined_data['comparison_error'] = {
                    'message': 'Cannot compare runs with different workload types',
                    'workload_id1': workload1,
                    'workload_id2': workload2,
                    'comparison_allowed': False,
                    'error_type': 'workload'
                }
            elif model1 and model2 and model1 != model2:
                combined_data['comparison_error'] = {
                    'message': 'Cannot compare runs with different model types',
                    'model_id1': model1,
                    'model_id2': model2,
                    'comparison_allowed': False,
                    'error_type': 'model'
                }
            else:
                combined_data['comparison_allowed'] = True
        
        return combined_data
    
    def fetch_stats_data(self, run_id):

        stats_data = {}
        
        year_month = run_id[:4]
        base_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/testdirview.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output'
        
        try:
            response = requests.get(base_url, timeout=15)
            if response.ok:
                text = response.text
                links = re.findall(r'href="(testdirview.cgi\?p=/x/eng/perfcloud/RESULTS/[^"]+/ontap_command_output/\d+_[^"]+)"', text)
                
                all_throughputs = []
                all_cache_percentages = []
                all_ext_cache_percentages = []
                all_disk_percentages = []
                all_bamboo_ssd_percentages = []
                all_rdma_stats = []
                all_ldma_stats = []
                all_cpu_busy = []
                instance_type = None  
                
                for link in links:
                    stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_workload.txt'
                    stats_response = requests.get(stats_url, timeout=10)
                    
                    if stats_response.ok:
                        stats_text = stats_response.text
                        
                        throughput_match = re.search(r'write_data:(\d+)b/s', stats_text)
                        if throughput_match:
                            all_throughputs.append(int(throughput_match.group(1)))
                        
                        cache_match = re.search(r'read_io_type\.cache:(\d+)%', stats_text)
                        if cache_match:
                            all_cache_percentages.append(int(cache_match.group(1)))
                        
                        ext_cache_match = re.search(r'read_io_type\.ext_cache:(\d+)%', stats_text)
                        if ext_cache_match:
                            all_ext_cache_percentages.append(int(ext_cache_match.group(1)))
                        
                        disk_match = re.search(r'read_io_type\.disk:(\d+)%', stats_text)
                        if disk_match:
                            all_disk_percentages.append(int(disk_match.group(1)))
                        
                        bamboo_ssd_match = re.search(r'read_io_type\.bamboo_ssd:(\d+)%', stats_text)
                        if bamboo_ssd_match:
                            all_bamboo_ssd_percentages.append(int(bamboo_ssd_match.group(1)))
                    
                    system_stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_system.txt'
                    system_stats_response = requests.get(system_stats_url, timeout=10)
                    
                    if system_stats_response.ok:
                        system_stats_text = system_stats_response.text
                        
                        cpu_match = re.search(r'cpu_busy:(\d+(?:\.\d+)?)%', system_stats_text)
                        if cpu_match:
                            all_cpu_busy.append(float(cpu_match.group(1)))

                    vm_instance_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/system_node_virtual_machine_instance_show.txt'
                    vm_instance_response = requests.get(vm_instance_url, timeout=10)

                    if vm_instance_response.ok:
                        vm_instance_text = vm_instance_response.text

                        if instance_type is None:
                            instance_type_match = re.search(r'Instance Type:\s*([^\n\r]+)', vm_instance_text)
                            if instance_type_match:
                                instance_type = instance_type_match.group(1).strip()
                    
                    write_stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_wafl_flexlog.txt'
                    write_stats_response = requests.get(write_stats_url, timeout=10)

                    if write_stats_response.ok:
                        write_stats_text = write_stats_response.text

                        rdma_latency_match = re.search(r'rdma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us', write_stats_text)
                        if rdma_latency_match:
                            all_rdma_stats.append(float(rdma_latency_match.group(1)))
                        
                        ldma_latency_match = re.search(r'ldma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us', write_stats_text)
                        if ldma_latency_match:
                            all_ldma_stats.append(float(ldma_latency_match.group(1)))


                if all_throughputs:
                    stats_data['Maximum Throughput'] = max(all_throughputs) / (1024 * 1024)
                
                if all_cache_percentages:
                    stats_data['Maximum Cache Percentage'] = max(all_cache_percentages)

                if all_ext_cache_percentages:
                    stats_data['Maximum External Cache Percentage'] = max(all_ext_cache_percentages)

                if all_disk_percentages:
                    stats_data['Maximum Disk Percentage'] = max(all_disk_percentages)
                
                if all_bamboo_ssd_percentages:
                    stats_data['Maximum Bamboo SSD Percentage'] = max(all_bamboo_ssd_percentages)

                if all_cpu_busy:
                    stats_data['Maximum System CPU Busy'] = max(all_cpu_busy)

                if all_rdma_stats:
                    stats_data['Maximum WAFL RDMA Write Latency'] = max(all_rdma_stats)

                if all_ldma_stats:
                    stats_data['Maximum WAFL LDMA Write Latency'] = max(all_ldma_stats)

                if instance_type:
                    stats_data['Instance Type'] = instance_type
                                    
        except Exception as e:
            print(f"Error fetching stats data: {e}")
            raise e
        
        return stats_data
    
class FetchGraphDataView(View):
    def get(self, request):
        run_id1 = request.GET.get('run_id1')
        run_id2 = request.GET.get('run_id2')
        
        if not run_id1:
            return JsonResponse({'error': 'run_id1 parameter is required'}, status=400)

        data_points = {}
        
        cache_key1 = f"graph_{run_id1}"
        cached_graph1 = api_cache.get(cache_key1)
        
        if cached_graph1:
            print(f"Found graph data in memory cache for {run_id1}")
            data_points[run_id1] = cached_graph1
        else:
            print(f"Fetching graph data from external API for {run_id1}")
            graph_data1 = self._fetch_graph_data_for_id(run_id1)
            if graph_data1:
                data_points[run_id1] = graph_data1
                api_cache.put(cache_key1, graph_data1)
            else:
                print(f"No graph data found for {run_id1}")

        if run_id2:
            cache_key2 = f"graph_{run_id2}"
            cached_graph2 = api_cache.get(cache_key2)
            
            if cached_graph2:
                print(f"Found graph data in memory cache for {run_id2}")
                data_points[run_id2] = cached_graph2
            else:
                print(f"Fetching graph data from external API for {run_id2}")
                graph_data2 = self._fetch_graph_data_for_id(run_id2)
                if graph_data2:
                    data_points[run_id2] = graph_data2
                    api_cache.put(cache_key2, graph_data2)
                else:
                    print(f"No graph data found for {run_id2}")

        if not data_points:
            return JsonResponse({'error': 'No graph data found for any of the provided run IDs'}, status=404)

        response_data = {'data_points': data_points}
        
        missing_data_messages = []
        if run_id1 and run_id1 not in data_points:
            missing_data_messages.append(f"No graph data available for run ID: {run_id1}")
        if run_id2 and run_id2 not in data_points:
            missing_data_messages.append(f"No graph data available for run ID: {run_id2}")
        
        if missing_data_messages:
            response_data['missing_data'] = missing_data_messages

        if run_id1 and run_id2 and run_id1 in data_points and run_id2 in data_points:
            compatibility_check = self._check_workload_compatibility(run_id1, run_id2)
            if not compatibility_check['compatible']:
                if compatibility_check.get('error_type') == 'workload':
                    return JsonResponse({
                        'error': 'Cannot generate graph comparison for runs with different workload types',
                        'workload_id1': compatibility_check['workload1'],
                        'workload_id2': compatibility_check['workload2'],
                        'message': 'Workload types must be identical for meaningful comparison',
                        'error_type': 'workload'
                    }, status=400)
                elif compatibility_check.get('error_type') == 'model':
                    return JsonResponse({
                        'error': 'Cannot generate graph comparison for runs with different model types',
                        'model_id1': compatibility_check['model1'],
                        'model_id2': compatibility_check['model2'],
                        'message': 'Model types must be identical for meaningful comparison',
                        'error_type': 'model'
                    }, status=400)

        print(f"Data points collected: {data_points}")
        return JsonResponse(response_data, safe=False)
    
    def _fetch_graph_data_for_id(self, run_id):
        """Helper method to fetch graph data for a single run ID"""
        try:
            year_month = run_id[:4]  
            base_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/testdirview.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output'

            response = requests.get(base_url)
            response.raise_for_status()
            text = response.text
            
            print(f"Response text length for {run_id}: {len(text)}")

            links = re.findall(r'href="(testdirview.cgi\?p=/x/eng/perfcloud/RESULTS/[^"]+/ontap_command_output/\d+_[^"]+)"', text)
            
            print(f"Number of iteration links found for {run_id}: {len(links)}")
            
            graph_data = []
            
            for link in links:
                stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_workload.txt'
                stats_response = requests.get(stats_url)
                if stats_response.ok:
                    stats_text = stats_response.text
                    latency_match = re.search(r'latency:(\d+\.\d+)us', stats_text)
                    ops_match = re.search(r'ops:(\d+)/s', stats_text)
                    throughput_match = re.search(r'write_data:(\d+)b/s', stats_text)
                    if latency_match and ops_match and throughput_match:
                        graph_data.append({
                            'latency': float(latency_match.group(1)),
                            'ops': int(ops_match.group(1)),
                            'throughput': int(throughput_match.group(1)),
                        })
            
            return graph_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching graph data for {run_id}: {e}")
            return None

    def _check_workload_compatibility(self, run_id1, run_id2):
        """Check if two run IDs have compatible workload types and models"""
        try:
            api_url_template = 'http://grover.rtp.netapp.com/KO/rest/api/Runs/{}?req_fields=workload,model'
            
            response1 = requests.get(api_url_template.format(run_id1), timeout=10)
            response2 = requests.get(api_url_template.format(run_id2), timeout=10)
            
            if response1.ok and response2.ok:
                data1 = response1.json()
                data2 = response2.json()
                
                workload1 = data1.get('workload')
                workload2 = data2.get('workload')
                model1 = data1.get('model')
                model2 = data2.get('model')
                
                if workload1 != workload2:
                    return {
                        'compatible': False,
                        'workload1': workload1,
                        'workload2': workload2,
                        'model1': model1,
                        'model2': model2,
                        'error_type': 'workload',
                        'message': 'Cannot compare runs with different workload types'
                    }
                elif model1 != model2:
                    return {
                        'compatible': False,
                        'workload1': workload1,
                        'workload2': workload2,
                        'model1': model1,
                        'model2': model2,
                        'error_type': 'model',
                        'message': 'Cannot compare runs with different model types'
                    }
                else:
                    return {
                        'compatible': True,
                        'workload1': workload1,
                        'workload2': workload2,
                        'model1': model1,
                        'model2': model2
                    }
            else:
                return {
                    'compatible': True,
                    'workload1': 'Unknown',
                    'workload2': 'Unknown',
                    'model1': 'Unknown',
                    'model2': 'Unknown'
                }
        except Exception as e:
            print(f"Error checking workload compatibility: {e}")
            return {
                'compatible': True,
                'workload1': 'Unknown',
                'workload2': 'Unknown'
            }
    


@method_decorator(csrf_exempt, name='dispatch')
class CacheManagementView(View):
    def get(self, request):
        """Get cache status for memory cache only"""
        memory_cache_status = api_cache.get_status()
        
        return JsonResponse({'memory_cache': memory_cache_status}, safe=False)
    
    def delete(self, request):
        """Clear memory cache"""
        api_cache.clear()
        
        return JsonResponse({
            'message': 'Memory cache cleared successfully',
            'memory_cache_cleared': True
        }, safe=False)

class FetchMultipleRunsView(View):
    """
    API endpoint to fetch data for multiple run IDs provided in comma-separated format
    Usage: /api/fetch-multiple-runs/?ids=250725hbn,250726xyz,250727abc
    """
    def get(self, request):
        ids_param = request.GET.get('ids')
        
        if not ids_param:
            return JsonResponse({'error': 'ids parameter is required (comma-separated)'}, status=400)
        
        run_ids = [id.strip() for id in ids_param.split(',') if id.strip()]
        
        if not run_ids:
            return JsonResponse({'error': 'No valid IDs provided'}, status=400)
        
        invalid_ids = [id for id in run_ids if len(id) != 9]
        if invalid_ids:
            return JsonResponse({
                'error': f'All IDs must be exactly 9 characters long. Invalid IDs: {invalid_ids}'
            }, status=400)
        
        if len(run_ids) > 50:
            return JsonResponse({'error': 'Maximum 50 IDs allowed per request'}, status=400)
        
        results = {}
        errors = {}
        
        for run_id in run_ids:
            try:
                data = self._fetch_single_run_data(run_id)
                if data:
                    results[run_id] = data
                else:
                    errors[run_id] = "No data available for this ID"
            except Exception as e:
                errors[run_id] = str(e)
        
        response_data = {
            'success_count': len(results),
            'error_count': len(errors),
            'total_requested': len(run_ids),
            'results': results
        }
        
        if errors:
            response_data['errors'] = errors
        
        return JsonResponse(response_data, safe=False)
    
    def _fetch_single_run_data(self, run_id):
        """Fetch data for a single run ID with caching"""
        cache_key = f"details_{run_id}"
        cached_data = api_cache.get(cache_key)
        if cached_data:
            print(f"Found details data in memory cache for {run_id}")
            return cached_data
        
        print(f"Fetching details data from external API for {run_id}")
        api_url = f'http://grover.rtp.netapp.com/KO/rest/api/Runs/{run_id}?req_fields=workload,peak_iter,ontap_ver,peak_ops,peak_lat,model'
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('workload') == 0:
                raise Exception(f'ID {run_id} is incorrect or not found')
            
            renamed_data = {
                'Workload Type': data.get('workload'),
                'Peak Iteration': data.get('peak_iter'),
                'ONTAP version': data.get('ontap_ver'),
                'Achieved Ops': data.get('peak_ops'),
                'Peak Latency': data.get('peak_lat'),
                'Model': data.get('model')
            }
            
            print(f"Fetched data for {run_id}: {renamed_data}")
            year_month = run_id[:4]
            renamed_data['Perfweb Link'] = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/cloud_test_harness.log'
            
            try:
                stats_data = self._fetch_stats_data(run_id)
                renamed_data.update(stats_data)
            except Exception as e:
                print(f"Error fetching stats data for {run_id}: {e}")
                renamed_data['stats_error'] = f"Could not fetch stats data: {str(e)}"
            
            api_cache.put(cache_key, renamed_data)
            
            return renamed_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error fetching data for {run_id}: {str(e)}")
    
    def _fetch_stats_data(self, run_id):
        """Fetch stats data for a single run ID"""
        stats_data = {}
        
        year_month = run_id[:4]
        base_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/testdirview.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output'
        
        try:
            response = requests.get(base_url, timeout=15)
            if response.ok:
                text = response.text
                links = re.findall(r'href="(testdirview.cgi\?p=/x/eng/perfcloud/RESULTS/[^"]+/ontap_command_output/\d+_[^"]+)"', text)
                
                all_throughputs = []
                all_cache_percentages = []
                all_ext_cache_percentages = []
                all_disk_percentages = []
                all_bamboo_ssd_percentages = []
                all_rdma_stats = []
                all_ldma_stats = []
                all_cpu_busy = []
                instance_type = None
                
                for link in links:
                    stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_workload.txt'
                    stats_response = requests.get(stats_url, timeout=10)
                    
                    if stats_response.ok:
                        stats_text = stats_response.text
                        
                        throughput_match = re.search(r'write_data:(\d+)b/s', stats_text)
                        if throughput_match:
                            all_throughputs.append(int(throughput_match.group(1)))
                        
                        cache_match = re.search(r'read_io_type\.cache:(\d+)%', stats_text)
                        if cache_match:
                            all_cache_percentages.append(int(cache_match.group(1)))
                        
                        ext_cache_match = re.search(r'read_io_type\.ext_cache:(\d+)%', stats_text)
                        if ext_cache_match:
                            all_ext_cache_percentages.append(int(ext_cache_match.group(1)))
                        
                        disk_match = re.search(r'read_io_type\.disk:(\d+)%', stats_text)
                        if disk_match:
                            all_disk_percentages.append(int(disk_match.group(1)))
                        
                        bamboo_ssd_match = re.search(r'read_io_type\.bamboo_ssd:(\d+)%', stats_text)
                        if bamboo_ssd_match:
                            all_bamboo_ssd_percentages.append(int(bamboo_ssd_match.group(1)))
                    
                    system_stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_system.txt'
                    system_stats_response = requests.get(system_stats_url, timeout=10)
                    
                    if system_stats_response.ok:
                        system_stats_text = system_stats_response.text
                        
                        cpu_match = re.search(r'cpu_busy:(\d+(?:\.\d+)?)%', system_stats_text)
                        if cpu_match:
                            all_cpu_busy.append(float(cpu_match.group(1)))

                    vm_instance_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/system_node_virtual_machine_instance_show.txt'
                    vm_instance_response = requests.get(vm_instance_url, timeout=10)

                    if vm_instance_response.ok:
                        vm_instance_text = vm_instance_response.text

                        if instance_type is None:
                            instance_type_match = re.search(r'Instance Type:\s*([^\n\r]+)', vm_instance_text)
                            if instance_type_match:
                                instance_type = instance_type_match.group(1).strip()
                    
                    write_stats_url = f'http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/{year_month}/{run_id}/ontap_command_output/{link.split("/")[-1]}/stats_wafl_flexlog.txt'
                    write_stats_response = requests.get(write_stats_url, timeout=10)

                    if write_stats_response.ok:
                        write_stats_text = write_stats_response.text

                        rdma_latency_match = re.search(r'rdma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us', write_stats_text)
                        if rdma_latency_match:
                            all_rdma_stats.append(float(rdma_latency_match.group(1)))
                        
                        ldma_latency_match = re.search(r'ldma_actual_latency\.WAFL_SPINNP_WRITE:(\d+(?:\.\d+)?)us', write_stats_text)
                        if ldma_latency_match:
                            all_ldma_stats.append(float(ldma_latency_match.group(1)))

                if all_throughputs:
                    stats_data['Maximum Throughput'] = max(all_throughputs) / (1024 * 1024)
                
                if all_cache_percentages:
                    stats_data['Maximum Cache Percentage'] = max(all_cache_percentages)

                if all_ext_cache_percentages:
                    stats_data['Maximum External Cache Percentage'] = max(all_ext_cache_percentages)

                if all_disk_percentages:
                    stats_data['Maximum Disk Percentage'] = max(all_disk_percentages)
                
                if all_bamboo_ssd_percentages:
                    stats_data['Maximum Bamboo SSD Percentage'] = max(all_bamboo_ssd_percentages)

                if all_cpu_busy:
                    stats_data['Maximum System CPU Busy'] = max(all_cpu_busy)

                if all_rdma_stats:
                    stats_data['Maximum WAFL RDMA Write Latency'] = max(all_rdma_stats)

                if all_ldma_stats:
                    stats_data['Maximum WAFL LDMA Write Latency'] = max(all_ldma_stats)

                if instance_type:
                    stats_data['Instance Type'] = instance_type
                                    
        except Exception as e:
            print(f"Error fetching stats data for {run_id}: {e}")
            raise e
        
        return stats_data

