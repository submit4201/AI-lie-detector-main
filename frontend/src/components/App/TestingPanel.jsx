import React from 'react';
import { sampleAnalysisResult, sampleSessionHistory } from '../../data/sampleAnalysisData';

const TestingPanel = ({ onLoadSampleData, className = "" }) => {
  const handleLoadSample = () => {
    onLoadSampleData(sampleAnalysisResult, sampleSessionHistory);
  };

  const handleClearData = () => {
    onLoadSampleData(null, []);
  };
  return (
    <div className={`section-container glow-purple ${className}`}>
      <h3 className="text-lg font-semibold text-purple-300 mb-3">🧪 Testing Panel</h3>
      <p className="text-gray-300 text-sm mb-4">
        Load sample analysis data to test the enhanced interface without uploading audio.
      </p>
      <div className="flex gap-3">
        <button
          onClick={handleLoadSample}
          className="btn glow-purple bg-purple-600/50 hover:bg-purple-600/70 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-purple-500/50 text-sm"
        >
          Load Sample Data
        </button>
        <button
          onClick={handleClearData}
          className="btn bg-gray-600/50 hover:bg-gray-600/70 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-gray-500/50 text-sm"
        >
          Clear Data
        </button>
      </div>
      <div className="mt-3 text-xs text-gray-400">
        Sample includes: Full analysis • Session history • All enhanced features
      </div>
    </div>
  );
};

export default TestingPanel;
