import { useMemo } from 'react';
import { UI_MESSAGES } from '../constants/appConstants';

export const useUIState = (runDataHook, graphDataHook, compatibilityHook) => {
  return useMemo(() => {
    const hasData = runDataHook.data1 || runDataHook.data2;
    const hasGraphData = graphDataHook.graphData1 || graphDataHook.graphData2;
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
    runDataHook.error,
    graphDataHook.graphData1, 
    graphDataHook.graphData2
  ]);
};
