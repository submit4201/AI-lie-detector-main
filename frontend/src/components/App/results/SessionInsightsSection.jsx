import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";

const SessionInsightsSection = ({ result, sessionHistory }) => {
  const [activeTab, setActiveTab] = useState('insights');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  
  if (!result) return null;

  // Check if we have session insights from the structured data
  const hasSessionInsights = result.session_insights && (
    result.session_insights.consistency_analysis ||
    result.session_insights.behavioral_evolution ||
    result.session_insights.risk_trajectory ||
    result.session_insights.conversation_dynamics
  );

  // Check if we have session history for analysis
  const hasSessionHistory = sessionHistory && sessionHistory.length > 1;

  // Calculate session statistics
  const sessionStats = hasSessionHistory ? {
    totalAnalyses: sessionHistory.length,
    avgCredibility: Math.round(sessionHistory.reduce((sum, item) => sum + (item.analysis?.credibility_score || 0), 0) / sessionHistory.length),
    totalWords: sessionHistory.reduce((sum, item) => sum + (item.transcript?.split(' ').length || 0), 0),
    credibilityTrend: (() => {
      const scores = sessionHistory.map(item => item.analysis?.credibility_score || 0);
      if (scores.length < 2) return { direction: 'stable', value: 0, icon: '📊' };
      const first = scores[0];
      const last = scores[scores.length - 1];
      const change = last - first;
      return {
        direction: change > 10 ? 'up' : change < -10 ? 'down' : 'stable',
        value: change,
        icon: change > 10 ? '📈' : change < -10 ? '📉' : '📊',
        description: change > 10 ? 'Improving' : change < -10 ? 'Declining' : 'Stable'
      };
    })(),
    riskProgression: sessionHistory.map(item => item.analysis?.overall_risk || 'Unknown'),
    emotionalStates: sessionHistory.map(item => item.analysis?.top_emotion || 'neutral'),
    // Enhanced metrics
    avgWordsPerAnalysis: Math.round(sessionHistory.reduce((sum, item) => sum + (item.transcript?.split(' ').length || 0), 0) / sessionHistory.length),
    consistencyScore: (() => {
      const scores = sessionHistory.map(item => item.analysis?.credibility_score || 0);
      if (scores.length < 2) return 100;
      const variance = scores.reduce((sum, score) => sum + Math.pow(score - scores.reduce((a, b) => a + b) / scores.length, 2), 0) / scores.length;
      return Math.max(0, Math.round(100 - variance));
    })(),
    sessionDuration: (() => {
      if (sessionHistory.length < 2) return 'N/A';
      const first = new Date(sessionHistory[0].timestamp);
      const last = new Date(sessionHistory[sessionHistory.length - 1].timestamp);
      const diffMinutes = Math.round((last - first) / (1000 * 60));
      return diffMinutes > 0 ? `${diffMinutes}m` : '<1m';
    })()
  } : null;
  if (!hasSessionInsights && !hasSessionHistory) {
    return (
      <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
            <h3 className="text-xl font-semibold text-white">Session Intelligence</h3>
          </div>
          <div className="bg-blue-500/10 backdrop-blur-sm border border-blue-400/30 rounded-lg p-6 text-center">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🧠</span>
            </div>
            <p className="text-blue-200 text-lg font-medium mb-2">
              Building Session Intelligence...
            </p>
            <p className="text-blue-300/70 text-sm">
              Advanced insights will be available after multiple analyses in the same session
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }
  return (
    <div className="space-y-6">
      {/* Enhanced Session Intelligence Dashboard */}
      {(hasSessionInsights || hasSessionHistory) && (
        <Card className="bg-gradient-to-br from-slate-900/40 to-slate-800/40 backdrop-blur-md border-white/20 shadow-xl">
          <CardContent className="p-0">
            {/* Header with Tabs */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-xl">🧠</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Session Intelligence</h3>
                  <p className="text-sm text-gray-400">
                    {hasSessionHistory && `${sessionStats.totalAnalyses} analyses • ${sessionStats.totalWords} words processed`}
                  </p>
                </div>
              </div>
              
              {/* Tab Navigation */}
              <div className="flex space-x-1 bg-black/20 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('insights')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'insights'
                      ? 'bg-white/20 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-white/10'
                  }`}
                >
                  AI Insights
                </button>
                {hasSessionHistory && (
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      activeTab === 'analytics'
                        ? 'bg-white/20 text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    Analytics
                  </button>
                )}
                {hasSessionHistory && (
                  <button
                    onClick={() => setActiveTab('timeline')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      activeTab === 'timeline'
                        ? 'bg-white/20 text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    Timeline
                  </button>
                )}
              </div>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {/* AI Insights Tab */}
              {activeTab === 'insights' && hasSessionInsights && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Consistency Analysis */}
                    {result.session_insights.consistency_analysis && (
                      <div className="bg-gradient-to-br from-green-900/20 to-green-800/20 backdrop-blur-sm p-6 rounded-lg border border-green-400/30 hover:border-green-400/50 transition-all">
                        <div className="flex items-center space-x-3 mb-4">
                          <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                            <span className="text-lg">🎯</span>
                          </div>
                          <span className="font-semibold text-green-300 text-lg">Consistency Analysis</span>
                        </div>
                        <p className="text-gray-200 leading-relaxed">
                          {result.session_insights.consistency_analysis}
                        </p>
                      </div>
                    )}

                    {/* Behavioral Evolution */}
                    {result.session_insights.behavioral_evolution && (
                      <div className="bg-gradient-to-br from-blue-900/20 to-blue-800/20 backdrop-blur-sm p-6 rounded-lg border border-blue-400/30 hover:border-blue-400/50 transition-all">
                        <div className="flex items-center space-x-3 mb-4">
                          <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
                            <span className="text-lg">📊</span>
                          </div>
                          <span className="font-semibold text-blue-300 text-lg">Behavioral Evolution</span>
                        </div>
                        <p className="text-gray-200 leading-relaxed">
                          {result.session_insights.behavioral_evolution}
                        </p>
                      </div>
                    )}

                    {/* Risk Trajectory */}
                    {result.session_insights.risk_trajectory && (
                      <div className="bg-gradient-to-br from-yellow-900/20 to-orange-800/20 backdrop-blur-sm p-6 rounded-lg border border-yellow-400/30 hover:border-yellow-400/50 transition-all">
                        <div className="flex items-center space-x-3 mb-4">
                          <div className="w-8 h-8 bg-yellow-500/20 rounded-full flex items-center justify-center">
                            <span className="text-lg">⚠️</span>
                          </div>
                          <span className="font-semibold text-yellow-300 text-lg">Risk Trajectory</span>
                        </div>
                        <p className="text-gray-200 leading-relaxed">
                          {result.session_insights.risk_trajectory}
                        </p>
                      </div>
                    )}

                    {/* Conversation Dynamics */}
                    {result.session_insights.conversation_dynamics && (
                      <div className="bg-gradient-to-br from-purple-900/20 to-purple-800/20 backdrop-blur-sm p-6 rounded-lg border border-purple-400/30 hover:border-purple-400/50 transition-all">
                        <div className="flex items-center space-x-3 mb-4">
                          <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                            <span className="text-lg">💬</span>
                          </div>
                          <span className="font-semibold text-purple-300 text-lg">Conversation Dynamics</span>
                        </div>
                        <p className="text-gray-200 leading-relaxed">
                          {result.session_insights.conversation_dynamics}
                        </p>
                      </div>
                    )}
                  </div>
                </div>              )}              {/* Analytics Tab */}
              {activeTab === 'analytics' && hasSessionHistory && (
                <div className="space-y-6">
                  {/* Enhanced Key Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-cyan-900/20 to-cyan-800/20 p-4 rounded-lg border border-cyan-400/30 hover:border-cyan-400/50 transition-all">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-cyan-300">{sessionStats.totalAnalyses}</div>
                        <div className="text-xs text-gray-400 mt-1">Total Analyses</div>
                        <div className="text-xs text-cyan-300 mt-2">{sessionStats.sessionDuration} session</div>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-emerald-900/20 to-emerald-800/20 p-4 rounded-lg border border-emerald-400/30 hover:border-emerald-400/50 transition-all">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-emerald-300">{sessionStats.avgCredibility}%</div>
                        <div className="text-xs text-gray-400 mt-1">Avg Credibility</div>
                        <div className={`text-xs mt-2 ${sessionStats.consistencyScore > 80 ? 'text-emerald-300' : sessionStats.consistencyScore > 60 ? 'text-yellow-300' : 'text-red-300'}`}>
                          {sessionStats.consistencyScore}% consistent
                        </div>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-violet-900/20 to-violet-800/20 p-4 rounded-lg border border-violet-400/30 hover:border-violet-400/50 transition-all">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-violet-300">{sessionStats.totalWords}</div>
                        <div className="text-xs text-gray-400 mt-1">Words Analyzed</div>
                        <div className="text-xs text-violet-300 mt-2">{sessionStats.avgWordsPerAnalysis} avg/analysis</div>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-amber-900/20 to-amber-800/20 p-4 rounded-lg border border-amber-400/30 hover:border-amber-400/50 transition-all">
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1">
                          <span className="text-2xl">{sessionStats.credibilityTrend.icon}</span>
                          <span className="text-xl font-bold text-amber-300">
                            {Math.abs(sessionStats.credibilityTrend.value).toFixed(0)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">Credibility Trend</div>
                        <div className={`text-xs mt-2 ${
                          sessionStats.credibilityTrend.direction === 'up' ? 'text-green-300' : 
                          sessionStats.credibilityTrend.direction === 'down' ? 'text-red-300' : 'text-yellow-300'
                        }`}>
                          {sessionStats.credibilityTrend.description}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Enhanced Credibility Chart */}
                  <div className="bg-gradient-to-br from-indigo-900/20 to-indigo-800/20 backdrop-blur-sm p-6 rounded-lg border border-indigo-400/30">
                    <div className="flex items-center justify-between mb-4">
                      <span className="font-semibold text-indigo-300 text-lg flex items-center space-x-2">
                        <span>📈</span>
                        <span>Credibility Progression</span>
                      </span>
                      <div className="text-sm text-gray-400">
                        {sessionStats.credibilityTrend.direction === 'up' && '↗️ Improving'}
                        {sessionStats.credibilityTrend.direction === 'down' && '↘️ Declining'}
                        {sessionStats.credibilityTrend.direction === 'stable' && '➡️ Stable'}
                      </div>
                    </div>
                    <div className="flex items-end space-x-2 h-24 mb-4">
                      {sessionHistory.map((item, index) => {
                        const score = item.analysis?.credibility_score || 0;
                        const height = Math.max((score / 100) * 100, 10);
                        return (
                          <div 
                            key={index} 
                            className="flex-1 relative group cursor-pointer"
                            onMouseEnter={() => setSelectedAnalysis(item)}
                            onMouseLeave={() => setSelectedAnalysis(null)}
                          >
                            <div className="bg-gray-700 rounded-t h-full relative overflow-hidden">
                              <div 
                                className={`absolute bottom-0 w-full rounded-t transition-all duration-700 ${
                                  score >= 70 ? 'bg-gradient-to-t from-green-500 to-green-400' :
                                  score >= 40 ? 'bg-gradient-to-t from-yellow-500 to-yellow-400' :
                                  'bg-gradient-to-t from-red-500 to-red-400'
                                } group-hover:shadow-lg`}
                                style={{ height: `${height}%` }}
                              ></div>
                              {selectedAnalysis === item && (
                                <div className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-black/80 text-white text-xs p-2 rounded whitespace-nowrap z-10">
                                  Analysis #{item.analysis_number}: {score}%
                                </div>
                              )}
                            </div>
                            <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-400">
                              {index + 1}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>0%</span>
                      <span>50%</span>
                      <span>100%</span>
                    </div>
                  </div>

                  {/* Risk and Emotion Analysis */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-red-900/20 to-red-800/20 backdrop-blur-sm p-6 rounded-lg border border-red-400/30">
                      <span className="font-semibold text-red-300 text-lg flex items-center space-x-2 mb-4">
                        <span>🚨</span>
                        <span>Risk Progression</span>
                      </span>
                      <div className="space-y-2">
                        {sessionStats.riskProgression.map((risk, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-xs">
                              {index + 1}
                            </div>
                            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                              risk === 'high' ? 'bg-red-500/20 text-red-300' :
                              risk === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                              risk === 'low' ? 'bg-green-500/20 text-green-300' :
                              'bg-gray-500/20 text-gray-300' // Default for 'unknown' or other values
                            }`}>
                              {(risk && risk.charAt(0).toUpperCase() + risk.slice(1)) || 'Unknown'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-pink-900/20 to-pink-800/20 backdrop-blur-sm p-6 rounded-lg border border-pink-400/30">
                      <span className="font-semibold text-pink-300 text-lg flex items-center space-x-2 mb-4">
                        <span>😊</span>
                        <span>Emotional States</span>
                      </span>
                      <div className="space-y-2">
                        {sessionStats.emotionalStates.map((emotion, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-xs">
                              {index + 1}
                            </div>
                            <div className="px-3 py-1 rounded-full text-xs font-medium bg-pink-500/20 text-pink-300 capitalize">
                              {emotion || 'neutral'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Timeline Tab */}
              {activeTab === 'timeline' && hasSessionHistory && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-6">
                    <span className="font-semibold text-white text-lg">📅 Session Timeline</span>
                    <div className="text-sm text-gray-400">
                      ({sessionHistory.length} analyses over time)
                    </div>
                  </div>
                  
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {sessionHistory.map((item, index) => (
                      <div key={index} className="relative">
                        {/* Timeline line */}
                        {index < sessionHistory.length - 1 && (
                          <div className="absolute left-6 top-12 w-0.5 h-full bg-gradient-to-b from-blue-500 to-purple-500 opacity-30"></div>
                        )}
                        
                        <div className="flex space-x-4">
                          {/* Timeline indicator */}
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold relative z-10 ${
                            item.analysis?.credibility_score >= 70 ? 'bg-gradient-to-r from-green-500 to-green-600' :
                            item.analysis?.credibility_score >= 40 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                            'bg-gradient-to-r from-red-500 to-red-600'
                          }`}>
                            {index + 1}
                          </div>
                          
                          {/* Timeline content */}
                          <div className="flex-1 bg-gradient-to-r from-slate-800/40 to-slate-700/40 backdrop-blur-sm p-4 rounded-lg border border-white/10 hover:border-white/20 transition-all">
                            <div className="flex justify-between items-start mb-3">
                              <div>
                                <span className="font-semibold text-white">Analysis #{item.analysis_number}</span>
                                <div className="text-xs text-gray-400">
                                  {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : 'Time unknown'}
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <div className={`px-2 py-1 rounded text-xs font-medium ${
                                  item.analysis?.credibility_score >= 70 ? 'bg-green-500/20 text-green-300' :
                                  item.analysis?.credibility_score >= 40 ? 'bg-yellow-500/20 text-yellow-300' :
                                  'bg-red-500/20 text-red-300'
                                }`}>
                                  {item.analysis?.credibility_score || 'N/A'}% credible
                                </div>
                                {item.analysis?.overall_risk && (
                                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                                    item.analysis.overall_risk === 'high' ? 'bg-red-500/20 text-red-300' :
                                    item.analysis.overall_risk === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                                    item.analysis.overall_risk === 'low' ? 'bg-green-500/20 text-green-300' :
                                    'bg-gray-500/20 text-gray-300' // Default for unknown
                                  }`}>
                                    {item.analysis.overall_risk.charAt(0).toUpperCase() + item.analysis.overall_risk.slice(1)} risk
                                  </div>
                                )}
                              </div>
                            </div>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              "{item.transcript?.substring(0, 120)}{item.transcript?.length > 120 ? '...' : ''}"
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Fallback for no insights */}
              {activeTab === 'insights' && !hasSessionInsights && (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">🔍</span>
                  </div>
                  <p className="text-gray-400">No AI insights available for this session yet.</p>
                  <p className="text-gray-500 text-sm mt-2">Advanced insights will be generated with more analyses.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SessionInsightsSection;
