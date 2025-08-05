import { useState, useEffect } from 'react';
import { validation, workloadUtils } from '../utils/helpers';

export const useAppLogic = (runDataHook, graphDataHook, cacheHook, compatibilityHook) => {
  const [mode, setMode] = useState('single');
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [submittedId1, setSubmittedId1] = useState('');
  const [submittedId2, setSubmittedId2] = useState('');
  const [inputError, setInputError] = useState('');
  const [showThroughputInMB, setShowThroughputInMB] = useState(true);

  // Automatically set throughput units based on workload type
  useEffect(() => {
    const shouldUseMB = workloadUtils.getDefaultThroughputUnit(runDataHook.data1, runDataHook.data2);
    setShowThroughputInMB(shouldUseMB);
  }, [runDataHook.data1, runDataHook.data2]); // React when data changes

  const handleModeChange = (newMode) => {
    setMode(newMode);
    
    // Clear submitted IDs when changing modes
    setSubmittedId1('');
    setSubmittedId2('');
    
    if (newMode === 'single') {
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
    } else {
      setId1(newId);
    }
  };

  const handleRunSubmit = async (runId1, runId2 = null) => {
    // Validate IDs based on mode
    graphDataHook.clearGraphData();
    if (runId2) {
      // Clear all errors when starting a comparison operation
      setInputError('');
      runDataHook.setError(null);
      graphDataHook.setGraphError(null);
      // Clear graph data immediately when user clicks Compare Runs
      
      // Comparison mode - validate both IDs using new logic
      const validationResult = validation.validateRunIdsForComparison(runId1, runId2);
      if (!validationResult.hasValidId1) {
        setInputError('First ID must be exactly 9 characters long.');
        return;
      }
      // Show warning if ID2 is invalid but continue with ID1
      if (runId2 && !validationResult.hasValidId2) {
        setInputError('Second ID is invalid. Proceeding with first ID only.');
      }
      
      await runDataHook.fetchComparisonRuns(runId1, runId2, submittedId1, submittedId2);
      setSubmittedId1(runId1);
      
      let finalRunId2 = '';
      // Only set submittedId2 if runId2 is valid
      if (runId2 && validation.isValidRunId(runId2)) {
        setSubmittedId2(runId2);
        finalRunId2 = runId2;
      } else {
        setSubmittedId2('');
        finalRunId2 = null; // Pass null for invalid ID
      }
      
      // Automatically generate comparison graph after data loads
      await graphDataHook.fetchGraphDataComparison(runId1, finalRunId2);
    } else {
      // Clear all errors when starting any individual ID load
      setInputError('');
      runDataHook.setError(null);
      graphDataHook.setGraphError(null);
      
      // Validate single ID format first before clearing anything
      if (!runId1 || runId1.trim() === '') {
        // For empty ID, clear ALL data and show error (even in compare mode)
        if (mode === 'single') {
          runDataHook.clearData();
          graphDataHook.clearGraphData();
          setSubmittedId1('');
        } else if (mode === 'compare') {
          // In compare mode, clear ALL data when any ID is empty
          runDataHook.clearData();
          graphDataHook.clearGraphData();
          setSubmittedId1('');
          setSubmittedId2('');
        }
        // Also clear runDataHook.error and graphError to ensure UI sections are hidden
        runDataHook.setError(null);
        graphDataHook.setGraphError(null);
        setInputError('ID cannot be empty.');
        return;
      }
      
      if (!validation.isValidRunId(runId1)) {
        // For invalid format, clear ALL data and show only error (even in compare mode)
        if (mode === 'single') {
          runDataHook.clearData();
          graphDataHook.clearGraphData();
          setSubmittedId1('');
        } else if (mode === 'compare') {
          // In compare mode, clear ALL data when any ID is invalid
          runDataHook.clearData();
          graphDataHook.clearGraphData();
          setSubmittedId1('');
          setSubmittedId2('');
        }
        // Also clear runDataHook.error and graphError to ensure UI sections are hidden
        runDataHook.setError(null);
        graphDataHook.setGraphError(null);
        setInputError('ID must be exactly 9 characters long.');
        return;
      }
      
      // Only clear data/graphs after validation passes
      if (mode === 'single') {
        // In single mode, clear everything when starting new valid submission
        runDataHook.clearData();
        graphDataHook.clearGraphData();
        // Don't clear submittedId1 here - we'll set it after API call
      }
      // In comparison mode, graph data will be cleared per ID immediately
      
      // In compare mode, when loading individual IDs, clear the compatibility status temporarily
      // by resetting the compatibility hook state
      if (mode === 'compare') {
        compatibilityHook.setComparisonAllowed(undefined);
      }
      
      // Determine if this is for ID2 in comparison mode
      const isSecondId = mode === 'compare' && runId1 === id2;
      
      try {
        await runDataHook.fetchSingleRun(runId1, isSecondId);
        
        if (mode === 'single') {
          setSubmittedId1(runId1);
          // In single mode, generate individual graph - wrap in try-catch for proper error handling
          try {
            await graphDataHook.fetchGraphData(runId1, false);
          } catch (graphError) {
            // Graph fetch failed - error is already set by fetchGraphData
            console.error('Graph fetch failed:', graphError);
          }
        } else {
          // In comparison mode, determine which ID was submitted and clear its graph data immediately
          const isSecondId = mode === 'compare' && runId1 === id2;
          
          // Clear the specific graph data slot immediately when user clicks Load ID
          if (isSecondId) {
            graphDataHook.clearGraphData2();
          } else {
            graphDataHook.clearGraphData1();
          }
          
          // In comparison mode, determine which ID was submitted and set the state
          if (runId1 === id1) {
            setSubmittedId1(runId1);
            // If ID2 input is empty, clear ID2 data
            if (!id2 || id2.trim() === '') {
              runDataHook.clearData2();
              graphDataHook.clearGraphData2();
              setSubmittedId2('');
            }
          } else if (runId1 === id2) {
            setSubmittedId2(runId1);
            // If ID1 input is empty, clear ID1 data
            if (!id1 || id1.trim() === '') {
              runDataHook.clearData1();
              graphDataHook.clearGraphData1();
              setSubmittedId1('');
            }
          }
          
          // In comparison mode, fetch individual graph for this ID immediately
          await graphDataHook.fetchGraphData(runId1, isSecondId);
          
          // Don't automatically trigger comparison graph - let the individual graphs stand
          // The comparison graph will be generated when the user explicitly clicks "Compare Runs"
        }
      } catch (dataError) {
        // Data fetch failed - error should be set by fetchSingleRun
        console.error('Data fetch failed:', dataError);
        
        // Set submitted ID even when data fetch fails so UI shows error sections properly
        if (mode === 'single') {
          setSubmittedId1(runId1);
          // Explicitly set graph error and clear any existing graph data
          graphDataHook.clearGraphData();
          graphDataHook.setGraphError(`❌ Error loading graph for ${runId1}: Data not found`);
        } else {
          // In comparison mode, set the appropriate submitted ID
          if (runId1 === id1) {
            setSubmittedId1(runId1);
            // If ID2 input is empty, clear ID2 data
            if (!id2 || id2.trim() === '') {
              runDataHook.clearData2();
              graphDataHook.clearGraphData2();
              setSubmittedId2('');
            }
          } else if (runId1 === id2) {
            setSubmittedId2(runId1);
            // If ID1 input is empty, clear ID1 data
            if (!id1 || id1.trim() === '') {
              runDataHook.clearData1();
              graphDataHook.clearGraphData1();
              setSubmittedId1('');
            }
          }
          // Set graph error for the failed ID
          graphDataHook.setGraphError(`❌ Error loading graph for ${runId1}: Data not found`);
        }
      }
    }
    
    await cacheHook.fetchCacheStatus();
  };

  return {
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
    handleRunSubmit
  };
};
