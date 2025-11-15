import React from 'react';

const LoadingSpinner = ({ size = 'md', message = 'Loading...', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={`flex flex-col items-center justify-center p-4 ${className}`}>
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-purple-500/30 border-t-purple-400`}></div>
      {message && (
        <p className="text-gray-400 text-sm mt-2 animate-pulse">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
