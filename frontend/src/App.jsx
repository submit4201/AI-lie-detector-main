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
import "./enhanced-app-styles.css";

export default function App() {
  const [showSessionPanel, setShowSessionPanel] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true); // Toggle for streaming vs traditional analysis

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

  // Combine streaming and regular errors for display
  const displayError = streamingError || audioError;
  
  // Use streaming progress if available, otherwise fall back to regular progress
  const displayProgress = useStreaming ? streamingProgress : analysisProgress;
  // Effect to load session history when a session ID becomes available or changes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId);
    }
  }, [sessionId, loadSessionHistory]);
  // Effect to handle streaming analysis partial results
  useEffect(() => {
    if (partialResults && Object.keys(partialResults).length > 0) {
      // Update the analysis result with partial results as they come in
      updateAnalysisResult(partialResults);
      
      // If this looks like a complete result (has transcript and credibility_score), 
      // load session history after a delay
      if (sessionId && partialResults.transcript && partialResults.credibility_score !== undefined) {
        console.log('Streaming analysis appears complete, loading session history');
        setTimeout(() => loadSessionHistory(sessionId), 1500);
      }
    }
  }, [partialResults, updateAnalysisResult, sessionId, loadSessionHistory]);

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
    if (useStreaming && sessionId) {
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
          isStreaming={isStreaming}
          streamingProgress={streamingStep}
          partialResults={partialResults}
          lastReceivedComponent={lastReceivedComponent}
          componentsReceived={componentsReceived}
          isLoading={loading}
        />
      </div>
    </div>
  );
}
