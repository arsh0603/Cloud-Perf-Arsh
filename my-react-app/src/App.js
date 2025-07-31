import React, { useState, useRef } from 'react';
import './App.css';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { 
  Header, 
  ModeSelector, 
  RunIdInput, 
  ErrorDisplay, 
  LoadingIndicator 
} from './components';
import { 
  useRunData, 
  useGraphData, 
  useCacheStatus, 
  useCompatibility 
} from './hooks';
import { validation, urlUtils, chartUtils } from './utils/helpers';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [mode, setMode] = useState('single');
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [submittedId1, setSubmittedId1] = useState('');
  const [submittedId2, setSubmittedId2] = useState('');
  const [inputError, setInputError] = useState('');
  const [showThroughputInMB, setShowThroughputInMB] = useState(true);
  
  // Chart reference for proper cleanup
  const chartRef = useRef();

  // Use custom hooks for data management
  const runDataHook = useRunData();
  const graphDataHook = useGraphData();
  const cacheHook = useCacheStatus();
  const compatibilityHook = useCompatibility(runDataHook.data1, runDataHook.data2, mode);

  // Event handlers using modular validation and hooks
  const handleModeChange = (newMode) => {
    setMode(newMode);
    if (newMode === 'single') {
      setSubmittedId2('');
      setId2('');
    }
    // Clear all errors when mode changes
    setInputError('');
    runDataHook.setError(null);
    graphDataHook.setGraphError(null);
    runDataHook.clearData();
    graphDataHook.clearGraphData();
  };

  const handleIdChange = (newId, isId2 = false) => {
    if (isId2) {
      setId2(newId);
      if (submittedId2 && newId !== submittedId2) {
        graphDataHook.clearGraphData();
      }
    } else {
      setId1(newId);
      if (submittedId1 && newId !== submittedId1) {
        graphDataHook.clearGraphData();
      }
    }
  };

  const handleRunSubmit = async (runId1, runId2 = null) => {
    // Clear all errors when starting a new operation
    setInputError('');
    runDataHook.setError(null);
    graphDataHook.setGraphError(null);
    
    // Validate IDs based on mode
    if (runId2) {
      // Comparison mode - validate both IDs
      const validationResult = validation.validateRunIds(runId1, runId2);
      if (!validationResult.isValid) {
        setInputError(validationResult.errors[0]);
        return;
      }
      await runDataHook.fetchComparisonRuns(runId1, runId2);
      setSubmittedId1(runId1);
      setSubmittedId2(runId2);
    } else {
      // Single mode - validate single ID
      if (!validation.isValidRunId(runId1)) {
        setInputError('ID must be exactly 9 characters long.');
        return;
      }
      // Determine if this is for ID2 in comparison mode
      const isSecondId = mode === 'compare' && runId1 === id2;
      
      await runDataHook.fetchSingleRun(runId1, isSecondId);
      if (mode === 'single') {
        setSubmittedId1(runId1);
      } else {
        // In comparison mode, determine which ID was submitted
        if (runId1 === id1) {
          setSubmittedId1(runId1);
        } else if (runId1 === id2) {
          setSubmittedId2(runId1);
        }
      }
    }
    
    await cacheHook.fetchCacheStatus();
  };

  const handleGraphSubmit = async (runId1, runId2 = null) => {
    // Clear graph errors when starting a new graph operation
    graphDataHook.setGraphError(null);
    
    // For individual graphs, only validate the single ID
    if (runId2) {
      // Comparison mode - validate both IDs
      const validationResult = validation.validateRunIds(runId1, runId2);
      if (!validationResult.isValid) {
        return;
      }
      
      // Always proceed with comparison - backend handles compatibility and returns warnings
      await graphDataHook.fetchGraphDataComparison(runId1, runId2);
    } else {
      // Individual graph - validate single ID
      if (!validation.isValidRunId(runId1)) {
        return;
      }
      
      // Determine if this is for the second ID (ID2)
      const isSecondId = runId1 === id2;
      await graphDataHook.fetchGraphData(runId1, isSecondId);
    }
    
    await cacheHook.fetchCacheStatus();
  };

  return (
    <div className="App no-scroll-dashboard">
      <Header />
      
      <div className="dashboard-layout">
        {/* Top Panel - Controls (Horizontal) */}
        <div className="top-panel">
          <div className="controls-row">
            <ModeSelector 
              mode={mode} 
              onModeChange={handleModeChange} 
            />
            
            <RunIdInput
              mode={mode}
              id1={id1}
              id2={id2}
              onId1Change={(e) => handleIdChange(e.target.value, false)}
              onId2Change={(e) => handleIdChange(e.target.value, true)}
              onSubmit={handleRunSubmit}
              isLoading1={runDataHook.isLoading1}
              isLoading2={runDataHook.isLoading2}
              inputError={inputError}
            />
          </div>

          {(runDataHook.data1 || runDataHook.data2) && (
            <div className="graph-controls">
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={showThroughputInMB}
                  onChange={(e) => setShowThroughputInMB(e.target.checked)}
                />
                <span className="input-label">Show throughput in MB/s</span>
              </div>
              
              {/* {mode === 'compare' && !compatibilityHook.comparisonAllowed && (
                <div className="warning-message compact">
                  ⚠️ <strong>Compatibility Issue:</strong> Individual graphs available, comparison disabled.
                </div>
              )} */}
              
              <div className="btn-group horizontal-buttons">
                {mode === 'single' ? (
                  <button 
                    type="button" 
                    className="btn btn-primary compact"
                    onClick={() => handleGraphSubmit(id1)}
                    disabled={graphDataHook.isLoadingGraph1}
                  >
                    {graphDataHook.isLoadingGraph1 ? (
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
                      onClick={() => handleGraphSubmit(id1)}
                      disabled={graphDataHook.isLoadingGraph1}
                    >
                      {graphDataHook.isLoadingGraph1 ? 'Loading...' : '📊 Graph ID1'}
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-primary compact"
                      onClick={() => handleGraphSubmit(id2)}
                      disabled={graphDataHook.isLoadingGraph2}
                    >
                      {graphDataHook.isLoadingGraph2 ? 'Loading...' : '📊 Graph ID2'}
                    </button>
                    <button 
                      type="button" 
                      className={`btn compact ${!compatibilityHook.comparisonAllowed ? 'btn-disabled' : 'btn-secondary'}`}
                      onClick={() => handleGraphSubmit(id1, id2)}
                      disabled={graphDataHook.isLoadingGraph || !compatibilityHook.comparisonAllowed}
                      title={!compatibilityHook.comparisonAllowed ? `Disabled: Different ${runDataHook.error && runDataHook.error.includes('model types') ? 'model types' : 'workload types'}` : ''}
                    >
                      {graphDataHook.isLoadingGraph ? 'Loading...' : (!compatibilityHook.comparisonAllowed ? '🚫 Compare' : '📊 Compare')}
                    </button>
                  </>
                )}
              </div>
            </div>
          )}

          <ErrorDisplay 
            inputError={inputError}
            error={runDataHook.error}
            graphError={graphDataHook.graphError}
          />
        </div>

        {/* Bottom Panel - Data and Charts */}
        <div className={`bottom-panel ${
          (runDataHook.data1 || runDataHook.data2) && (graphDataHook.graphData1 || graphDataHook.graphData2) 
            ? 'has-both' 
            : 'data-only'
        }`}>
          {(runDataHook.data1 || runDataHook.data2) && (
            <div className="data-section">
              <div className="dashboard-card">
                <h3 className="card-title">Performance Data</h3>
                
                {mode === 'compare' && runDataHook.data1 && runDataHook.data2 && (
                  <div className={`compatibility-status compact ${!compatibilityHook.comparisonAllowed ? 'incompatible' : 'compatible'}`}>
                    {!compatibilityHook.comparisonAllowed ? (
                      <>
                        {runDataHook.error && runDataHook.error.includes('model types') ? (
                          <>
                            ⚠️ <strong>Model Incompatibility:</strong> Different model types 
                            ({runDataHook.data1['Model']} vs {runDataHook.data2['Model']}).
                          </>
                        ) : (
                          <>
                            ⚠️ <strong>Workload Incompatibility:</strong> Different workload types 
                            ({runDataHook.data1['Workload Type']} vs {runDataHook.data2['Workload Type']}).
                          </>
                        )}
                      </>
                    ) : compatibilityHook.comparisonAllowed === true ? (
                      <>
                        ✅ <strong>Compatible:</strong> {runDataHook.data1['Workload Type']} / {runDataHook.data1['Model']}
                      </>
                    ) : (
                      <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                        ⏳ Checking compatibility...
                      </div>
                    )}
                  </div>
                )}
                
                <div className="table-container">
                  <table className="data-table compact">
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>
                          ID1: {runDataHook.isLoading1 ? 'Loading...' : submittedId1}
                          {!runDataHook.isLoading1 && submittedId1 && (
                            <a 
                              href={urlUtils.generatePerfwebLink(submittedId1)} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="perfweb-link"
                            >
                              📊
                            </a>
                          )}
                        </th>
                        {mode === 'compare' && (
                          <th>
                            ID2: {runDataHook.isLoading2 ? 'Loading...' : submittedId2}
                            {!runDataHook.isLoading2 && submittedId2 && (
                              <a 
                                href={urlUtils.generatePerfwebLink(submittedId2)} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="perfweb-link"
                              >
                                📊
                              </a>
                            )}
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {runDataHook.data1 && Object.keys(runDataHook.data1).map((key) => (
                        <tr key={key}>
                          <td><strong>{key}</strong></td>
                          <td>
                            {runDataHook.isLoading1 ? (
                              'Loading...'
                            ) : (
                              runDataHook.data1[key] !== null && runDataHook.data1[key] !== undefined && runDataHook.data1[key] !== '' ? runDataHook.data1[key] : 'N/A'
                            )}
                          </td>
                          {mode === 'compare' && (
                            <td>
                              {runDataHook.isLoading2 ? (
                                'Loading...'
                              ) : (
                                runDataHook.data2 && runDataHook.data2[key] !== null && runDataHook.data2[key] !== undefined && runDataHook.data2[key] !== '' ? runDataHook.data2[key] : 'N/A'
                              )}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
          
          {(graphDataHook.graphData1 || graphDataHook.graphData2) && (
            <div className="chart-section">
              <div className="dashboard-card">
                <h3 className="card-title">📈 Performance Chart</h3>
                
                {mode === 'compare' && graphDataHook.graphData1 && graphDataHook.graphData2 && !compatibilityHook.comparisonAllowed && runDataHook.data1 && runDataHook.data2 && (
                  <div className="warning-message compact">
                    ⚠️ Different {runDataHook.error && runDataHook.error.includes('model types') ? 'model types' : 'workload types'} - comparison not valid.
                  </div>
                )}
                
                <div className="chart-container">
                  <Line 
                    ref={chartRef}
                    key={`chart-${submittedId1}-${submittedId2}-${showThroughputInMB}`}
                    data={chartUtils.prepareChartData(graphDataHook.graphData1, graphDataHook.graphData2, showThroughputInMB)} 
                    options={chartUtils.getChartOptions(showThroughputInMB)} 
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <LoadingIndicator 
        isLoading={graphDataHook.isLoadingGraph1 || graphDataHook.isLoadingGraph2 || graphDataHook.isLoadingGraph}
        message="Processing performance data..."
        subMessage="Analyzing run data..."
      />
    </div>
  );
}

export default App;
