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
      if (!isSecondId) {
        setData2(null); // Clear data2 only when loading ID1
      }
    } catch (error) {
      console.error('Error fetching run data:', error);
      setError(error.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchComparisonRuns = useCallback(async (id1, id2) => {
    const validationResult = validation.validateRunIds(id1, id2);
    if (!validationResult.isValid) {
      setError(validationResult.errors[0]);
      return;
    }

    setIsLoading1(true);
    setIsLoading2(true);
    setError(null);

    try {
      const result = await apiService.fetchComparisonDetails(id1, id2);

      if (result.id1) {
        setData1(result.id1);
      }
      if (result.id2) {
        setData2(result.id2);
      }

      // Handle errors for individual IDs
      if (result.error_id1) {
        setError(result.error_id1);
      }
      if (result.error_id2) {
        setError(result.error_id2);
      }

      // Handle comparison errors
      if (result.comparison_error) {
        const errorMsg = compatibilityUtils.formatCompatibilityError({
          compatible: false,
          errorType: result.comparison_error.error_type,
          details: {
            workload1: result.comparison_error.workload_id1,
            workload2: result.comparison_error.workload_id2,
            model1: result.comparison_error.model_id1,
            model2: result.comparison_error.model_id2
          }
        });
        setError(errorMsg);
        return { comparisonAllowed: false };
      }

      return { comparisonAllowed: true };
    } catch (error) {
      console.error('Error fetching comparison data:', error);
      setError(error.message);
      setData1(null);
      setData2(null);
      return { comparisonAllowed: false };
    } finally {
      setIsLoading1(false);
      setIsLoading2(false);
    }
  }, []);

  const clearData = useCallback(() => {
    setData1(null);
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
    clearData
  };
};

// Hook for managing graph data
export const useGraphData = () => {
  const [graphData1, setGraphData1] = useState(null);
  const [graphData2, setGraphData2] = useState(null);
  const [isLoadingGraph1, setIsLoadingGraph1] = useState(false);
  const [isLoadingGraph2, setIsLoadingGraph2] = useState(false);
  const [isLoadingGraph, setIsLoadingGraph] = useState(false);
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
    const validationResult = validation.validateRunIds(id1, id2);
    if (!validationResult.isValid) {
      setGraphError(validationResult.errors[0]);
      return;
    }

    setIsLoadingGraph(true);
    setGraphError(null);

    try {
      const result = await apiService.fetchGraphDataComparison(id1, id2);

      if (!result.data_points || Object.keys(result.data_points).length === 0) {
        throw new Error('No data points received from backend');
      }

      if (result.data_points[id1]) {
        setGraphData1({ [id1]: result.data_points[id1] });
      }
      if (result.data_points[id2]) {
        setGraphData2({ [id2]: result.data_points[id2] });
      }

      // Handle different types of warnings/messages
      if (result.compatibility_warning) {
        const warningMsg = result.compatibility_warning.message;
        setGraphError(`⚠️ ${warningMsg}`);
      } else if (result.missing_data && result.missing_data.length > 0) {
        const missingDataMessage = result.missing_data.join('. ');
        setGraphError(`⚠️ ${missingDataMessage}`);
      }

    } catch (error) {
      console.error('Graph loading error:', error);
      setGraphError(`Error loading graph: ${error.message}`);
    } finally {
      setIsLoadingGraph(false);
    }
  }, []);

  const clearGraphData = useCallback(() => {
    setGraphData1(null);
    setGraphData2(null);
    setGraphError(null);
  }, []);

  return {
    graphData1,
    graphData2,
    isLoadingGraph1,
    isLoadingGraph2,
    isLoadingGraph,
    graphError,
    setGraphError,
    fetchGraphData,
    fetchGraphDataComparison,
    clearGraphData
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
export const useCompatibility = (data1, data2, mode) => {
  const [comparisonAllowed, setComparisonAllowed] = useState(undefined);

  useEffect(() => {
    if (mode === 'compare' && data1 && data2) {
      const result = compatibilityUtils.checkWorkloadCompatibility(data1, data2);
      setComparisonAllowed(result.compatible);
    } else {
      setComparisonAllowed(undefined);
    }
  }, [data1, data2, mode]);

  return { comparisonAllowed, setComparisonAllowed };
};
