import React from 'react';
import { ModeSelector, RunIdInput } from './index';

const ControlPanel = ({
  mode,
  id1,
  id2,
  onModeChange,
  onId1Change,
  onId2Change,
  onSubmit,
  isLoading1,
  isLoading2,
  inputError
}) => {
  return (
    <div className="top-panel">
      <div className="dashboard-card">
        <div className="controls-row horizontal-flex">
          <ModeSelector 
            mode={mode} 
            onModeChange={onModeChange} 
          />
          
          <RunIdInput
            mode={mode}
            id1={id1}
            id2={id2}
            onId1Change={onId1Change}
            onId2Change={onId2Change}
            onSubmit={onSubmit}
            isLoading1={isLoading1}
            isLoading2={isLoading2}
            inputError={inputError}
          />
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;
