import React from 'react';

const ModeSelector = ({ mode, onModeChange }) => {
  return (
    <div className="dashboard-card">
      <h3 className="card-title">Analysis Mode</h3>
      <div className="mode-toggle">
        <button 
          className={`mode-btn ${mode === 'single' ? 'active' : ''}`}
          onClick={() => onModeChange('single')}
        >
          Single Run Analysis
        </button>
        <button 
          className={`mode-btn ${mode === 'compare' ? 'active' : ''}`}
          onClick={() => onModeChange('compare')}
        >
          Compare Runs
        </button>
      </div>
    </div>
  );
};

export default ModeSelector;
