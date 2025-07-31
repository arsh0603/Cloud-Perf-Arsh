import React, { useState, useEffect } from 'react';
import './App.css';
import {Line} from 'react-chartjs-2';

function App() {
  const [mode, setMode] = useState('single');
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [submittedId1, setSubmittedId1] = useState('');
  const [submittedId2, setSubmittedId2] = useState('');
  const [data1, setData1] = useState(null);
  const [data2, setData2] = useState(null);
  const [error, setError] = useState(null);
  const [inputError, setInputError] = useState('');
  const [graphData1, setGraphData1] = useState(null);
  const [graphData2, setGraphData2] = useState(null);
  const [graphError, setGraphError] = useState(null);
  const [isLoadingGraph, setIsLoadingGraph] = useState(false);
  const [isLoadingGraph1, setIsLoadingGraph1] = useState(false);
  const [isLoadingGraph2, setIsLoadingGraph2] = useState(false);
  const [isLoading1, setIsLoading1] = useState(false);
  const [isLoading2, setIsLoading2] = useState(false);
  const [cacheStatus, setCacheStatus] = useState(null);
  const [showThroughputInMB, setShowThroughputInMB] = useState(true);

  const fetchCacheStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cache-management/');
      if (response.ok) {
        const status = await response.json();
        setCacheStatus(status);
      }
    } catch (error) {
      console.error('Error fetching cache status:', error);
    }
  };

  useEffect(() => {
    fetchCacheStatus();
  }, []);

  const fetchDataForId = async (id, setDataFunction, setLoadingFunction) => {
    if (id.length !== 9) {
      return;
    }
    
    setLoadingFunction(true);
    try {
      const url = `http://localhost:8000/api/fetch-details/?id=${id}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const result = await response.json();
      setDataFunction(result);
      
      fetchCacheStatus();
    } catch (error) {
      setError(error.toString());
      setDataFunction(null);
    } finally {
      setLoadingFunction(false);
    }
  };

  const handleId1Change = (e) => {
    const newId = e.target.value;
    setId1(newId);
    
    if (submittedId1 && newId !== submittedId1) {
      setGraphData1(null);
    }
  };

  const handleId2Change = (e) => {
    const newId = e.target.value;
    setId2(newId);
    
    if (submittedId2 && newId !== submittedId2) {
      setGraphData2(null);
    }
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    if (newMode === 'single') {
      setData2(null);
      setSubmittedId2('');
      setId2('');
    } else {
      setData2(null);
      setSubmittedId2('');
    }
    setError(null);
    setInputError('');
    setGraphError(null);
    setGraphData1(null);
    setGraphData2(null);
    window.comparisonAllowed = undefined;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setInputError('');
    setGraphError(null);

    if (mode === 'single') {
      if (id1.length !== 9) {
        setInputError('ID 1 must be exactly 9 characters long.');
        return;
      }
      await fetchDataForId(id1, setData1, setIsLoading1);
      setSubmittedId1(id1);
      setData2(null); 
    } else {
      if (id1.length !== 9 && id2.length !== 9) {
        setInputError("Both ID fields must be 9 characters long.");
        return;
      }
      if (id1.length !== 9) {
        setInputError('ID 1 must be exactly 9 characters long.');
        return;
      }
      if (id2.length !== 9) {
        setInputError('ID 2 must be exactly 9 characters long.');
        return;
      }
      
      setIsLoading1(true);
      setIsLoading2(true);
      
      try {
        const url = `http://localhost:8000/api/fetch-details/?id1=${id1}&id2=${id2}`;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        
        const result = await response.json();
        
        if (result.id1) {
          setData1(result.id1);
        }
        if (result.id2) {
          setData2(result.id2);
        }
        
        if (result.error_id1) {
          setError(result.error_id1);
        }
        if (result.error_id2) {
          setError(result.error_id2);
        }
        
        if (result.comparison_error) {
          if (result.comparison_error.error_type === 'workload') {
            setError(`⚠️ ${result.comparison_error.message}: ID1 workload (${result.comparison_error.workload_id1}) vs ID2 workload (${result.comparison_error.workload_id2})`);
            setGraphError('Graph comparison disabled due to different workload types');
          } else if (result.comparison_error.error_type === 'model') {
            setError(`⚠️ ${result.comparison_error.message}: ID1 model (${result.comparison_error.model_id1}) vs ID2 model (${result.comparison_error.model_id2})`);
            setGraphError('Graph comparison disabled due to different model types');
          }
          setGraphData1(null);
          setGraphData2(null);
          window.comparisonAllowed = false;
        } else {
          window.comparisonAllowed = true;
        }
        
        setSubmittedId1(id1);
        setSubmittedId2(id2);
        
        fetchCacheStatus();
      } catch (error) {
        setError(error.toString());
        setData1(null);
        setData2(null);
      } finally {
        setIsLoading1(false);
        setIsLoading2(false);
      }
    }
  };

  const handleSubmitId1 = async (event) => {
    event.preventDefault();
    setError(null);
    setInputError('');
    
    if (id1.length !== 9) {
      setInputError('ID 1 must be exactly 9 characters long.');
      return;
    }
    
    await fetchDataForId(id1, setData1, setIsLoading1);
    setSubmittedId1(id1);
    
    setTimeout(() => checkWorkloadCompatibility(), 100);
  };

  const handleSubmitId2 = async (event) => {
    event.preventDefault();
    setError(null);
    setInputError('');
    
    if (id2.length !== 9) {
      setInputError('ID 2 must be exactly 9 characters long.');
      return;
    }
    
    await fetchDataForId(id2, setData2, setIsLoading2);
    setSubmittedId2(id2);
    
    setTimeout(() => checkWorkloadCompatibility(), 100);
  };

  const handleGraph = async (event) => {
    event.preventDefault();
    setGraphError(null);
    
    if (mode === 'compare') {
      if (id1.length !== 9) {
        setGraphError('ID 1 must be exactly 9 characters long.');
        return;
      }
      if (id2.length !== 9) {
        setGraphError('ID 2 must be exactly 9 characters long.');
        return;
      }
      
      if (window.comparisonAllowed === false) {
        const errorType = error && error.includes('model types') ? 'model types' : 'workload types';
        setGraphError(`❌ Cannot generate comparison graph: Runs have different ${errorType} and cannot be meaningfully compared`);
        return;
      }
      
      
      const hasGraphData1 = graphData1 && submittedId1 === id1;
      const hasGraphData2 = graphData2 && submittedId2 === id2;
      
      if (hasGraphData1 && hasGraphData2) {
        console.log('Graph data for both IDs already exists, skipping fetch');
        return;
      }
      
      setIsLoadingGraph(true);
      await fetchGraphForBothIds();
    } else if (mode === 'single') {
      if (!id1) {
        setGraphError('ID must be provided for graph display.');
        return;
      }
      
      if (id1.length !== 9) {
        setGraphError('ID must be exactly 9 characters long.');
        return;
      }
      
      if (graphData1 && submittedId1 === id1) {
        console.log('Graph data for ID1 already exists, skipping fetch');
        return;
      }
      
      await fetchGraphData(id1, false);
    }
  };

  const handleGraphId1 = async (event) => {
    event.preventDefault();
    setGraphError(null);
    
    if (!id1) {
      setGraphError('ID 1 must be provided for graph display.');
      return;
    }
    
    if (id1.length !== 9) {
      setGraphError('ID 1 must be exactly 9 characters long.');
      return;
    }
    
    if (graphData1 && submittedId1 === id1) {
      console.log('Graph data for ID1 already exists, skipping fetch');
      return;
    }
    
    await fetchGraphData(id1, false);
  };

  const handleGraphId2 = async (event) => {
    event.preventDefault();
    setGraphError(null);
    
    if (!id2) {
      setGraphError('ID 2 must be provided for graph display.');
      return;
    }
    
    if (id2.length !== 9) {
      setGraphError('ID 2 must be exactly 9 characters long.');
      return;
    }
    
    if (graphData2 && submittedId2 === id2) {
      console.log('Graph data for ID2 already exists, skipping fetch');
      return;
    }
    
    await fetchGraphData(id2, true);
  };

  const fetchGraphData = async (runId, isSecondId = false) => {
    if (isSecondId) {
      setIsLoadingGraph2(true);
    } else {
      setIsLoadingGraph1(true);
    }
    
    const startTime = Date.now();
    console.log('Starting graph data fetch for ID:', runId);
    
    try {
      const url = `http://localhost:8000/api/fetch-graph-data/?run_id1=${runId}`;
      console.log('Fetching from:', url);
      
      const response = await fetch(url);
      const fetchTime = Date.now() - startTime;
      console.log(`Fetch completed in ${fetchTime}ms`);
      console.log(response);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }


      const result = await response.json();
      const totalTime = Date.now() - startTime;
      console.log(`Total processing time: ${totalTime}ms`);
      console.log('Backend response:', result);

      if (!result.data_points || Object.keys(result.data_points).length === 0) {
        throw new Error('No data points received from backend');
      }

      if (isSecondId) {
        setGraphData2(result.data_points);
      } else {
        setGraphData1(result.data_points);
      }
      
      if (result.missing_data && result.missing_data.length > 0) {
        const missingDataMessage = result.missing_data.join('. ');
        setGraphError(`⚠️ ${missingDataMessage}`);
      }
      
      fetchCacheStatus();
    } catch (error) {
      console.error('Graph loading error:', error);
      const graphId = isSecondId ? 'ID2' : 'ID1';
      setGraphError(`❌ Error loading graph for ${graphId}: ${error.message}`);
    } finally {
      if (isSecondId) {
        setIsLoadingGraph2(false);
      } else {
        setIsLoadingGraph1(false);
      }
    }
  };

  const fetchGraphForBothIds = async () => {
    if (!id1 || !id2) {
      setGraphError('Both IDs must be provided for graph comparison.');
      setIsLoadingGraph(false);
      return;
    }

    if (id1.length !== 9) {
      setGraphError('ID 1 must be exactly 9 characters long.');
      setIsLoadingGraph(false);
      return;
    }

    if (id2.length !== 9) {
      setGraphError('ID 2 must be exactly 9 characters long.');
      setIsLoadingGraph(false);
      return;
    }

    if (window.comparisonAllowed === false) {
      const errorType = error && error.includes('model types') ? 'model types' : 'workload types';
      setGraphError(`Cannot generate comparison graph: Runs have different ${errorType}`);
      setIsLoadingGraph(false);
      return;
    }

    const startTime = Date.now();
    console.log('Starting graph data fetch for both IDs...');
    
    const needsData1 = !graphData1 || submittedId1 !== id1;
    const needsData2 = !graphData2 || submittedId2 !== id2;
    
    if (!needsData1 && !needsData2) {
      console.log('Both graph data already exist, skipping fetch');
      setIsLoadingGraph(false);
      return;
    }
    
    try {
      const url = `http://localhost:8000/api/fetch-graph-data/?run_id1=${id1}&run_id2=${id2}`;
      console.log('Fetching graph data for both IDs from:', url);
      
      const response = await fetch(url);
      
      const fetchTime = Date.now() - startTime;
      console.log(`Fetch completed in ${fetchTime}ms`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      const totalTime = Date.now() - startTime;
      console.log(`Total processing time for both: ${totalTime}ms`);

      if (!result.data_points || Object.keys(result.data_points).length === 0) {
        throw new Error('No data points received from backend');
      }

      if (result.data_points[id1]) {
        setGraphData1({ [id1]: result.data_points[id1] });
      }
      if (result.data_points[id2]) {
        setGraphData2({ [id2]: result.data_points[id2] });
      }
      
      if (result.missing_data && result.missing_data.length > 0) {
        const missingDataMessage = result.missing_data.join('. ');
        setGraphError(`⚠️ ${missingDataMessage}`);
      }
      
      fetchCacheStatus();
    } catch (error) {
      console.error('Graph loading error:', error);
      setGraphError(`Error loading graph: ${error.message}`);
    } finally {
      setIsLoadingGraph(false);
    }
  };

  const generatePerfwebLink = (runId) => {
    if (!runId || runId.length < 4) return null;
    const yearMonth = runId.substring(0, 4);
    return `http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/${yearMonth}/${runId}/cloud_test_harness.log`;
  };

  const checkWorkloadCompatibility = () => {
    if (mode === 'compare' && data1 && data2) {
      const workload1 = data1['Workload Type'];
      const workload2 = data2['Workload Type'];
      const model1 = data1['Model'];
      const model2 = data2['Model'];

      if (workload1 && workload2) {
        if (workload1 !== workload2) {
          window.comparisonAllowed = false;
          setError(`⚠️ Cannot compare runs with different workload types: ID1 workload (${workload1}) vs ID2 workload (${workload2})`);
          setGraphError('Comparison disabled: Different workload types. Individual graphs/data are still shown.');
        } else if (model1 && model2 && model1 !== model2) {
          window.comparisonAllowed = false;
          setError(`⚠️ Cannot compare runs with different model types: ID1 model (${model1}) vs ID2 model (${model2})`);
          setGraphError('Comparison disabled: Different model types. Individual graphs/data are still shown.');
        } else {
          window.comparisonAllowed = true;
          if (error && (error.includes('Cannot compare runs with different workload types') || error.includes('Cannot compare runs with different model types'))) {
            setError(null);
          }
          if (graphError && (graphError.includes('Comparison disabled'))) {
            setGraphError(null);
          }
        }
      }
    }
  };

  useEffect(() => {
    checkWorkloadCompatibility();
  }, [data1, data2, mode]);

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <img src="/netapp.png" alt="NetApp Logo" className="logo-image" />
          </div>
          <h1 className="header-title">Performance Analytics Dashboard</h1>
        </div>
      </header>

      <div className="main-content">
        
        <div className="dashboard-card">
          <h3 className="card-title">Analysis Mode</h3>
          <div className="mode-toggle">
            <button 
              className={`mode-btn ${mode === 'single' ? 'active' : ''}`}
              onClick={() => handleModeChange('single')}
            >
              Single Run Analysis
            </button>
            <button 
              className={`mode-btn ${mode === 'compare' ? 'active' : ''}`}
              onClick={() => handleModeChange('compare')}
            >
              Compare Runs
            </button>
          </div>
        </div>

        <div className="dashboard-card">
          <h3 className="card-title">
            {mode === 'single' ? 'Run ID Input' : 'Compare Run IDs'}
          </h3>
          
          {mode === 'single' ? (
            <form onSubmit={handleSubmit} className="form-section">
              <div className="form-row">
                <div className="input-group">
                  <label className="input-label">Run ID (9 characters)</label>
                  <input
                    type="text"
                    className="input-field"
                    value={id1}
                    onChange={handleId1Change}
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
                    onChange={handleId1Change}
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
                    onChange={handleId2Change}
                    placeholder="e.g., 250726xyz"
                    maxLength="9"
                  />
                </div>
              </div>
              
              <div className="btn-group">
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  onClick={handleSubmitId1} 
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
                  onClick={handleSubmitId2} 
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
                  onClick={handleSubmit} 
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

        {(data1 || data2) && (
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
              
              {mode === 'compare' && window.comparisonAllowed === false && (
                <div className="warning-message">
                  ⚠️ <strong>Compatibility Issue:</strong> Individual graphs are available, but graph comparison is disabled due to different {error && error.includes('model types') ? 'model types' : 'workload types'}.
                </div>
              )}
              
              <div className="btn-group">
                {mode === 'single' ? (
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={handleGraph}
                    disabled={isLoadingGraph1}
                  >
                    {isLoadingGraph1 ? (
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
                      onClick={handleGraphId1}
                      disabled={isLoadingGraph1}
                    >
                      {isLoadingGraph1 ? (
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
                      onClick={handleGraphId2}
                      disabled={isLoadingGraph2}
                    >
                      {isLoadingGraph2 ? (
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
                      className={`btn ${window.comparisonAllowed === false ? 'btn-disabled' : 'btn-secondary'}`}
                      onClick={handleGraph}
                      disabled={isLoadingGraph || window.comparisonAllowed === false}
                      title={window.comparisonAllowed === false ? `Disabled: Different ${error && error.includes('model types') ? 'model types' : 'workload types'}` : ''}
                    >
                      {isLoadingGraph ? (
                        <>
                          <span className="loading-spinner"></span>
                          Loading Both...
                        </>
                      ) : window.comparisonAllowed === false ? (
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

        <div className="dashboard-card">
          <h3 className="card-title">System Status</h3>
          {cacheStatus ? (
            <div className="status-grid">
              <div className="status-card">
                <h5>Memory Cache</h5>
                <p><strong>Items:</strong> {cacheStatus.memory_cache?.size || 0}/{cacheStatus.memory_cache?.max_size || 20}</p>
                <p><strong>Details:</strong> {cacheStatus.memory_cache?.details_keys?.length || 0} entries</p>
                <p><strong>Graphs:</strong> {cacheStatus.memory_cache?.graph_keys?.length || 0} entries</p>
                {cacheStatus.memory_cache?.access_order?.length > 0 && (
                  <p style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                    <strong>Recent:</strong> {cacheStatus.memory_cache.access_order.slice(-3).join(', ')}
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="loading-indicator">
              <span className="loading-spinner"></span>
              Loading system status...
            </div>
          )}
        </div>

        {inputError && <div className="error">⚠️ {inputError}</div>}
        {error && <div className="warning">⚠️ {error}</div>}
        {graphError && <div className="error">❌ {graphError}</div>}

        {(data1 || data2) && (
          <div className="dashboard-card">
            <h3 className="card-title">Performance Data</h3>
            
            {mode === 'compare' && data1 && data2 && (
              <div className={`compatibility-status ${window.comparisonAllowed === false ? 'incompatible' : 'compatible'}`}>
                {window.comparisonAllowed === false ? (
                  <>
                    {error && error.includes('model types') ? (
                      <>
                        ⚠️ <strong>Model Incompatibility:</strong> These runs have different model types 
                        ({data1['Model']} vs {data2['Model']}). <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual data and graphs are shown below.</span>
                      </>
                    ) : (
                      <>
                        ⚠️ <strong>Workload Incompatibility:</strong> These runs have different workload types 
                        ({data1['Workload Type']} vs {data2['Workload Type']}). <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual data and graphs are shown below.</span>
                      </>
                    )}
                  </>
                ) : window.comparisonAllowed === true ? (
                  <>
                    ✅ <strong>Compatible Runs:</strong> Both runs use workload type {data1['Workload Type']} 
                    and model {data1['Model']} and can be compared.
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
                      ID1: {isLoading1 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (submittedId1)}
                      {isLoading1 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : submittedId1 && (
                        <a 
                          href={generatePerfwebLink(submittedId1)} 
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
                        ID2: {isLoading2 ? (
                          <span style={{ color: '#9ca3af' }}>Loading...</span>
                        ) : (submittedId2)}
                        {isLoading2 ? (
                          <span style={{ color: '#9ca3af' }}>Loading...</span>
                        ) : submittedId2 && (
                          <a 
                            href={generatePerfwebLink(submittedId2)} 
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
                {data1 && Object.keys(data1).map((key) => (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>
                      {isLoading1 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (
                        data1[key] !== null && data1[key] !== undefined && data1[key] !== '' ? data1[key] : 'N/A'
                      )}
                    </td>
                    {mode === 'compare' && (
                      <td>
                        {isLoading2 ? (
                          <span style={{ color: '#9ca3af' }}>Loading...</span>
                        ) : (
                          data2 && data2[key] !== null && data2[key] !== undefined && data2[key] !== '' ? data2[key] : 'N/A'
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {mode === 'compare' && data2 && Object.keys(data2).filter(key => !data1 || !data1.hasOwnProperty(key)).map((key) => (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>N/A</td>
                    <td>
                      {isLoading2 ? (
                        <span style={{ color: '#9ca3af' }}>Loading...</span>
                      ) : (
                        data2[key] !== null && data2[key] !== undefined && data2[key] !== '' ? data2[key] : 'N/A'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {(graphData1 || graphData2) && (
          <div className="dashboard-card">
            <h3 className="card-title">📈 Latency vs Throughput Performance</h3>
            
            {mode === 'compare' && graphData1 && graphData2 && window.comparisonAllowed === false && data1 && data2 && (
              <div className="warning-message">
                ⚠️ <strong>Note:</strong> These graphs show different {error && error.includes('model types') ? 'model types' : 'workload types'} 
                {error && error.includes('model types') ? 
                  `(${data1['Model']} vs ${data2['Model']})` : 
                  `(${data1['Workload Type']} vs ${data2['Workload Type']})`
                }. <span style={{color:'#e53e3e'}}>Comparison is not valid, but individual graphs are shown below for analysis.</span>
              </div>
            )}
            
            <div className="chart-container">
              <Line
                data={{
                  datasets: [
                    ...(graphData1 ? Object.keys(graphData1).map((runId, index) => ({
                      label: `ID1 - Run ${runId}`,
                      data: graphData1[runId].map((point, pointIndex) => ({
                        x: showThroughputInMB ? point.throughput / (1024 * 1024) : point.throughput,
                        y: point.latency,
                        label: `Iteration ${pointIndex + 1}`
                      })),
                      borderColor: `hsla(${index * 137.508}, 70%, 50%, 1)`,
                      backgroundColor: `hsla(${index * 137.508}, 70%, 50%, 0.1)`,
                      fill: false,
                      tension: 0.1,
                      pointRadius: 4,
                      pointHoverRadius: 6
                    })) : []),
                    ...(graphData2 ? Object.keys(graphData2).map((runId, index) => ({
                      label: `ID2 - Run ${runId}`,
                      data: graphData2[runId].map((point, pointIndex) => ({
                        x: showThroughputInMB ? point.throughput / (1024 * 1024) : point.throughput,
                        y: point.latency,
                        label: `Iteration ${pointIndex + 1}`
                      })),
                      borderColor: `hsla(${(index + 1) * 137.508 + 60}, 70%, 50%, 1)`,
                      backgroundColor: `hsla(${(index + 1) * 137.508 + 60}, 70%, 50%, 0.1)`,
                      fill: false,
                      tension: 0.1,
                      pointRadius: 4,
                      pointHoverRadius: 6
                    })) : [])
                  ]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    x: {
                      type: 'linear',
                      position: 'bottom',
                      title: {
                        display: true,
                        text: showThroughputInMB ? 'Throughput (MB/s)' : 'Throughput (bytes/sec)',
                        font: { size: 12, weight: 'bold' }
                      },
                      grid: { color: '#f3f4f6' }
                    },
                    y: {
                      title: {
                        display: true,
                        text: 'Latency (μs)',
                        font: { size: 12, weight: 'bold' }
                      },
                      grid: { color: '#f3f4f6' }
                    }
                  },
                  plugins: {
                    legend: {
                      display: true,
                      position: 'top',
                      labels: { 
                        usePointStyle: true,
                        font: { size: 11 }
                      }
                    },
                    tooltip: {
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      titleColor: 'white',
                      bodyColor: 'white',
                      callbacks: {
                        title: function(context) {
                          return context[0].raw.label || '';
                        },
                        label: function(context) {
                          const throughputUnit = showThroughputInMB ? 'MB/s' : 'bytes/sec';
                          const throughputValue = showThroughputInMB ? 
                            context.raw.x.toFixed(2) : 
                            context.raw.x.toLocaleString();
                          
                          return [
                            `${context.dataset.label}`,
                            `Throughput: ${throughputValue} ${throughputUnit}`,
                            `Latency: ${context.raw.y.toFixed(2)} μs`
                          ];
                        }
                      }
                    }
                  },
                  interaction: {
                    intersect: false,
                    mode: 'index'
                  }
                }}
              />
            </div>
          </div>
        )}

        {(isLoadingGraph1 || isLoadingGraph2 || isLoadingGraph) && (
          <div className="loading-indicator">
            <span className="loading-spinner"></span>
            <div>Processing performance data...</div>
            <div style={{ fontSize: '0.875rem', color: '#9ca3af', marginTop: '0.5rem' }}>
              This may take a moment while analyzing the run data
            </div>
          </div>
        )}
        
      </div>
    </div>
  );
}

export default App;
