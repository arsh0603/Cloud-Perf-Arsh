import React from 'react';

const ErrorDisplay = ({ inputError, error, graphError }) => {
  return (
    <>
      {inputError && <div className="error">⚠️ {inputError}</div>}
      {error && <div className="warning">⚠️ {error}</div>}
      {graphError && <div className="error">❌ {graphError}</div>}
    </>
  );
};

export default ErrorDisplay;
