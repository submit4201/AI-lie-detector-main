import React from 'react';
import { Badge } from './badge';

const ConfidenceChip = ({ value = 0 }) => {
  const percent = Math.round(value);
  const label = percent >= 75 ? 'High' : percent >= 50 ? 'Medium' : 'Low';
  const variant = percent >= 75 ? 'success' : percent >= 50 ? 'warning' : 'destructive';
  return (<Badge variant={variant} className="ml-2">{label} {percent >= 0 ? `${percent}%` : ''}</Badge>);
};

export default ConfidenceChip;
