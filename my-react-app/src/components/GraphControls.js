import React from 'react';

const GraphControls = ({
  mode,
  id1,
  id2,
  showThroughputInMB,
  onThroughputToggle,
  onGraphSubmit,
  isLoadingGraph1,
  isLoadingGraph2,
  comparisonAllowed,
  disabledReason
}) => {
  return (
    <div className='dashboard-card' style={{ justifyContent: 'center' }}>
      <div className="graph-controls horizontal" style={{ flexDirection: 'column' }}>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={showThroughputInMB}
            onChange={(e) => onThroughputToggle(e.target.checked)}
          />
          <span className="input-label">Show throughput in MB/s</span>
        </div>
        
        <div className="btn-group horizontal-buttons">
          {mode === 'single' ? (
            <button 
              type="button" 
              className="btn btn-primary compact"
              onClick={() => onGraphSubmit(id1)}
              disabled={isLoadingGraph1}
            >
              {isLoadingGraph1 ? (
                <>
                  <span className="loading-spinner"></span>
                  Loading...
                </>
              ) : (
                '📊 Generate Graph'
              )}
            </button>
          ) : (
            <>
              <button 
                type="button" 
                className="btn btn-primary compact"
                onClick={() => onGraphSubmit(id1)}
                disabled={isLoadingGraph1}
              >
                {isLoadingGraph1 ? 'Loading...' : '📊 Graph ID1'}
              </button>
              <button 
                type="button" 
                className="btn btn-primary compact"
                onClick={() => onGraphSubmit(id2)}
                disabled={isLoadingGraph2}
              >
                {isLoadingGraph2 ? 'Loading...' : '📊 Graph ID2'}
              </button>
              <button 
                type="button" 
                className={`btn compact ${!comparisonAllowed ? 'btn-disabled' : 'btn-secondary'}`}
                onClick={() => onGraphSubmit(id1, id2)}
                disabled={(isLoadingGraph1 || isLoadingGraph2) || !comparisonAllowed}
                title={!comparisonAllowed ? `Disabled: ${disabledReason}` : ''}
              >
                {(isLoadingGraph1 || isLoadingGraph2) ? 'Loading...' : (!comparisonAllowed ? '🚫 Compare' : '📊 Compare')}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GraphControls;
