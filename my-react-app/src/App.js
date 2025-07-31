import React, { useState } from 'react';
import './App.css';
import { Line } from 'react-chartjs-2';
import { 
  Header, 
  ModeSelector, 
  RunIdInput, 
  SystemStatus, 
  ErrorDisplay, 
  LoadingIndicator 
} from './components';
import { 
  useRunData, 
  useGraphData, 
  useCacheStatus, 
  useCompatibility 
} from './hooks';
import { validation, urlUtils, chartUtils, compatibilityUtils } from './utils/helpers';

function App() {
  const [mode, setMode] = useState('single');
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [submittedId1, setSubmittedId1] = useState('');
  const [submittedId2, setSubmittedId2] = useState('');
  const [inputError, setInputError] = useState('');
  const [showThroughputInMB, setShowThroughputInMB] = useState(true);

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
    setInputError('');
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
    setInputError('');
    
    const validationResult = validation.validateRunIds(runId1, runId2);
    if (!validationResult.isValid) {
      setInputError(validationResult.errors[0]);
      return;
    }

    if (runId2) {
      await runDataHook.fetchComparisonRuns(runId1, runId2);
      setSubmittedId1(runId1);
      setSubmittedId2(runId2);
    } else {
      await runDataHook.fetchSingleRun(runId1);
      if (mode === 'single') {
        setSubmittedId1(runId1);
      } else {
        // In comparison mode, determine which ID was submitted
        if (runId1 === id1) setSubmittedId1(runId1);
        if (runId1 === id2) setSubmittedId2(runId1);
      }
    }
    
    await cacheHook.fetchCacheStatus();
  };

  const handleGraphSubmit = async (runId1, runId2 = null) => {
    const validationResult = validation.validateRunIds(runId1, runId2);
    if (!validationResult.isValid) {
      return;
    }

    if (runId2) {
      // Comparison mode
      if (!compatibilityHook.comparisonAllowed) {
        return;
      }
      await graphDataHook.fetchGraphDataComparison(runId1, runId2);
    } else {
      // Single mode or individual graph
      await graphDataHook.fetchGraphData(runId1, runId1 === id2);
    }
    
    await cacheHook.fetchCacheStatus();
  };

  return (
    <div className="App">
      <Header />
      
      <div className="main-content">
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

        {(runDataHook.data1 || runDataHook.data2) && (
          <div className="dashboard-card">
            <h3 className="card-title">Performance Graphs</h3>
            
            <div className="form-section">
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={showThroughputInMB}
                  onChange={(e) => setShowThroughputInMB(e.target.checked)}
                />
                <span className="input-label">Show throughput in MB/s</span>
              </div>
              
              {mode === 'compare' && !compatibilityHook.comparisonAllowed && (
                <div className="warning-message">
                  ⚠️ <strong>Compatibility Issue:</strong> Individual graphs are available, but graph comparison is disabled due to different {runDataHook.error && runDataHook.error.includes('model types') ? 'model types' : 'workload types'}.
                </div>
              )}
              
              <div className="btn-group">
                {mode === 'single' ? (
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={() => handleGraphSubmit(id1)}
                    disabled={graphDataHook.isLoadingGraph1}
                  >
                    {graphDataHook.isLoadingGraph1 ? (
                      <>
                        <span className="loading-spinner"></span>
                        Loading Graph...
                      </>
                    ) : (
                      '📊 Generate Graph'
                    )}
                  </button>
                ) : (
                  <>
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={() => handleGraphSubmit(id1)}
                      disabled={graphDataHook.isLoadingGraph1}
                    >
                      {graphDataHook.isLoadingGraph1 ? (
                        <>
                          <span className="loading-spinner"></span>
                          Loading Graph 1...
                        </>
                      ) : (
                        '📊 Graph for ID1'
                      )}
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={() => handleGraphSubmit(id2)}
                      disabled={graphDataHook.isLoadingGraph2}
                    >
                      {graphDataHook.isLoadingGraph2 ? (
                        <>
                          <span className="loading-spinner"></span>
                          Loading Graph 2...
                        </>
                      ) : (
                        '📊 Graph for ID2'
                      )}
                    </button>
                    <button 
                      type="button" 
                      className={`btn ${!compatibilityHook.comparisonAllowed ? 'btn-disabled' : 'btn-secondary'}`}
                      onClick={() => handleGraphSubmit(id1, id2)}
                      disabled={graphDataHook.isLoadingGraph || !compatibilityHook.comparisonAllowed}
                      title={!compatibilityHook.comparisonAllowed ? `Disabled: Different ${runDataHook.error && runDataHook.error.includes('model types') ? 'model types' : 'workload types'}` : ''}
                    >
                      {graphDataHook.isLoadingGraph ? (
                        <>
                          <span className="loading-spinner"></span>
                          Loading Both...
                        </>
                      ) : !compatibilityHook.comparisonAllowed ? (
                        '🚫 Compare Graphs (Disabled)'
                      ) : (
                        '📊 Compare Graphs'
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        <SystemStatus cacheStatus={cacheHook.cacheStatus} />
        
        <ErrorDisplay 
          inputError={inputError}
          error={runDataHook.error}
          graphError={graphDataHook.graphError}
        />

        {(runDataHook.data1 || runDataHook.data2) && (
          <div className="dashboard-card">
            <h3 className="card-title">Performance Data</h3>
            
            {mode === 'compare' && runDataHook.data1 && runDataHook.data2 && (
              <div className={`compatibility-status ${!compatibilityHook.comparisonAllowed ? 'incompatible' : 'compatible'}`}>
                {!compatibilityHook.comparisonAllowed ? (
                  <>
                    {runDataHook.error && runDataHook.error.includes('model types') ? (
                      <>
                        ⚠️ <strong>Model Incompatibility:</strong> These runs have different model types 
                        ({runDataHook.data1['Model']} vs {runDataHook.data2['Model']}). <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual data and graphs are shown below.</span>
                      </>
                    ) : (
                      <>
                        ⚠️ <strong>Workload Incompatibility:</strong> These runs have different workload types 
                        ({runDataHook.data1['Workload Type']} vs {runDataHook.data2['Workload Type']}). <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual data and graphs are shown below.</span>
                      </>
                    )}
                  </>
                ) : compatibilityHook.comparisonAllowed === true ? (
                  <>
                    ✅ <strong>Compatible Runs:</strong> Both runs use workload type {runDataHook.data1['Workload Type']} 
                    and model {runDataHook.data1['Model']} and can be compared.
                  </>
                ) : (
                  <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                    ⏳ Checking compatibility...
                  </div>
                )}
              </div>
            )}
            
            <table className="data-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>
                    <div>
                      ID1: {runDataHook.isLoading1 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (submittedId1)}
                      {!runDataHook.isLoading1 && submittedId1 && (
                        <a 
                          href={urlUtils.generatePerfwebLink(submittedId1)} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="perfweb-link"
                        >
                          📊 View Log
                        </a>
                      )}
                    </div>
                  </th>
                  {mode === 'compare' && (
                    <th>
                      <div>
                        ID2: {runDataHook.isLoading2 ? (
                          <span style={{ color: '#9ca3af' }}>Loading...</span>
                        ) : (submittedId2)}
                        {!runDataHook.isLoading2 && submittedId2 && (
                          <a 
                            href={urlUtils.generatePerfwebLink(submittedId2)} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="perfweb-link"
                          >
                            📊 View Log
                          </a>
                        )}
                      </div>
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
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (
                        runDataHook.data1[key] !== null && runDataHook.data1[key] !== undefined && runDataHook.data1[key] !== '' ? runDataHook.data1[key] : 'N/A'
                      )}
                    </td>
                    {mode === 'compare' && (
                      <td>
                        {runDataHook.isLoading2 ? (
                          <span style={{ color: '#9ca3af' }}>Loading...</span>
                        ) : (
                          runDataHook.data2 && runDataHook.data2[key] !== null && runDataHook.data2[key] !== undefined && runDataHook.data2[key] !== '' ? runDataHook.data2[key] : 'N/A'
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {mode === 'compare' && runDataHook.data2 && Object.keys(runDataHook.data2).filter(key => !runDataHook.data1 || !runDataHook.data1.hasOwnProperty(key)).map((key) => (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>N/A</td>
                    <td>
                      {runDataHook.isLoading2 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (
                        runDataHook.data2[key] !== null && runDataHook.data2[key] !== undefined && runDataHook.data2[key] !== '' ? runDataHook.data2[key] : 'N/A'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {(graphDataHook.graphData1 || graphDataHook.graphData2) && (
          <div className="dashboard-card">
            <h3 className="card-title">📈 Latency vs Throughput Performance</h3>
            
            {mode === 'compare' && graphDataHook.graphData1 && graphDataHook.graphData2 && !compatibilityHook.comparisonAllowed && runDataHook.data1 && runDataHook.data2 && (
              <div className="warning-message">
                ⚠️ <strong>Note:</strong> These graphs show different {runDataHook.error && runDataHook.error.includes('model types') ? 'model types' : 'workload types'} 
                {runDataHook.error && runDataHook.error.includes('model types') ? 
                  `(${runDataHook.data1['Model']} vs ${runDataHook.data2['Model']})` : 
                  `(${runDataHook.data1['Workload Type']} vs ${runDataHook.data2['Workload Type']})`
                }. <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual graphs are shown below for analysis.</span>
              </div>
            )}
            
            <div className="chart-container">
              <Line data={chartUtils.prepareChartData(graphDataHook.graphData1, graphDataHook.graphData2, showThroughputInMB)} options={chartUtils.getChartOptions(showThroughputInMB)} />
            </div>
          </div>
        )}

        <LoadingIndicator 
          isLoading={graphDataHook.isLoadingGraph1 || graphDataHook.isLoadingGraph2 || graphDataHook.isLoadingGraph}
          message="Processing performance data..."
          subMessage="This may take a moment while analyzing the run data"
        />
      </div>
    </div>
  );
}

export default App;
