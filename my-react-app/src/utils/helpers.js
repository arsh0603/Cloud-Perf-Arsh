// Utility functions for the application

// Validation utilities
export const validation = {
  isValidRunId: (id) => {
    return typeof id === 'string' && id.length === 9;
  },

  validateRunIds: (...ids) => {
    const errors = [];
    ids.forEach((id, index) => {
      if (!validation.isValidRunId(id)) {
        errors.push(`ID ${index + 1} must be exactly 9 characters long.`);
      }
    });
    return {
      isValid: errors.length === 0,
      errors
    };
  }
};

// URL generation utilities
export const urlUtils = {
  generatePerfwebLink: (runId) => {
    if (!runId || runId.length < 4) return null;
    const yearMonth = runId.substring(0, 4);
    return `http://perfweb.gdl.englab.netapp.com/cgi-bin/perfcloud/view.cgi?p=/x/eng/perfcloud/RESULTS/${yearMonth}/${runId}/cloud_test_harness.log`;
  }
};

// Data processing utilities
export const dataUtils = {
  convertThroughputToMB: (throughputBytes) => {
    return throughputBytes / (1024 * 1024);
  },

  formatThroughput: (throughput, showInMB = true) => {
    if (showInMB) {
      return `${dataUtils.convertThroughputToMB(throughput).toFixed(2)} MB/s`;
    }
    return `${throughput.toLocaleString()} bytes/sec`;
  },

  isEmpty: (value) => {
    return value === null || value === undefined || value === '';
  },

  safeGet: (obj, key, defaultValue = 'N/A') => {
    const value = obj?.[key];
    return dataUtils.isEmpty(value) ? defaultValue : value;
  }
};

// Compatibility checking utilities
export const compatibilityUtils = {
  checkWorkloadCompatibility: (data1, data2) => {
    if (!data1 || !data2) return { compatible: true };

    const workload1 = data1['Workload Type'];
    const workload2 = data2['Workload Type'];
    const model1 = data1['Model'];
    const model2 = data2['Model'];

    // Check workload compatibility first
    if (workload1 && workload2 && workload1 !== workload2) {
      return {
        compatible: false,
        errorType: 'workload',
        message: 'Cannot compare runs with different workload types',
        details: { workload1, workload2, model1, model2 }
      };
    }

    // Check model compatibility
    if (model1 && model2 && model1 !== model2) {
      return {
        compatible: false,
        errorType: 'model',
        message: 'Cannot compare runs with different model types',
        details: { workload1, workload2, model1, model2 }
      };
    }

    return {
      compatible: true,
      details: { workload1, workload2, model1, model2 }
    };
  },

  formatCompatibilityError: (compatibilityResult) => {
    if (compatibilityResult.compatible) return null;

    const { errorType, details } = compatibilityResult;
    
    if (errorType === 'workload') {
      return `⚠️ Cannot compare runs with different workload types: ID1 workload (${details.workload1}) vs ID2 workload (${details.workload2})`;
    } else if (errorType === 'model') {
      return `⚠️ Cannot compare runs with different model types: ID1 model (${details.model1}) vs ID2 model (${details.model2})`;
    }

    return null;
  }
};

// Chart utilities
export const chartUtils = {
  generateColors: (index, offset = 0) => {
    const hue = (index * 137.508 + offset) % 360;
    return {
      border: `hsla(${hue}, 70%, 50%, 1)`,
      background: `hsla(${hue}, 70%, 50%, 0.1)`
    };
  },

  formatChartData: (graphData, runIdPrefix, showThroughputInMB = true) => {
    if (!graphData) return [];

    return Object.keys(graphData).map((runId, index) => {
      const colors = chartUtils.generateColors(index, runIdPrefix === 'ID2' ? 60 : 0);
      
      return {
        label: `${runIdPrefix} - Run ${runId}`,
        data: graphData[runId].map((point, pointIndex) => ({
          x: showThroughputInMB ? dataUtils.convertThroughputToMB(point.throughput) : point.throughput,
          y: point.latency,
          label: `Iteration ${pointIndex + 1}`
        })),
        borderColor: colors.border,
        backgroundColor: colors.background,
        fill: false,
        tension: 0.1,
        pointRadius: 4,
        pointHoverRadius: 6
      };
    });
  },

  prepareChartData: (graphData1, graphData2, showThroughputInMB = true) => {
    const datasets = [];
    
    if (graphData1) {
      datasets.push(...chartUtils.formatChartData(graphData1, 'ID1', showThroughputInMB));
    }
    
    if (graphData2) {
      datasets.push(...chartUtils.formatChartData(graphData2, 'ID2', showThroughputInMB));
    }
    
    return { datasets };
  },

  getChartOptions: (showThroughputInMB = true) => ({
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
        grid: { color: CONSTANTS.CHART_COLORS.GRID }
      },
      y: {
        title: {
          display: true,
          text: 'Latency (μs)',
          font: { size: 12, weight: 'bold' }
        },
        grid: { color: CONSTANTS.CHART_COLORS.GRID }
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
        backgroundColor: CONSTANTS.CHART_COLORS.TOOLTIP_BG,
        titleColor: CONSTANTS.CHART_COLORS.TOOLTIP_TEXT,
        bodyColor: CONSTANTS.CHART_COLORS.TOOLTIP_TEXT,
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
  })
};

// Constants
export const CONSTANTS = {
  RUN_ID_LENGTH: 9,
  LOADING_TIMEOUT: 100,
  MAX_CACHE_SIZE: 20,
  CHART_COLORS: {
    GRID: '#f3f4f6',
    TOOLTIP_BG: 'rgba(0, 0, 0, 0.8)',
    TOOLTIP_TEXT: 'white'
  }
};

export default {
  validation,
  urlUtils,
  dataUtils,
  compatibilityUtils,
  chartUtils,
  CONSTANTS
};
