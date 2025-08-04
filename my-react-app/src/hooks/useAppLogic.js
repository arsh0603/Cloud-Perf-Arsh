import { useState } from 'react';
import { validation } from '../utils/helpers';

export const useAppLogic = (runDataHook, graphDataHook, cacheHook, compatibilityHook) => {
  const [mode, setMode] = useState('single');
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [submittedId1, setSubmittedId1] = useState('');
  const [submittedId2, setSubmittedId2] = useState('');
  const [inputError, setInputError] = useState('');
  const [showThroughputInMB, setShowThroughputInMB] = useState(true);

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
    // Validate IDs based on mode
    if (runId2) {
      // Clear all errors when starting a comparison operation
      setInputError('');
      runDataHook.setError(null);
      graphDataHook.setGraphError(null);
      
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
      
      await runDataHook.fetchComparisonRuns(runId1, runId2);
      setSubmittedId1(runId1);
      // Only set submittedId2 if runId2 is valid
      if (runId2 && validation.isValidRunId(runId2)) {
        setSubmittedId2(runId2);
      } else {
        setSubmittedId2('');
      }
    } else {
      // Clear all errors when loading individual IDs (both single and compare mode)
      setInputError('');
      runDataHook.setError(null);
      graphDataHook.setGraphError(null);
      
      // Single mode - validate single ID
      if (!validation.isValidRunId(runId1)) {
        setInputError('ID must be exactly 9 characters long.');
        return;
      }
      // Determine if this is for ID2 in comparison mode
      const isSecondId = mode === 'compare' && runId1 === id2;
      
      // In compare mode, when loading individual IDs, clear the compatibility status temporarily
      // by resetting the compatibility hook state
      if (mode === 'compare') {
        compatibilityHook.setComparisonAllowed(undefined);
      }
      
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
      // Comparison mode - use new validation logic
      const validationResult = validation.validateRunIdsForComparison(runId1, runId2);
      if (!validationResult.hasValidId1) {
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
    handleRunSubmit,
    handleGraphSubmit
  };
};
