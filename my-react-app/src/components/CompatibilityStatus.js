import React from 'react';

const CompatibilityStatus = ({
  mode,
  data1,
  data2,
  isLoading1,
  isLoading2,
  submittedId2,
  comparisonAllowed,
  error
}) => {
  if (mode !== 'compare' || (!data1 && !data2) || isLoading1 || isLoading2) {
    return null;
  }

  return (
    <div className={`compatibility-status compact ${
      data1 && data2 
        ? (!comparisonAllowed ? 'incompatible' : 'compatible')
        : 'neutral'
    }`}>
      {data1 && data2 ? (
        // Both data available - show compatibility
        !comparisonAllowed ? (
          <>
            {error && error.includes('model types') ? (
              <>
                ⚠️ <strong>Model Incompatibility:</strong> Different model types 
                ({data1['Model']} vs {data2['Model']}).
              </>
            ) : error && error.includes('workload types') ? (
              <>
                ⚠️ <strong>Workload Incompatibility:</strong> Different workload types 
                ({data1['Workload Type']} vs {data2['Workload Type']}).
              </>
            ) : (
              <>
                ⚠️ <strong>Incompatible:</strong> {error || 'Cannot compare these runs.'}
              </>
            )}
          </>
        ) : comparisonAllowed === true ? (
          <>
            ✅ <strong>Compatible:</strong> {data1['Workload Type']} / {data1['Model']}
          </>
        ) : (
          <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
            ⏳ Checking compatibility...
          </div>
        )
      ) : (
        // Handle single ID cases in compare mode
        data1 && !data2 ? (
          // Only ID1 data available
          <>
            📋 <strong>ID1 Data Loaded:</strong> {data1['Workload Type']} / {data1['Model']}
            {submittedId2 && (
              <span style={{ color: '#9ca3af', marginLeft: '10px' }}>
                (Waiting for ID2...)
              </span>
            )}
          </>
        ) : !data1 && data2 ? (
          // Only ID2 data available
          <>
            📋 <strong>ID2 Data Loaded:</strong> {data2['Workload Type']} / {data2['Model']}
            <span style={{ color: '#9ca3af', marginLeft: '10px' }}>
              (Enter ID1 to compare...)
            </span>
          </>
        ) : null
      )}
    </div>
  );
};

export default CompatibilityStatus;
