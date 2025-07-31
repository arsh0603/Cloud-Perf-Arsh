from django.urls import path
from .views import FetchDetailsView, FetchGraphDataView, CacheManagementView, FetchMultipleRunsView

urlpatterns = [
    path('fetch-details/', FetchDetailsView.as_view(), name='fetch_details'),
    path('fetch-graph-data/', FetchGraphDataView.as_view(), name='fetch_graph_data'),
    path('fetch-multiple-runs/', FetchMultipleRunsView.as_view(), name='fetch_multiple_runs'),
    path('cache-management/', CacheManagementView.as_view(), name='cache_management'),
]
