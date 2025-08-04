from django.urls import path
from .views import FetchDetailsView, FetchGraphDataView, CacheStatusView, CacheManagementView, FetchMultipleRunsView

urlpatterns = [
    path('fetch-details/', FetchDetailsView.as_view(), name='fetch-details'),
    path('fetch-graph-data/', FetchGraphDataView.as_view(), name='fetch-graph-data'),
    path('fetch-multiple-runs/', FetchMultipleRunsView.as_view(), name='fetch-multiple-runs'),
    path('cache-status/', CacheStatusView.as_view(), name='cache-status'),
    path('cache-management/', CacheManagementView.as_view(), name='cache-management'),
]
