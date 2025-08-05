import React from 'react';
import { CompatibilityStatus, DataTable } from '../components';
import { CSS_CLASSES } from '../constants/appConstants';

const DataSection = ({ 
  mode, 
  runDataProps, 
  compatibilityProps, 
  submittedIds 
}) => {
  const { data1, data2, isLoading1, isLoading2, error } = runDataProps;
  const { submittedId1, submittedId2 } = submittedIds;

  return (
    <div className={CSS_CLASSES.DATA_SECTION}>
      <div className={CSS_CLASSES.DASHBOARD_CARD}>
        <h3 className={CSS_CLASSES.CARD_TITLE}>Performance Data</h3>
        
        <CompatibilityStatus
          mode={mode}
          data1={data1}
          data2={data2}
          isLoading1={isLoading1}
          isLoading2={isLoading2}
          submittedId2={submittedId2}
          comparisonAllowed={compatibilityProps.comparisonAllowed}
          error={error}
        />
        
        <DataTable
          mode={mode}
          data1={data1}
          data2={data2}
          isLoading1={isLoading1}
          isLoading2={isLoading2}
          submittedId1={submittedId1}
          submittedId2={submittedId2}
          error={error}
        />
      </div>
    </div>
  );
};

export default DataSection;
