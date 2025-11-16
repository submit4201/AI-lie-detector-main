import React from 'react';
import './ResultsDisplay.css'; // Import the CSS file for styling
// Import enhanced result section components
import KeyHighlightsSection from './results/KeyHighlightsSection';
import ComprehensiveAnalysisSection from './results/ComprehensiveAnalysisSection';
import SessionInsightsSection from './results/SessionInsightsSection';
import SessionHistorySection from './results/SessionHistorySection';
import TabbedSecondarySection from './results/TabbedSecondarySection';
import DataDiagnosticPanel from './results/DataDiagnosticPanel';
import LoadingSpinner from './results/LoadingSpinner';
import ErrorDisplay from './results/ErrorDisplay';
import ErrorBoundary from './results/ErrorBoundary';
import V2ServiceGrid from '../streaming/V2ServiceGrid';
import StreamingStatusBar from '../streaming/StreamingStatusBar';
import ValidationStatus from './results/ValidationStatus';
import ManipulationPanel from './results/ManipulationPanel';
import ArgumentStructurePanel from './results/ArgumentStructurePanel';
import TranscriptPanel from '../transcript/TranscriptPanel';

// Helper component for displaying a score with a label
const ScoreDisplay = ({ label, score, unit = '%' }) => {
  let scoreText;
  if (typeof score === 'number' && !isNaN(score)) {
    if (unit === '%') {
      scoreText = `${score.toFixed(0)}${unit}`;
    } else if (unit && unit.trim() === 'WPM') {
      scoreText = `${score.toFixed(1)}${unit}`;
    } else {
      scoreText = `${score.toFixed(2)}${unit || ''}`;
    }
  } else {
    scoreText = 'N/A';
  }

  return (
    <div className="score-item">
      <span className="score-label">{label}:</span>
      <span className="score-value">{scoreText}</span>
    </div>
  );
};

// Helper component for list items
const ListItem = ({ item }) => <li className="list-item-detail">{item}</li>;

// Helper component for key-value pairs in summaries
const SummaryItem = ({ itemKey, value }) => (
  <p className="summary-item">
    <strong className="summary-item-key">{itemKey}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
  </p>
);

const MetricBadge = ({ label, value, suffix = '' }) => (
  <div className="bg-black/30 backdrop-blur-sm border border-white/10 rounded-lg p-3">
    <p className="text-xs uppercase tracking-widest text-gray-400">{label}</p>
    <p className="text-xl font-semibold text-white mt-1">
      {value !== undefined && value !== null && value !== '' ? `${value}${suffix}` : 'N/A'}
    </p>
  </div>
);

