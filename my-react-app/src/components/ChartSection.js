import React from 'react';
import { Line } from 'react-chartjs-2';
import { chartUtils } from '../utils/helpers';

const ChartSection = ({
  chartRef,
  graphData1,
  graphData2,
  showThroughputInMB,
  setShowThroughputInMB,
  submittedId1,
  submittedId2,
  mode,
  comparisonAllowed,
  data1,
  data2,
  isLoading1,
  isLoading2,
  isLoadingGraph1,
  isLoadingGraph2,
  error,
  graphError
}) => {
  return (
    <div className="chart-section">
      <div className="dashboard-card">
        <div className="chart-header">
          <h3 className="card-title">📈 Performance Chart</h3>
          
          <div className="toggle-switch">
            <input
              type="checkbox"
              checked={showThroughputInMB}
              onChange={(e) => setShowThroughputInMB(e.target.checked)}
            />
            <span className="input-label">Show throughput in MB/s</span>
          </div>
        </div>
        
        {mode === 'compare' && graphData1 && graphData2 && !comparisonAllowed && data1 && data2 && !isLoading1 && !isLoading2 && (
          <div className="warning-message compact">
            ⚠️ Different {error && error.includes('model types') ? 'model types' : 'workload types'} - comparison not valid.
          </div>
        )} 
        
        {graphError && (
          <div className="error-message compact">
            {graphError}
          </div>
        )}
        
        {(isLoadingGraph1 || isLoadingGraph2) && (
          <div className="loading-message compact">
            📊 Loading graph data...
            {mode === 'compare' && (
              <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', lineHeight: '1.4' }}>
                {isLoadingGraph1 && submittedId1 && (
                  <div>• Loading graph for ID1: {submittedId1}</div>
                )}
                {isLoadingGraph2 && submittedId2 && (
                  <div>• Loading graph for ID2: {submittedId2}</div>
                )}
                {(!isLoadingGraph1 && !isLoadingGraph2) && (
                  <div>• Preparing comparison chart...</div>
                )}
              </div>
            )}
          </div>
        )}
        
        <div className="chart-container">
          {(() => {
            const hasGraphData = graphData1 || graphData2;
            const isLoading = isLoadingGraph1 || isLoadingGraph2;
            const hasSubmittedIds = submittedId1 || submittedId2;
            
            if (hasGraphData && !isLoading) {
              return (
                <Line 
                  ref={chartRef}
                  key={`chart-${submittedId1}-${submittedId2}-${showThroughputInMB}`}
                  data={chartUtils.prepareChartData(graphData1, graphData2, showThroughputInMB)} 
                  options={chartUtils.getChartOptions(showThroughputInMB)} 
                />
              );
            } else if (isLoading) {
              return (
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '300px',
                  color: '#6b7280',
                  fontSize: '0.875rem'
                }}>
                  <div>📊 Preparing chart...</div>
                  {mode === 'compare' && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', textAlign: 'center' }}>
                      {(isLoadingGraph1 && isLoadingGraph2) && 'Loading both comparison graphs'}
                      {(isLoadingGraph1 && !isLoadingGraph2) && 'Loading first graph'}
                      {(!isLoadingGraph1 && isLoadingGraph2) && 'Loading second graph'}
                    </div>
                  )}
                </div>
              );
            } else if (graphError) {
              // When there's a graph error, show a placeholder instead of "waiting"
              return (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '300px',
                  color: '#6b7280',
                  fontSize: '0.875rem'
                }}>
                  📊 Chart unavailable
                </div>
              );
            } else if (hasSubmittedIds) {
              return (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '300px',
                  color: '#6b7280',
                  fontSize: '0.875rem'
                }}>
                  📊 Waiting for graph data...
                </div>
              );
            } else {
              return (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '300px',
                  color: '#6b7280',
                  fontSize: '0.875rem'
                }}>
                  No graph data available
                </div>
              );
            }
          })()}
        </div>
      </div>
    </div>
  );
};

export default ChartSection;
