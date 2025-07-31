import React from 'react';

const LoadingIndicator = ({ isLoadingGraph1, isLoadingGraph2, isLoadingGraph }) => {
  if (!isLoadingGraph1 && !isLoadingGraph2 && !isLoadingGraph) {
    return null;
  }

  return (
    <div className="loading-indicator">
      <span className="loading-spinner"></span>
      <div>Processing performance data...</div>
      <div style={{ fontSize: '0.875rem', color: '#9ca3af', marginTop: '0.5rem' }}>
        This may take a moment while analyzing the run data
      </div>
    </div>
  );
};

export default LoadingIndicator;
