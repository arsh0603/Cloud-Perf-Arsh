import React from 'react';
import { Line } from 'react-chartjs-2';
import { chartUtils } from '../utils/helpers';

const ChartSection = ({
  chartRef,
  graphData1,
  graphData2,
  showThroughputInMB,
  submittedId1,
  submittedId2,
  mode,
  comparisonAllowed,
  data1,
  data2,
  isLoading1,
  isLoading2,
  error
}) => {
  return (
    <div className="chart-section">
      <div className="dashboard-card">
        <h3 className="card-title">📈 Performance Chart</h3>
        
        {mode === 'compare' && graphData1 && graphData2 && !comparisonAllowed && data1 && data2 && !isLoading1 && !isLoading2 && (
          <div className="warning-message compact">
            ⚠️ Different {error && error.includes('model types') ? 'model types' : 'workload types'} - comparison not valid.
          </div>
        )} 
        
        <div className="chart-container">
          <Line 
            ref={chartRef}
            key={`chart-${submittedId1}-${submittedId2}-${showThroughputInMB}`}
            data={chartUtils.prepareChartData(graphData1, graphData2, showThroughputInMB)} 
            options={chartUtils.getChartOptions(showThroughputInMB)} 
          />
        </div>
      </div>
    </div>
  );
};

export default ChartSection;
