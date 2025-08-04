import React from 'react';
import { urlUtils, dataUtils } from '../utils/helpers';

const DataTable = ({
  mode,
  data1,
  data2,
  isLoading1,
  isLoading2,
  submittedId1,
  submittedId2
}) => {
  return (
    <div className="table-container">
      <table className="data-table compact">
        <thead>
          <tr>
            <th>Metric</th>
            <th>
              ID1: {isLoading1 ? 'Loading...' : submittedId1}
              {!isLoading1 && submittedId1 && (
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
                ID2: {isLoading2 ? 'Loading...' : submittedId2}
                {!isLoading2 && submittedId2 && (
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
          {data1 && Object.keys(data1).map((key) => {
            const value1 = data1[key];
            const value2 = data2?.[key];
            const renderedValue1 = dataUtils.renderValue(value1, key);
            const renderedValue2 = dataUtils.renderValue(value2, key);
            
            return (
              <tr key={key}>
                <td><strong>{key}</strong></td>
                <td>
                  {isLoading1 ? (
                    'Loading...'
                  ) : (
                    renderedValue1.isLink ? (
                      <a 
                        href={renderedValue1.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="data-link"
                        style={{ 
                          color: '#2563eb', 
                          textDecoration: 'none',
                          fontSize: '0.875rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        {renderedValue1.text}
                      </a>
                    ) : (
                      renderedValue1.text
                    )
                  )}
                </td>
                {mode === 'compare' && (
                  <td>
                    {isLoading2 ? (
                      'Loading...'
                    ) : (
                      renderedValue2.isLink ? (
                        <a 
                          href={renderedValue2.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="data-link"
                          style={{ 
                            color: '#2563eb', 
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          {renderedValue2.text}
                        </a>
                      ) : (
                        renderedValue2.text
                      )
                    )}
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
