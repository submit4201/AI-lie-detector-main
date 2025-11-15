import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

const ErrorDisplay = ({ 
  error, 
  onRetry, 
  title = "Something went wrong",
  description = "An error occurred while processing your request.",
  className = ""
}) => {
  return (
    <Card className={`bg-red-900/20 backdrop-blur-sm border border-red-500/30 ${className}`}>
      <CardContent className="p-6 text-center">
        <div className="text-red-400 text-4xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-300 mb-2">{title}</h3>
        <p className="text-gray-300 mb-4">{description}</p>
        
        {error && (
          <details className="bg-black/30 rounded-lg p-3 mb-4 text-left">
            <summary className="text-red-400 cursor-pointer hover:text-red-300 transition-colors">
              View Technical Details
            </summary>
            <pre className="text-xs text-gray-400 mt-2 overflow-auto max-h-40">
              {typeof error === 'string' ? error : JSON.stringify(error, null, 2)}
            </pre>
          </details>
        )}
        
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-red-600/50 hover:bg-red-600/70 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-red-500/50"
          >
            Try Again
          </button>
        )}
      </CardContent>
    </Card>
  );
};

export default ErrorDisplay;
