import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <img src="/netapp.png" alt="NetApp Logo" className="logo-image" />
        </div>
        <h1 className="header-title">Perf Data Visualization</h1>
      </div>
    </header>
  );
};

export default Header;
