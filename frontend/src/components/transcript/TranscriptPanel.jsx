import React from 'react';

const TranscriptPanel = ({ transcriptText, isStreaming, lastReceivedComponent }) => {
  if (!transcriptText) return null;

  const live = isStreaming && lastReceivedComponent === 'transcript';

  return (
    <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${live ? 'just-received' : ''}`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-2 h-2 rounded-full ${live ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`}></div>
        <h3 className="text-lg font-semibold text-white">Conversation Transcript</h3>
        {isStreaming && live && <span className="component-received-badge">• Live</span>}
        {!isStreaming && <span className="component-final-badge">• Final</span>}
      </div>
      <div className="text-gray-300 bg-black/20 p-3 rounded border-l-4 border-green-400">
        <p aria-live={isStreaming ? 'polite' : 'off'}>{transcriptText}</p>
      </div>
    </div>
  );
};

export default TranscriptPanel;