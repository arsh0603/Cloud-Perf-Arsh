import React from 'react';
import { urlUtils } from '../utils/helpers';

const DataTable = ({
  mode,
  data1,
  data2,
  isLoading1,
  isLoading2,
  submittedId1,
  submittedId2,
  error
}) => {
    
  return (
    <div className="table-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
      <table className="data-table compact">
        <thead>
          <tr>
            <th>Metric</th>
            <th>
              ID1: {isLoading1 ? 'Loading...' : submittedId1}
            </th>
            {mode === 'compare' && (
              <th>
                ID2: {isLoading2 ? 'Loading...' : submittedId2}
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {/* Show error message when there's an error but no successful data loads */}
          {error && !data1 && !data2 && !isLoading1 && !isLoading2 && (submittedId1 || submittedId2) && (
            <tr>
              <td colSpan={mode === 'compare' ? 3 : 2} style={{ textAlign: 'center', color: '#ef4444', padding: '1rem' }}>
                ❌ Error: {error}
              </td>
            </tr>
          )}
          
          {/* Show error for specific ID when one ID fails but the other succeeds in compare mode */}
          {mode === 'compare' && error && ((submittedId1 && !data1 && !isLoading1) || (submittedId2 && !data2 && !isLoading2)) && (data1 || data2) && (
            <tr>
              <td colSpan={3} style={{ textAlign: 'center', color: '#ef4444', padding: '1rem' }}>
                ❌ {error}
              </td>
            </tr>
          )}
          
          {/* Generate rows based on available data */}
          {(() => {
            // For comparison mode, merge all unique fields from both datasets
            // For single mode, use the available dataset
            if (mode === 'compare' && (data1 || data2)) {
              // Get all unique fields from both datasets
              const fields1 = data1 ? Object.keys(data1) : [];
              const fields2 = data2 ? Object.keys(data2) : [];
              const allFields = [...new Set([...fields1, ...fields2])].sort();
              
              if (allFields.length === 0) return null;
              
              return allFields.map((key) => {
                const value1 = data1?.[key];
                const value2 = data2?.[key];
                
                return (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>
                      {isLoading1 ? (
                        'Loading...'
                      ) : (
                        value1 || 'N/A'
                      )}
                    </td>
                    <td>
                      {isLoading2 ? (
                        'Loading...'
                      ) : (
                        value2 || 'N/A'
                      )}
                    </td>
                  </tr>
                );
              });
            } else {
              // Single mode - use whichever data is available
              const baseData = data1 || data2;
              if (!baseData) return null;
              
              return Object.keys(baseData).map((key) => {
                const value1 = data1?.[key];
                
                return (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>
                      {isLoading1 ? (
                        'Loading...'
                      ) : (
                        value1 || 'N/A'
                      )}
                    </td>
                  </tr>
                );
              });
            }
          })()}
          
          {/* Always show Test Harness Log row when we have any data */}
          {(data1 || data2) && (
            <tr>
              <td><strong>Test Harness Log</strong></td>
              <td>
                {isLoading1 ? (
                  'Loading...'
                ) : data1 ? (
                  <a 
                    href={urlUtils.generatePerfwebLink(submittedId1)} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="perfweb-link"
                    style={{ 
                      color: '#2563eb', 
                      textDecoration: 'none',
                      fontSize: '0.875rem'
                    }}
                  >
                    📋 Test Harness Log
                  </a>
                ) : (
                  'N/A'
                )}
              </td>
              {mode === 'compare' && (
                <td>
                  {isLoading2 ? (
                    'Loading...'
                  ) : data2 && submittedId2 ? (
                    <a 
                      href={urlUtils.generatePerfwebLink(submittedId2)} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="perfweb-link"
                      style={{ 
                        color: '#2563eb', 
                        textDecoration: 'none',
                        fontSize: '0.875rem'
                      }}
                    >
                      📋 Test Harness Log
                    </a>
                  ) : (
                    'N/A'
                  )}
                </td>
              )}
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
