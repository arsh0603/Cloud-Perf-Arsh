import React from 'react';

const SystemStatus = ({ cacheStatus, onClearCache }) => {
  return (
    <div className="dashboard-card">
      <h3 className="card-title">System Status</h3>
      {cacheStatus ? (
        <div className="status-grid">
          <div className="status-card">
            <h5>Memory Cache</h5>
            <p><strong>Items:</strong> {cacheStatus.size || 0}/{cacheStatus.max_size || 20}</p>
            <p><strong>Details:</strong> {cacheStatus.details_keys?.length || 0} entries</p>
            <p><strong>Graphs:</strong> {cacheStatus.graph_keys?.length || 0} entries</p>
            {cacheStatus.access_order?.length > 0 && (
              <p style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                <strong>Recent:</strong> {cacheStatus.access_order.slice(-3).join(', ')}
              </p>
            )}
            {onClearCache && (
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={onClearCache}
                style={{ marginTop: '10px', fontSize: '0.8rem' }}
              >
                🗑️ Clear Cache
              </button>
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
