import React from 'react';
import { CSS_CLASSES } from '../constants/appConstants';
import DataSection from './DataSection';
import { ChartSection } from '../components';

const DashboardLayout = ({ 
  mode,
  ids,
  handlers,
  runDataProps,
  graphDataProps,
  compatibilityProps,
  submittedIds,
  uiState,
  chartRef,
  showThroughputInMB,
  setShowThroughputInMB
}) => {
  const { id1, id2 } = ids;
  const { 
    handleModeChange, 
    handleIdChange, 
    handleRunSubmit
  } = handlers;
  
  const { hasData, hasGraphData, disabledReason, inputError } = uiState;
  const { data1, data2, isLoading1, isLoading2 } = runDataProps;
  const { graphData1, graphData2, isLoadingGraph1, isLoadingGraph2, graphError } = graphDataProps;

  return (
    <div className={CSS_CLASSES.DASHBOARD}>
      {/* Bottom Panel - Data and Charts */}
      <div className={`${CSS_CLASSES.BOTTOM_PANEL} ${hasData && hasGraphData ? CSS_CLASSES.BOTTOM_PANEL_BOTH : CSS_CLASSES.BOTTOM_PANEL_DATA}`}>
        {hasData && (
          <DataSection
            mode={mode}
            runDataProps={runDataProps}
            compatibilityProps={compatibilityProps}
            submittedIds={submittedIds}
          />
        )}
        
        {hasGraphData && (
          <ChartSection
            chartRef={chartRef}
            graphData1={graphData1}
            graphData2={graphData2}
            showThroughputInMB={showThroughputInMB}
            setShowThroughputInMB={setShowThroughputInMB}
            submittedId1={submittedIds.submittedId1}
            submittedId2={submittedIds.submittedId2}
            mode={mode}
            comparisonAllowed={compatibilityProps.comparisonAllowed}
            data1={data1}
            data2={data2}
            isLoading1={isLoading1}
            isLoading2={isLoading2}
            isLoadingGraph1={isLoadingGraph1}
            isLoadingGraph2={isLoadingGraph2}
            error={runDataProps.error}
            graphError={graphError}
          />
        )}
      </div>
    </div>
  );
};

export default DashboardLayout;
