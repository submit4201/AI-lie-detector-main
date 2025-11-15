import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const SessionHistorySection = ({ sessionHistory, sessionId, onSelectHistoryItem }) => {
  const [expandedItem, setExpandedItem] = useState(null);
  if (!sessionHistory || sessionHistory.length === 0) {
    return (
      <Card className="section-container session-history">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-purple-300 mb-4 flex items-center">
            <span className="mr-2">📜</span>
            Session History
          </h3>
          <div className="text-center py-8">
            <p className="text-gray-400">No previous analyses in this session.</p>
            <p className="text-sm text-gray-500 mt-2">
              Upload audio files to build analysis history.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown time';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getCredibilityColor = (score) => {
    if (typeof score !== 'number') return 'gray';
    if (score < 40) return 'red';
    if (score < 70) return 'yellow';
    return 'green';
  };

  const getRiskColor = (risk) => {
    if (!risk) return 'gray';
    const level = risk.toLowerCase();
    if (level === 'high') return 'red';
    if (level === 'medium') return 'yellow';
    if (level === 'low') return 'green';
    return 'gray';
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text || typeof text !== 'string') return 'No transcript available';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };
  return (
    <Card className="section-container session-history">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-purple-300 mb-4 flex items-center">
          <span className="mr-2">📜</span>
          Session History
        </h3>
        
        <div className="text-sm text-gray-400 mb-4">
          Session ID: <span className="font-mono text-purple-300">{sessionId}</span>
        </div>

        <div className="space-y-4">
          {sessionHistory.map((item, index) => (
            <div
              key={index}
              className="bg-black/30 border border-gray-600/30 rounded-lg p-4 hover:border-purple-400/50 transition-all duration-200"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-purple-300 font-medium">
                    Analysis #{sessionHistory.length - index}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {formatTimestamp(item.timestamp)}
                  </Badge>
                </div>
                <button
                  onClick={() => setExpandedItem(expandedItem === index ? null : index)}
                  className="text-gray-400 hover:text-purple-300 text-sm"
                >
                  {expandedItem === index ? '▼ Collapse' : '▶ Expand'}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                {/* Credibility Score */}
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Credibility:</span>
                  <Badge className={`bg-${getCredibilityColor(item.credibility_score)}-500/30 text-${getCredibilityColor(item.credibility_score)}-200 border-${getCredibilityColor(item.credibility_score)}-400/50`}>
                    {typeof item.credibility_score === 'number' ? `${item.credibility_score.toFixed(0)}%` : 'N/A'}
                  </Badge>
                </div>

                {/* Risk Level */}
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Risk:</span>
                  <Badge className={`bg-${getRiskColor(item.risk_level)}-500/30 text-${getRiskColor(item.risk_level)}-200 border-${getRiskColor(item.risk_level)}-400/50`}>
                    {item.risk_level || 'N/A'}
                  </Badge>
                </div>

                {/* Primary Emotion */}
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Emotion:</span>
                  <Badge variant="outline" className="text-blue-200">
                    {item.primary_emotion || 'N/A'}
                  </Badge>
                </div>
              </div>

              {/* Transcript Preview */}
              <div className="mb-3">
                <span className="text-gray-400 text-sm">Transcript: </span>
                <span className="text-gray-200">
                  {truncateText(item.transcript_summary || item.transcript)}
                </span>
              </div>

              {/* Expanded Details */}
              {expandedItem === index && (
                <div className="mt-4 pt-4 border-t border-gray-600/30">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Key Analysis Points */}
                    {item.key_analysis_points && (
                      <div>
                        <h5 className="text-purple-300 font-medium mb-2">Key Analysis Points:</h5>
                        <ul className="text-sm text-gray-300 space-y-1">
                          {item.key_analysis_points.map((point, i) => (
                            <li key={i} className="flex items-start">
                              <span className="text-purple-400 mr-2">•</span>
                              {point}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Red Flags */}
                    {item.red_flags && item.red_flags.length > 0 && (
                      <div>
                        <h5 className="text-red-300 font-medium mb-2">Red Flags:</h5>
                        <ul className="text-sm text-gray-300 space-y-1">
                          {item.red_flags.map((flag, i) => (
                            <li key={i} className="flex items-start">
                              <span className="text-red-400 mr-2">⚠</span>
                              {flag}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Full Transcript */}
                  {item.transcript && expandedItem === index && (
                    <div className="mt-4">
                      <h5 className="text-purple-300 font-medium mb-2">Full Transcript:</h5>
                      <div className="bg-black/40 p-3 rounded border border-gray-600/30 text-sm text-gray-200 max-h-40 overflow-y-auto">
                        {item.transcript}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="mt-4 flex space-x-2">
                    {onSelectHistoryItem && (
                      <button
                        onClick={() => onSelectHistoryItem(item)}
                        className="px-3 py-1 bg-purple-500/30 text-purple-200 rounded hover:bg-purple-500/50 transition-colors text-sm"
                      >
                        View Details
                      </button>
                    )}
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(item, null, 2));
                        // Could add a toast notification here
                      }}
                      className="px-3 py-1 bg-gray-500/30 text-gray-200 rounded hover:bg-gray-500/50 transition-colors text-sm"
                    >
                      Copy Data
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary Statistics */}
        <div className="mt-6 pt-4 border-t border-gray-600/30">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-purple-300">{sessionHistory.length}</div>
              <div className="text-xs text-gray-400">Total Analyses</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-green-300">
                {sessionHistory.filter(item => (item.credibility_score || 0) >= 70).length}
              </div>
              <div className="text-xs text-gray-400">High Credibility</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-red-300">
                {sessionHistory.filter(item => (item.risk_level || '').toLowerCase() === 'high').length}
              </div>
              <div className="text-xs text-gray-400">High Risk</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-blue-300">
                {sessionHistory.reduce((avg, item) => avg + (item.credibility_score || 0), 0) / sessionHistory.length || 0}%
              </div>
              <div className="text-xs text-gray-400">Avg Credibility</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SessionHistorySection;
