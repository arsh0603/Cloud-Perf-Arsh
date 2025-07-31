import React from 'react';

const SystemStatus = ({ cacheStatus }) => {
  return (
    <div className="dashboard-card">
      <h3 className="card-title">System Status</h3>
      {cacheStatus ? (
        <div className="status-grid">
          <div className="status-card">
            <h5>Memory Cache</h5>
            <p><strong>Items:</strong> {cacheStatus.memory_cache?.size || 0}/{cacheStatus.memory_cache?.max_size || 20}</p>
            <p><strong>Details:</strong> {cacheStatus.memory_cache?.details_keys?.length || 0} entries</p>
            <p><strong>Graphs:</strong> {cacheStatus.memory_cache?.graph_keys?.length || 0} entries</p>
            {cacheStatus.memory_cache?.access_order?.length > 0 && (
              <p style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                <strong>Recent:</strong> {cacheStatus.memory_cache.access_order.slice(-3).join(', ')}
              </p>
            )}
          </div>
        </div>
      ) : (
        <div className="loading-indicator">
          <span className="loading-spinner"></span>
          Loading system status...
        </div>
      )}
    </div>
  );
};

export default SystemStatus;
