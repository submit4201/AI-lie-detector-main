import React from 'react';

const Tooltip = ({ children, text }) => {
  // Very small tooltip using HTML title attribute for tests and accessibility
  return (
    <span title={text} style={{ textDecoration: 'underline dotted', cursor: 'help' }}>
      {children}
    </span>
  );
};

export default Tooltip;
