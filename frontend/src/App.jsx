import React, { useState, useCallback, useEffect } from "react";
// Removed Button import as it's not used directly in App.jsx
// Removed duplicate React imports
import Header from "./components/App/Header";
import ControlPanel from "./components/App/ControlPanel";
import ResultsDisplay from "./components/App/ResultsDisplay";
import TestingPanel from "./components/App/TestingPanel";
import { useSessionManagement } from "./hooks/useSessionManagement";
import { useAudioProcessing } from "./hooks/useAudioProcessing";
import { useAnalysisResults } from "./hooks/useAnalysisResults";
import { useStreamingAnalysis } from "./hooks/useStreamingAnalysis";
import { useV2AnalysisSession } from './hooks/useV2AnalysisSession';
import { getV2Features } from './lib/api/features';
import "./enhanced-app-styles.css";
const API_URL = 'http://localhost:8000';

export default function App() {
  const [showSessionPanel, setShowSessionPanel] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true); // Toggle for streaming vs traditional analysis
  const [useV2, setUseV2] = useState(false);
  const [v2Available, setV2Available] = useState(null);

  const {
    sessionId,
    sessionHistory,
    createNewSession: hookCreateNewSession,
    loadSessionHistory,
    clearCurrentSession,
  } = useSessionManagement();

  const {
    file,
    setFile,
    recording,
    loading,
    error: audioError,
    setError: setAudioError,
    analysisProgress,
    validateAudioFile,
    handleUpload: hookHandleUpload,
    startRecording,
    stopRecording,
  } = useAudioProcessing(
    () => sessionId,
    hookCreateNewSession
  );
  const {
    result,
    updateAnalysisResult,
    exportResults,
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis,
    formatConfidenceLevel,
  } = useAnalysisResults();

  // Streaming analysis hook
  const {
    isStreaming,
    streamingProgress,
    streamingStep,
    streamingError,
    partialResults,
    lastReceivedComponent,
    componentsReceived,
    startStreamingAnalysis,
    resetStreamingState,
  } = useStreamingAnalysis(sessionId);

  const v2Session = useV2AnalysisSession({ sessionId });

  // Feature detection for /v2/features
  useEffect(() => {
    let mounted = true;
    const checkFeatures = async () => {
      try {
        const json = await getV2Features();
        if (!mounted) return;
        setV2Available(!!json?.streaming);
      } catch (e) {
        setV2Available(false);
      }
    };
    checkFeatures();
    return () => { mounted = false; };
  }, []);

  // Combine streaming and regular errors for display
  const displayError = streamingError || audioError;
  
  // Use streaming progress if available, otherwise fall back to regular progress
  const displayProgress = useStreaming ? streamingProgress : analysisProgress;
  const v2PartialResults = useV2 && v2Session && v2Session.state ? { transcript: v2Session.state.transcript, services: v2Session.state.services } : partialResults;
  const v2LastReceived = useV2 && v2Session && v2Session.state ? v2Session.state.lastReceived : lastReceivedComponent;
  const v2IsStreamingActive = useV2 && v2Session && v2Session.state ? v2Session.state.status === 'streaming' : isStreaming;
  // Effect to load session history when a session ID becomes available or changes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId);
    }
  }, [sessionId, loadSessionHistory]);
  // Effect to handle streaming analysis partial results
  useEffect(() => {
    const currentPartial = useV2 ? v2PartialResults : partialResults;
    if (currentPartial && Object.keys(currentPartial).length > 0) {
      updateAnalysisResult(currentPartial);
      if (sessionId && currentPartial.transcript && currentPartial.credibility_score !== undefined) {
        console.log('Streaming analysis appears complete, loading session history');
        setTimeout(() => loadSessionHistory(sessionId), 1500);
      }
    }
  }, [partialResults, v2PartialResults, useV2, updateAnalysisResult, sessionId, loadSessionHistory]);

  // Modified handleUpload to use streaming analysis when enabled
  const appHandleUpload = useCallback(async (fileToUpload) => {
    console.log('appHandleUpload called with file:', fileToUpload);
    
    // If a file is passed directly (e.g. from recording), set it in audio hook first
    if (fileToUpload) {
      const validationError = validateAudioFile(fileToUpload);
      if (validationError) {
        setAudioError(validationError);
        return;
      }
      setFile(fileToUpload);
    }    // Choose between streaming and traditional analysis
    if (useStreaming && sessionId && !useV2) {
      console.log('Using streaming analysis...');
      resetStreamingState(); // Clear previous streaming state
      const finalResult = await startStreamingAnalysis(file || fileToUpload);
      if (!finalResult) {
        console.log('Streaming analysis failed, falling back to traditional analysis');
        // Fall back to traditional analysis
        const analysisData = await hookHandleUpload();
        if (analysisData) {
          updateAnalysisResult(analysisData);
          if (sessionId) {
            // Wait a moment for backend to save session data, then load history
            setTimeout(() => loadSessionHistory(sessionId), 1000);
          }
        }      } else {
        // Streaming analysis completed successfully
        console.log('Streaming analysis completed, updating results and loading session history');
        // Wait a moment for streaming state to update, then set final results
        setTimeout(() => {
          updateAnalysisResult(finalResult);
        }, 100);
        if (sessionId) {
          // Wait a moment for backend to save session data, then load history
          setTimeout(() => loadSessionHistory(sessionId), 1000);
        }
      }
    } else if (useStreaming && sessionId && useV2) {
      // V2 stream path
      resetStreamingState();
      const finalResult = await v2Session.startStreaming(file || fileToUpload);
      if (!finalResult) {
        const analysisData = await hookHandleUpload();
        if (analysisData) {
          updateAnalysisResult(analysisData);
          if (sessionId) setTimeout(() => loadSessionHistory(sessionId), 1000);
        }
      } else {
        setTimeout(() => updateAnalysisResult(finalResult), 100);
        if (sessionId) setTimeout(() => loadSessionHistory(sessionId), 1000);
      }
    } else {
      console.log('Using traditional analysis...');
      const analysisData = await hookHandleUpload();
      if (analysisData) {
        updateAnalysisResult(analysisData);
        if (sessionId) {
          // Wait a moment for backend to save session data, then load history
          setTimeout(() => loadSessionHistory(sessionId), 1000);
        }
      }
    }
  }, [
    hookHandleUpload, 
    updateAnalysisResult, 
    loadSessionHistory, 
    sessionId, 
    setFile, 
    validateAudioFile, 
    setAudioError,
    useStreaming,
    startStreamingAnalysis,
    resetStreamingState,
    v2Session,
    useV2,
    file
  ]);

  // Wrapper for createNewSession to also clear results and errors
  const appCreateNewSession = useCallback(async () => {
    setAudioError(null);
    updateAnalysisResult(null);
    resetStreamingState(); // Clear streaming state when starting new session
    const newSessionId = await hookCreateNewSession();
    if (newSessionId) {
      // Session history will be loaded by useEffect
    } else {
      setAudioError("Failed to create a new session. Please try again.");
    }
  }, [hookCreateNewSession, updateAnalysisResult, setAudioError, resetStreamingState]);

  // Wrapper for clearCurrentSession to also clear results and errors
  const appClearCurrentSession = useCallback(async () => {
    await clearCurrentSession();
    updateAnalysisResult(null);
    setAudioError(null);
    resetStreamingState(); // Clear streaming state when clearing session
  }, [clearCurrentSession, updateAnalysisResult, setAudioError, resetStreamingState]);

  // Handler for testing panel to load sample data
  const handleLoadSampleData = useCallback((sampleResult, sampleHistory) => {
    updateAnalysisResult(sampleResult);
    // Note: We can't directly set session history from this component
    // In a real implementation, you might want to add this capability to useSessionManagement
    console.log('Loaded sample data:', sampleResult);
    console.log('Sample session history:', sampleHistory);
  }, [updateAnalysisResult]);

  return (
    <div className="app-container min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-8 fade-in">        
        {/* Testing Panel - Remove in production */}
        <TestingPanel onLoadSampleData={handleLoadSampleData} className="mb-6 section-container" />
          <ControlPanel
          file={file}
          setFile={setFile}
          loading={loading}
          recording={recording}
          error={displayError}
          setError={setAudioError}
          analysisProgress={displayProgress}
          sessionId={sessionId}
          sessionHistory={sessionHistory}
          showSessionPanel={showSessionPanel}
          setShowSessionPanel={setShowSessionPanel}
          createNewSession={appCreateNewSession}
          clearCurrentSession={appClearCurrentSession}
          handleUpload={appHandleUpload}
          startRecording={startRecording}
          stopRecording={stopRecording}
          exportResults={exportResults}
          result={result}
          validateAudioFile={validateAudioFile}
          updateAnalysisResult={updateAnalysisResult}
          useStreaming={useStreaming}
          setUseStreaming={setUseStreaming}
          useV2={useV2}
          setUseV2={setUseV2}
          v2Available={v2Available}
          isStreamingConnected={isStreaming}
          streamingProgress={streamingProgress}
        />        <ResultsDisplay
          analysisResults={result}
          parseGeminiAnalysis={parseGeminiAnalysis}
          getCredibilityColor={getCredibilityColor}
          getCredibilityLabel={getCredibilityLabel}
          formatConfidenceLevel={formatConfidenceLevel}
          sessionHistory={sessionHistory}
          sessionId={sessionId}
          isStreaming={v2IsStreamingActive}
          streamingProgress={streamingStep}
          partialResults={v2PartialResults}
          lastReceivedComponent={v2LastReceived}
          componentsReceived={componentsReceived}
          v2SessionState={v2Session.state}
          isLoading={loading}
        />
      </div>
    </div>
  );
}