const QuantitativeMetricsPanel = ({ data, isStreaming, highlight }) => {
  if (!data) return null;
  const linguistic = data?.local?.numerical_linguistic_metrics || {};
  const interaction = data?.gemini?.interaction_metrics || {};
  const sentimentTrend = Array.isArray(interaction.sentiment_trend) ? interaction.sentiment_trend : [];

  return (
    <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${highlight ? 'just-received' : ''}`}>
      <div className="flex items-center gap-2 mb-3">
        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
        <h3 className="text-lg font-semibold text-white">Quantitative Interaction Metrics</h3>
        {isStreaming && highlight && (
          <span className="component-received-badge">• Just received</span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <MetricBadge label="Word Count" value={linguistic.word_count} />
        <MetricBadge label="Unique Words" value={linguistic.unique_word_count} />
        <MetricBadge label="Speech Rate" value={linguistic.speech_rate_wpm} suffix=" WPM" />
        <MetricBadge label="Filler Words" value={linguistic.filler_word_count} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-black/20 rounded-lg p-4 border border-white/10">
          <h4 className="text-sm uppercase tracking-wide text-cyan-300 mb-2">Interaction Sentiment</h4>
          <p className="text-white text-xl font-semibold mb-1">{interaction.overall_sentiment_label || 'Unknown'}</p>
          <p className="text-gray-300 text-sm mb-2">
            Score: {interaction.overall_sentiment_score ?? 'N/A'} • Confidence: {interaction.sentiment_confidence ?? 'N/A'}
          </p>
          {sentimentTrend.length > 0 && (
            <div className="text-gray-300 text-sm space-y-1 max-h-24 overflow-auto">
              {sentimentTrend.slice(0, 3).map((entry, index) => (
                <div key={`${entry.segment || index}-${entry.sentiment_label || entry.sentiment_score || index}`} className="flex items-center justify-between text-xs bg-black/30 rounded px-2 py-1">
                  <span>{entry.segment || `Segment ${index + 1}`}</span>
                  <span className="text-cyan-200 font-medium">
                    {entry.sentiment_label || entry.sentiment_score || 'n/a'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-black/20 rounded-lg p-4 border border-white/10">
          <h4 className="text-sm uppercase tracking-wide text-cyan-300 mb-2">Engagement Signals</h4>
          <ul className="text-gray-300 text-sm space-y-2">
            <li>Question Ratio: {interaction.question_to_statement_ratio ?? 'N/A'}</li>
            <li>Energy Score: {interaction.conversation_energy_score ?? 'N/A'}</li>
            <li>Engagement Level: {interaction.engagement_level || 'N/A'}</li>
            {Array.isArray(interaction.notable_interaction_events) && interaction.notable_interaction_events.length > 0 && (
              <li>
                Notable Events:
                <ul className="list-disc ml-5 mt-1 space-y-1">
                  {interaction.notable_interaction_events.slice(0, 3).map((event, idx) => (
                    <li key={`${event}-${idx}`} className="text-gray-400">{event}</li>
                  ))}
                </ul>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

const ResultsDisplay = ({ 
  analysisResults, 
  isLoading, 
  getCredibilityColor, 
  getCredibilityLabel, 
  sessionHistory, 
  sessionId, 
  error,
  isStreaming = false,
  streamingProgress = 'Processing...',
  partialResults = null,
  lastReceivedComponent = null,
  componentsReceived = []
  ,
  v2SessionState = null
}) => {
  console.log('=== ResultsDisplay Debug ===');
  console.log('analysisResults received:', analysisResults);
  console.log('typeof analysisResults:', typeof analysisResults);
  console.log('analysisResults === null:', analysisResults === null);
  console.log('isStreaming:', isStreaming);
  console.log('partialResults:', partialResults);
  console.log('analysisResults === undefined:', analysisResults === undefined);
  console.log('isLoading:', isLoading);
  console.log('error:', error);
  console.log('=== End Debug ===');

  const currentResults = isStreaming ? partialResults : analysisResults;
  const serviceResults = currentResults?.services || {};
  const transcriptPayload = currentResults?.transcript;
  const transcriptText = typeof transcriptPayload === 'string'
    ? transcriptPayload
    : transcriptPayload?.transcript;
  const transcriptAvailable = Boolean(transcriptText && transcriptText.trim().length > 0);
  const hasServiceResults = Object.keys(serviceResults).length > 0;
  const legacyKeysPresent = currentResults
    ? Object.keys(currentResults).some(key => !['services', 'errors', 'meta'].includes(key) && currentResults[key])
    : false;
  const hasResults = transcriptAvailable || hasServiceResults || legacyKeysPresent;
  const quantitativeMetrics = serviceResults.quantitative_metrics;

  if (error) {
    return (
      <div className="results-display-container">
        <ErrorDisplay 
          error={error}
          title="Analysis Error"
          description="There was an error processing your audio analysis."
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }
  if (isLoading) {
    return (
      <div className="results-display-container">
        <LoadingSpinner 
          size="lg" 
          message={streamingProgress || "Analyzing your audio..."}
        />
        {isStreaming && (
          <div className="mt-4 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
              <span className="text-blue-200 font-medium">Streaming Analysis Active</span>
            </div>
            {streamingProgress && (
              <p className="text-blue-300 text-sm mt-2">{streamingProgress}</p>
            )}
          </div>
        )}
      </div>
    );
  }
  // Show partial results during streaming OR when streaming is complete
  if ((isStreaming && partialResults) || (!isStreaming && analysisResults)) {
    
    if (!hasResults) {
      return (
        <div className="results-display-container">
          <div className="results-placeholder bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border border-white/20 rounded-lg p-8 text-center">
            <div className="text-6xl mb-4">🎤</div>
            <h3 className="text-2xl font-semibold text-white mb-4">Ready to Analyze</h3>
            <p className="text-gray-300 mb-6">Upload an audio file or start recording to begin your AI-powered lie detection analysis.</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-display-container">
        {/* Streaming Status Header */}
        {v2SessionState && v2SessionState.status && (
          <div className="mb-4">
            <StreamingStatusBar state={v2SessionState} onStop={() => {}} onReset={() => {}} />
          </div>
        )}
        {isStreaming && (
          <div className="mb-4 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
              <span className="text-blue-200 font-medium">
                Real-time Analysis • { (transcriptAvailable ? 1 : 0) + Object.keys(serviceResults).length } components received
              </span>
            </div>
            {streamingProgress && (
              <p className="text-blue-300 text-sm mt-2">{streamingProgress}</p>
            )}
          </div>
        )}

        {/* Completion Status Header */}
        {!isStreaming && analysisResults && (
          <div className="mb-4 bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-green-200 font-medium">Analysis Complete</span>
            </div>
          </div>
        )}
        
        <ErrorBoundary>
          <div className="results-content space-y-6">
            <V2ServiceGrid
              services={serviceResults}
              transcript={transcriptText}
              meta={currentResults?.meta}
              isStreaming={isStreaming}
              lastReceived={lastReceivedComponent}
              state={v2SessionState}
            />

            {/* Show Key Highlights as soon as any data is available */}
            {hasResults && (
              <div className="animate-fadeIn">
                <KeyHighlightsSection
                  result={currentResults}
                  services={serviceResults}
                  getCredibilityColor={getCredibilityColor}
                  getCredibilityLabel={getCredibilityLabel}
                />
              </div>
            )}

            {/* Show Individual Analysis Components as They Arrive */}
              {/* Audio Quality Analysis */}
            {currentResults.audio_quality && (
              <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${lastReceivedComponent === 'audio_quality' ? 'just-received' : ''}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  <h3 className="text-lg font-semibold text-white">Audio Quality Analysis</h3>
                  {isStreaming && lastReceivedComponent === 'audio_quality' && (
                    <span className="component-received-badge">• Just received</span>
                  )}
                </div>
                <div className="text-gray-300">
                  <p>Quality Score: <span className="text-white font-medium">{currentResults.audio_quality.overall_score || 'Processing...'}</span></p>
                  {currentResults.audio_quality.issues && (
                    <p className="text-sm mt-1">Issues detected: {currentResults.audio_quality.issues.join(', ')}</p>
                  )}
                </div>
              </div>
            )}

            {/* Transcript */}
            {transcriptAvailable && (
              <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${lastReceivedComponent === 'transcript' ? 'just-received' : ''}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <h3 className="text-lg font-semibold text-white">Transcript</h3>
                  {isStreaming && lastReceivedComponent === 'transcript' && (
                    <span className="component-received-badge">• Just received</span>
                  )}
                </div>
                <div className="text-gray-300 bg-black/20 p-3 rounded border-l-4 border-green-400">
                  <p>"{transcriptText}"</p>
                </div>
              </div>
            )}

            {quantitativeMetrics && (
              <QuantitativeMetricsPanel
                data={quantitativeMetrics}
                isStreaming={isStreaming}
                highlight={lastReceivedComponent === 'quantitative_metrics'}
              />
            )}

            {/* Manipulation / Influence Signals */}
            {(serviceResults.manipulation || currentResults.manipulation_assessment) && (
              <ManipulationPanel serviceData={serviceResults.manipulation} finalAssessment={currentResults.manipulation_assessment} />
            )}

            {/* Argument / Reasoning */}
            {(serviceResults.argument || currentResults.argument_analysis) && (
              <ArgumentStructurePanel serviceData={serviceResults.argument} finalArgument={currentResults.argument_analysis} />
            )}

            {/* Emotion Analysis */}
            {currentResults.emotion_analysis && (
              <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${lastReceivedComponent === 'emotion_analysis' ? 'just-received' : ''}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                  <h3 className="text-lg font-semibold text-white">Emotion Analysis</h3>
                  {isStreaming && lastReceivedComponent === 'emotion_analysis' && (
                    <span className="component-received-badge">• Just received</span>
                  )}
                </div>
                <div className="text-gray-300">
                  {currentResults.emotion_analysis.primary_emotion && (
                    <p>Primary Emotion: <span className="text-white font-medium">{currentResults.emotion_analysis.primary_emotion}</span></p>
                  )}
                  {currentResults.emotion_analysis.confidence && (
                    <p>Confidence: <span className="text-white font-medium">{Math.round(currentResults.emotion_analysis.confidence * 100)}%</span></p>
                  )}
                </div>
              </div>
            )}            {/* Linguistic Analysis */}
            {currentResults.linguistic_analysis && (
              <div className={`animate-slideInFromLeft bg-gray-800/50 border border-gray-600/30 rounded-lg p-4 streaming-component ${lastReceivedComponent === 'linguistic_analysis' ? 'just-received' : ''}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <h3 className="text-lg font-semibold text-white">Linguistic Analysis</h3>
                  {isStreaming && lastReceivedComponent === 'linguistic_analysis' && (
                    <span className="component-received-badge">• Just received</span>
                  )}
                </div>
                <div className="text-gray-300">
                  {currentResults.linguistic_analysis.deception_indicators && (
                    <p>Deception Score: <span className="text-white font-medium">{Math.round(currentResults.linguistic_analysis.deception_indicators * 100)}%</span></p>
                  )}
                  {currentResults.linguistic_analysis.patterns && (
                    <p className="text-sm mt-1">Patterns: {currentResults.linguistic_analysis.patterns.join(', ')}</p>
                  )}
                </div>
              </div>
            )}

            {/* Main Gemini Analysis */}
            {currentResults.gemini_analysis && (
              <div className={`animate-slideInFromLeft ${lastReceivedComponent === 'gemini_analysis' ? 'just-received' : ''}`}>
                <ComprehensiveAnalysisSection
                  analysisResults={currentResults}
                  services={serviceResults}
                />
              </div>
            )}

            {/* Secondary Analysis (if available) */}
            {currentResults.secondary_analysis && (
              <div className={`animate-slideInFromLeft ${lastReceivedComponent === 'secondary_analysis' ? 'just-received' : ''}`}>
                <TabbedSecondarySection analysisResults={currentResults} />
              </div>
            )}

            {/* Session History and Insights (only when not streaming) */}
            {!isStreaming && analysisResults && (
              <>
                <SessionHistorySection 
                  sessionHistory={sessionHistory}
                  sessionId={sessionId}
                  analysisResults={analysisResults}
                />
                <SessionInsightsSection 
                  sessionHistory={sessionHistory}
                  currentAnalysis={analysisResults}
                />
              </>
            )}
          </div>
        </ErrorBoundary>
      </div>
    );
  }
  if (!analysisResults) {
    console.log('⚠️ No analysisResults - returning placeholder');
    return (
      <div className="results-display-container">
        <div className="results-placeholder bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border border-white/20 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">🎤</div>
          <h3 className="text-2xl font-semibold text-white mb-4">Ready to Analyze</h3>
          <p className="text-gray-300 mb-6">Upload an audio file or start recording to begin your AI-powered lie detection analysis.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">📊</div>
              <div className="font-medium text-white">Credibility Scoring</div>
              <div>Advanced AI analysis of speech patterns</div>
            </div>
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium text-white">Risk Assessment</div>
              <div>Comprehensive deception indicators</div>
            </div>
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">💡</div>
              <div className="font-medium text-white">Actionable Insights</div>
              <div>Detailed recommendations and guidance</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  // Debug log the structure
  console.log('📊 Analysis results structure:', {
    transcript: !!analysisResults.transcript,
    speaker_transcripts: !!analysisResults.speaker_transcripts,
    audio_analysis: !!analysisResults.audio_analysis,
    emotion_analysis: !!analysisResults.emotion_analysis,
    credibility_score: analysisResults.credibility_score,
    confidence_level: analysisResults.confidence_level
  });

  const {
    transcript,
    session_insights,
    audio_analysis = {}
  } = analysisResults;

  console.log('Audio analysis:', audio_analysis);

  // Calculate filler word frequency for ComprehensiveAnalysisSection
  let fillerWordFrequencyText = 'N/A';
  if (analysisResults.linguistic_analysis) {
    const { linguistic_analysis } = analysisResults;
    if (typeof linguistic_analysis.filler_word_frequency === 'number' && !isNaN(linguistic_analysis.filler_word_frequency)) {
      fillerWordFrequencyText = `${linguistic_analysis.filler_word_frequency.toFixed(2)} per 100 words`;
    } else if (typeof linguistic_analysis.filler_count === 'number' && !isNaN(linguistic_analysis.filler_count) &&
               typeof linguistic_analysis.word_count === 'number' && !isNaN(linguistic_analysis.word_count) &&
               linguistic_analysis.word_count > 0) {
      const calculatedFrequency = (linguistic_analysis.filler_count / linguistic_analysis.word_count) * 100;
      fillerWordFrequencyText = `${calculatedFrequency.toFixed(2)} per 100 words`;
    }
  }  return (
    <div className="results-display-container space-y-6 fade-in">
      {/* Data Diagnostics Panel - Remove in production */}
      <ErrorBoundary fallback="Error loading diagnostics">
        <DataDiagnosticPanel 
          result={analysisResults}
          sessionHistory={sessionHistory}
          sessionId={sessionId}
        />
      </ErrorBoundary>

      {/* Key Highlights Section - Enhanced Overview */}
      <ErrorBoundary fallback="Error loading highlights">
        <KeyHighlightsSection 
          result={analysisResults}
          services={analysisResults?.services}
          getCredibilityColor={getCredibilityColor}
          getCredibilityLabel={getCredibilityLabel}
        />
      </ErrorBoundary>

      {/* Comprehensive Analysis Section - Detailed Analysis with Tabs */}
      <ErrorBoundary fallback="Error loading comprehensive analysis">
        <ComprehensiveAnalysisSection 
          result={analysisResults}
          services={analysisResults?.services}
          fillerWordFrequencyText={fillerWordFrequencyText}
        />
      </ErrorBoundary>      {/* Session Insights Section - Only show if session data is available */}
      {session_insights && (
        <ErrorBoundary fallback="Error loading session insights">
          <SessionInsightsSection 
            sessionInsights={session_insights}
            sessionHistory={sessionHistory}
          />
        </ErrorBoundary>
      )}

      {/* Secondary Features Section - Tabbed interface for Session History and Export */}
      <ErrorBoundary fallback="Error loading secondary features">
        <TabbedSecondarySection 
          result={analysisResults}
          sessionHistory={sessionHistory}
          sessionId={sessionId}
          onSelectHistoryItem={(item) => {
            console.log('Selected history item:', item);
          }}
        />
      </ErrorBoundary>

      {/* Validation Status - Show analysis completeness and any issues */}
      <ErrorBoundary fallback="Error loading validation status">
        <ValidationStatus result={analysisResults} className="mt-4" />
      </ErrorBoundary>

      {/* Legacy sections maintained for any missing data (can be removed later if all data is covered above) */}
      {/* This ensures backward compatibility while we migrate to enhanced components */}
      
      {/* Only show legacy sections if specific data is missing from enhanced components */}
      {transcript && !analysisResults.speaker_transcripts && (
        <div className="results-section section-core">
          <h3>Full Transcript</h3>
          <div className="transcript-section">
            <p>{transcript}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
