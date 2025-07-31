import React from 'react';

const RunIdInput = ({ 
  mode, 
  id1, 
  id2, 
  onId1Change, 
  onId2Change, 
  onSubmit, 
  onSubmitId1, 
  onSubmitId2, 
  isLoading1, 
  isLoading2 
}) => {
  return (
    <div className="dashboard-card">
      <h3 className="card-title">
        {mode === 'single' ? 'Run ID Input' : 'Compare Run IDs'}
      </h3>
      
      {mode === 'single' ? (
        <form onSubmit={onSubmit} className="form-section">
          <div className="form-row">
            <div className="input-group">
              <label className="input-label">Run ID (9 characters)</label>
              <input
                type="text"
                className="input-field"
                value={id1}
                onChange={onId1Change}
                placeholder="e.g., 250725hbn"
                maxLength="9"
              />
            </div>
            <div className="btn-group">
              <button type="submit" className="btn btn-primary" disabled={isLoading1}>
                {isLoading1 ? (
                  <>
                    <span className="loading-spinner"></span>
                    Loading...
                  </>
                ) : (
                  'Analyze Run'
                )}
              </button>
            </div>
          </div>
        </form>
      ) : (
        <div className="form-section">
          <div className="form-row">
            <div className="input-group">
              <label className="input-label">First Run ID</label>
              <input
                type="text"
                className="input-field"
                value={id1}
                onChange={onId1Change}
                placeholder="e.g., 250725hbn"
                maxLength="9"
              />
            </div>
            <div className="input-group">
              <label className="input-label">Second Run ID</label>
              <input
                type="text"
                className="input-field"
                value={id2}
                onChange={onId2Change}
                placeholder="e.g., 250726xyz"
                maxLength="9"
              />
            </div>
          </div>
          
          <div className="btn-group">
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={onSubmitId1} 
              disabled={isLoading1}
            >
              {isLoading1 ? (
                <>
                  <span className="loading-spinner"></span>
                  Loading ID1...
                </>
              ) : (
                'Load ID1'
              )}
            </button> 
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={onSubmitId2} 
              disabled={isLoading2}
            >
              {isLoading2 ? (
                <>
                  <span className="loading-spinner"></span>
                  Loading ID2...
                </>
              ) : (
                'Load ID2'
              )}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onSubmit} 
              disabled={isLoading1 || isLoading2}
            >
              {(isLoading1 || isLoading2) ? (
                <>
                  <span className="loading-spinner"></span>
                  Loading...
                </>
              ) : (
                ' Compare Runs'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RunIdInput;
