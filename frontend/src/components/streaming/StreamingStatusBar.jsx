import React from 'react';

const StreamingStatusBar = ({ state, onStop, onReset }) => {
  const { status, progress, lastReceived, lastReceivedAt } = state || {};
  return (
    <div className="bg-black/30 border border-white/10 rounded-lg p-3 flex items-center gap-4">
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${status === 'streaming' ? 'bg-blue-400 animate-pulse' : status === 'completed' ? 'bg-green-400' : 'bg-gray-500'}`} />
          <div className="text-sm text-white font-medium">{status === 'streaming' ? 'Streaming' : status === 'completed' ? 'Completed' : 'Idle'}</div>
          <div className="ml-auto text-xs text-gray-300">Progress: {progress ?? 0}%</div>
        </div>
        <div className="text-xs text-gray-400 mt-1" aria-live="polite" data-timestamp={lastReceivedAt} data-testid="stream-last-received">
          Last received: {lastReceived ?? '—'} {lastReceivedAt ? `• ${new Date(lastReceivedAt).toLocaleTimeString()}` : ''}
        </div>
      </div>
      <div className="flex gap-2">
        {status === 'streaming' && (
          <button onClick={onStop} className="px-3 py-1 bg-red-500 text-white rounded">Stop</button>
        )}
        <button onClick={onReset} className="px-3 py-1 bg-gray-800 text-white rounded">Reset</button>
      </div>
    </div>
  );
};

export default StreamingStatusBar;
