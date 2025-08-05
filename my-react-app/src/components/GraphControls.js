import React from 'react';

const GraphControls = ({
  showThroughputInMB,
  onThroughputToggle
}) => {
  return (
    <div className="graph-controls inline">
      <div className="toggle-switch">
        <input
          type="checkbox"
          checked={showThroughputInMB}
          onChange={(e) => onThroughputToggle(e.target.checked)}
        />
        <span className="input-label">Show throughput in MB/s</span>
      </div>
      
      <div className="info-message">
        💡 Graphs auto-generate
      </div>
    </div>
  );
};

export default GraphControls;
