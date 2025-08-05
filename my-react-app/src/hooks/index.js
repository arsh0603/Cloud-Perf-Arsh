import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../utils/api';
import { validation, compatibilityUtils } from '../utils/helpers';

// Hook for managing run data fetching
export const useRunData = () => {
  const [data1, setData1] = useState(null);
  const [data2, setData2] = useState(null);
  const [isLoading1, setIsLoading1] = useState(false);
  const [isLoading2, setIsLoading2] = useState(false);
  const [error, setError] = useState(null);

  const fetchSingleRun = useCallback(async (id, isSecondId = false) => {
    if (!validation.isValidRunId(id)) {
      return;
    }

    const setLoading = isSecondId ? setIsLoading2 : setIsLoading1;
    const setData = isSecondId ? setData2 : setData1;
    
    setLoading(true);
    setError(null);

    try {
      const result = await apiService.fetchSingleDetails(id);
      setData(result);
      // Don't clear other data in compare mode - only clear when explicitly switching modes
    } catch (error) {
      console.error('Error fetching run data:', error);
      setError(error.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchComparisonRuns = useCallback(async (id1, id2, previousId1 = null, previousId2 = null, forceRefresh = false) => {
    const validationResult = validation.validateRunIdsForComparison(id1, id2);
    if (!validationResult.hasValidId1) {
      setError('First ID must be exactly 9 characters long.');
      return;
    }

    // Only clear errors, don't clear existing data unless IDs have changed or forceRefresh is true
    setError(null);

    // Fetch ID1 and ID2 separately for instant cache rendering
    const promises = [];
    
    // Check if ID1 has changed or force refresh - only fetch if it's different from previous or forced
    const id1Changed = previousId1 !== id1 || forceRefresh;
    if (id1Changed) {
      setIsLoading1(true);
      promises.push(
        apiService.fetchSingleDetails(id1)
          .then(result => {
            setData1(result);
            setIsLoading1(false);
          })
          .catch(error => {
            console.error('Error fetching ID1:', error);
            setError(`ID1 Error: ${error.message}`);
            setData1(null);
            setIsLoading1(false);
          })
      );
    }

    // Check if ID2 has changed or force refresh - only fetch if it's different from previous or forced
    const id2Changed = previousId2 !== id2 || forceRefresh;
    if (validationResult.hasValidId2) {
      if (id2Changed) {
        setIsLoading2(true);
        promises.push(
          apiService.fetchSingleDetails(id2)
            .then(result => {
              setData2(result);
              setIsLoading2(false);
            })
            .catch(error => {
              console.error('Error fetching ID2:', error);
              setError(prevError => prevError ? `${prevError}; ID2 Error: ${error.message}` : `ID2 Error: ${error.message}`);
              setData2(null);
              setIsLoading2(false);
            })
        );
      }
    } else {
      // Clear ID2 data if ID2 is invalid and it was previously valid
      if (previousId2 && validation.isValidRunId(previousId2)) {
        setData2(null);
      }
    }

    // Wait for all promises to complete and return compatibility status
    try {
      await Promise.allSettled(promises);
      return { comparisonAllowed: true };
    } catch (error) {
      console.error('Error in comparison fetch:', error);
      return { comparisonAllowed: false };
    }
  }, []);

  const clearData = useCallback(() => {
    setData1(null);
    setData2(null);
    setError(null);
  }, []);

  const clearData1 = useCallback(() => {
    setData1(null);
    setError(null);
  }, []);

  const clearData2 = useCallback(() => {
    setData2(null);
    setError(null);
  }, []);

  return {
    data1,
    data2,
    isLoading1,
    isLoading2,
    error,
    setError,
    fetchSingleRun,
    fetchComparisonRuns,
    clearData,
    clearData1,
    clearData2
  };
};

// Hook for managing graph data
export const useGraphData = () => {
  const [graphData1, setGraphData1] = useState(null);
  const [graphData2, setGraphData2] = useState(null);
  const [isLoadingGraph1, setIsLoadingGraph1] = useState(false);
  const [isLoadingGraph2, setIsLoadingGraph2] = useState(false);
  const [graphError, setGraphError] = useState(null);

  const fetchGraphData = useCallback(async (runId, isSecondId = false) => {
    if (!validation.isValidRunId(runId)) {
      setGraphError(`ID must be exactly 9 characters long.`);
      return;
    }

    const setLoading = isSecondId ? setIsLoadingGraph2 : setIsLoadingGraph1;
    const setData = isSecondId ? setGraphData2 : setGraphData1;

    setLoading(true);
    setGraphError(null);

    try {
      // Data is already cleared by useAppLogic, just fetch new data
      
      const result = await apiService.fetchGraphData(runId);

      if (!result.data_points || Object.keys(result.data_points).length === 0) {
        throw new Error('No data points received from backend');
      }

      setData(result.data_points);

      if (result.missing_data && result.missing_data.length > 0) {
        const missingDataMessage = result.missing_data.join('. ');
        setGraphError(`⚠️ ${missingDataMessage}`);
      }

    } catch (error) {
      console.error('Graph loading error:', error);
      const graphId = isSecondId ? 'ID2' : 'ID1';
      setGraphError(`❌ Error loading graph for ${graphId}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGraphDataComparison = useCallback(async (id1, id2) => {
    const validationResult = validation.validateRunIdsForComparison(id1, id2);
    
    if (!validationResult.hasValidId1) {
      setGraphError('First ID must be exactly 9 characters long.');
      return;
    }

    // Only clear errors, data is already cleared by useAppLogic
    setGraphError(null);

    // Fetch graph data separately
    const promises = [];
    
    // Always fetch ID1 graph data
    setIsLoadingGraph1(true);
    promises.push(
      apiService.fetchGraphData(id1)
        .then(result => {
          if (result.data_points && result.data_points[id1]) {
            setGraphData1({ [id1]: result.data_points[id1] });
          }
          setIsLoadingGraph1(false);
        })
        .catch(error => {
          console.error('Error fetching graph for ID1:', error);
          setGraphError(`ID1 Graph Error: ${error.message}`);
          setIsLoadingGraph1(false);
        })
    );

    // Fetch ID2 graph if valid
    if (validationResult.hasValidId2) {
      setIsLoadingGraph2(true);
      promises.push(
        apiService.fetchGraphData(id2)
          .then(result => {
            if (result.data_points && result.data_points[id2]) {
              setGraphData2({ [id2]: result.data_points[id2] });
            }
            setIsLoadingGraph2(false);
          })
          .catch(error => {
            console.error('Error fetching graph for ID2:', error);
            setGraphError(prevError => prevError ? `${prevError}; ID2 Graph Error: ${error.message}` : `ID2 Graph Error: ${error.message}`);
            setIsLoadingGraph2(false);
          })
      );
    }

    // Wait for all promises to complete
    try {
      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error in graph comparison fetch:', error);
    }
  }, []);

  const clearGraphData = useCallback(() => {
    setGraphData1(null);
    setGraphData2(null);
    setGraphError(null);
  }, []);

  const clearGraphData1 = useCallback(() => {
    setGraphData1(null);
    setGraphError(null);
  }, []);

  const clearGraphData2 = useCallback(() => {
    setGraphData2(null);
    setGraphError(null);
  }, []);

  return {
    graphData1,
    graphData2,
    isLoadingGraph1,
    isLoadingGraph2,
    graphError,
    setGraphError,
    fetchGraphData,
    fetchGraphDataComparison,
    clearGraphData,
    clearGraphData1,
    clearGraphData2
  };
};

// Hook for cache management
export const useCacheStatus = () => {
  const [cacheStatus, setCacheStatus] = useState(null);

  const fetchCacheStatus = useCallback(async () => {
    try {
      const status = await apiService.fetchCacheStatus();
      setCacheStatus(status);
    } catch (error) {
      console.error('Error fetching cache status:', error);
    }
  }, []);

  const clearCache = useCallback(async () => {
    try {
      await apiService.clearCache();
      await fetchCacheStatus(); // Refresh status after clearing
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }, [fetchCacheStatus]);

  useEffect(() => {
    fetchCacheStatus();
  }, [fetchCacheStatus]);

  return {
    cacheStatus,
    fetchCacheStatus,
    clearCache
  };
};

// Hook for compatibility checking
export const useCompatibility = (data1, data2, mode, setRunDataError) => {
  const [comparisonAllowed, setComparisonAllowed] = useState(undefined);

  useEffect(() => {
    if (mode === 'compare' && data1 && data2) {
      const result = compatibilityUtils.checkWorkloadCompatibility(data1, data2);
      setComparisonAllowed(result.compatible);
      
      // Set error message if incompatible
      if (!result.compatible && setRunDataError) {
        if (result.errorType === 'model') {
          setRunDataError('Cannot compare runs with different model types');
        } else if (result.errorType === 'workload') {
          setRunDataError('Cannot compare runs with different workload types');
        }
      } else if (result.compatible && setRunDataError) {
        // Clear error if compatible
        setRunDataError(null);
      }
    } else {
      setComparisonAllowed(undefined);
    }
  }, [data1, data2, mode, setRunDataError]);

  return { comparisonAllowed, setComparisonAllowed };
};

// Re-export the useUIState hook
export { useUIState } from './useUIState';
