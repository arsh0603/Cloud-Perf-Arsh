import React, { useRef } from 'react';
import './App.css';
import './config/chartConfig'; // Register Chart.js components
import { 
  Header, 
  LoadingIndicator,
  ControlPanel
} from './components';
import DashboardLayout from './components/DashboardLayout';
import { 
  useRunData, 
  useGraphData, 
  useCacheStatus, 
  useCompatibility 
} from './hooks';
import { useAppLogic } from './hooks/useAppLogic';
import { useUIState } from './hooks/useUIState';
import { CSS_CLASSES, UI_MESSAGES } from './constants/appConstants';

function App() {
  // Chart reference for proper cleanup
  const chartRef = useRef();

  // Use custom hooks for data management
  const runDataHook = useRunData();
  const graphDataHook = useGraphData();
  const cacheHook = useCacheStatus();
  const compatibilityHook = useCompatibility(runDataHook.data1, runDataHook.data2);

  // Use custom hook for app logic
  const {
    mode,
    id1,
    id2,
    submittedId1,
    submittedId2,
    inputError,
    showThroughputInMB,
    setShowThroughputInMB,
    handleModeChange,
    handleIdChange,
    handleRunSubmit,
    handleGraphSubmit
  } = useAppLogic(runDataHook, graphDataHook, cacheHook, compatibilityHook);

  // UI state derived values
  const uiState = useUIState(runDataHook, graphDataHook, compatibilityHook);

  // Organize props for cleaner component passing
  const ids = { id1, id2 };
  const submittedIds = { submittedId1, submittedId2 };
  const handlers = {
    handleModeChange,
    handleIdChange,
    handleRunSubmit,
    handleGraphSubmit,
    setShowThroughputInMB
  };
  const runDataProps = {
    data1: runDataHook.data1,
    data2: runDataHook.data2,
    isLoading1: runDataHook.isLoading1,
    isLoading2: runDataHook.isLoading2,
    error: runDataHook.error
  };
  const graphDataProps = {
    graphData1: graphDataHook.graphData1,
    graphData2: graphDataHook.graphData2,
    isLoadingGraph1: graphDataHook.isLoadingGraph1,
    isLoadingGraph2: graphDataHook.isLoadingGraph2
  };

  return (
    <div className={CSS_CLASSES.LAYOUT}>
      <Header />
      
      {/* Top Panel - Controls */}
      <ControlPanel
        mode={mode}
        id1={id1}
        id2={id2}
        onModeChange={handleModeChange}
        onId1Change={(e) => handleIdChange(e.target.value, false)}
        onId2Change={(e) => handleIdChange(e.target.value, true)}
        onSubmit={handleRunSubmit}
        isLoading1={runDataHook.isLoading1}
        isLoading2={runDataHook.isLoading2}
        inputError={inputError}
      />

      <DashboardLayout
        mode={mode}
        ids={ids}
        handlers={handlers}
        runDataProps={runDataProps}
        graphDataProps={graphDataProps}
        compatibilityProps={compatibilityHook}
        submittedIds={submittedIds}
        uiState={{ ...uiState, showThroughputInMB, inputError }}
        chartRef={chartRef}
      />

      <LoadingIndicator 
        isLoading={graphDataHook.isLoadingGraph1 || graphDataHook.isLoadingGraph2}
        message={UI_MESSAGES.LOADING_GRAPH}
        subMessage={UI_MESSAGES.LOADING_SUB}
      />
    </div>
  );
}

export default App;
