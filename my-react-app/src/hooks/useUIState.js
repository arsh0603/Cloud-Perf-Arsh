import { useMemo } from 'react';
import { UI_MESSAGES } from '../constants/appConstants';

export const useUIState = (runDataHook, graphDataHook, compatibilityHook, submittedIds) => {
  return useMemo(() => {
    // Show data section if there's actual data, loading states, submitted IDs, or errors
    const hasData = runDataHook.data1 || runDataHook.data2 || 
                   runDataHook.isLoading1 || runDataHook.isLoading2 ||
                   submittedIds.submittedId1 || submittedIds.submittedId2 ||
                   runDataHook.error;
    
    // Show graph section if there's graph data, loading states, or submitted IDs
    const hasGraphData = graphDataHook.graphData1 || graphDataHook.graphData2 || 
                        graphDataHook.isLoadingGraph1 || graphDataHook.isLoadingGraph2 ||
                        submittedIds.submittedId1 || submittedIds.submittedId2;
    
    const disabledReason = runDataHook.error && runDataHook.error.includes('model types') 
      ? UI_MESSAGES.DIFFERENT_MODELS 
      : UI_MESSAGES.DIFFERENT_WORKLOADS;

    return {
      hasData,
      hasGraphData,
      disabledReason
    };
  }, [
    runDataHook.data1, 
    runDataHook.data2, 
    runDataHook.isLoading1,
    runDataHook.isLoading2,
    runDataHook.error,
    graphDataHook.graphData1, 
    graphDataHook.graphData2,
    graphDataHook.isLoadingGraph1,
    graphDataHook.isLoadingGraph2,
    submittedIds.submittedId1,
    submittedIds.submittedId2
  ]);
};
