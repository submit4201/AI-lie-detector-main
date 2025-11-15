import { useState, useCallback, useRef } from 'react';
import { useStreamingAnalysis } from './useStreamingAnalysis';

const API_URL = 'http://localhost:8000'; // DO NOT CHANGE THIS IF ITS NOT CONNECTING STOP THE BACKEND AND ENSURE IT ON THIS PORT

export const useAudioProcessing = (getSessionId, createNewSessionIfNeeded) => {
  const [file, setFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisProgress, setAnalysisProgress] = useState(0); // Example: 0-100
  const [useStreaming, setUseStreaming] = useState(true); // Toggle for streaming vs traditional

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Streaming analysis hook
  const {
    isStreaming: _IS_STREAMING,
    streamingProgress,
    streamingError,
    partialResults: _PARTIAL_RESULTS,
    startStreamingAnalysis,
  } = useStreamingAnalysis(getSessionId(), null);

  const validateAudioFile = (selectedFile) => {
    if (!selectedFile) return "No file selected.";
    if (!selectedFile.type.startsWith("audio/")) return "Invalid file type. Please select an audio file.";
    // Add more validation as needed (e.g., size)
    return null; // No error
  };

  const handleUpload = useCallback(async () => {
    if (!file) {
      setError("No file selected for upload.");
      return null;
    }
    setLoading(true);
    setError(null);
    setAnalysisProgress(0);

    let currentSessionId = getSessionId();
    if (!currentSessionId) {
      currentSessionId = await createNewSessionIfNeeded();
      if (!currentSessionId) {
        setError("Failed to create or retrieve session for upload.");
        setLoading(false);
        return null;
      }
    }    const formData = new FormData();
    formData.append('audio', file);
    formData.append('session_id', currentSessionId);

    try {
      // Use streaming analysis if available and enabled
      if (useStreaming && startStreamingAnalysis) {
        console.log('Starting streaming analysis...');
        
        // Monitor streaming progress
        const progressInterval = setInterval(() => {
          if (streamingProgress !== undefined) {
            setAnalysisProgress(streamingProgress);
          }
        }, 100);

        const result = await startStreamingAnalysis(file);
        clearInterval(progressInterval);
        
        if (streamingError) {
          throw new Error(streamingError);
        }
        
        setLoading(false);
        setAnalysisProgress(100);
        return result;
      } else {
        // Fallback to traditional analysis
        console.log('Using traditional analysis...');
        
        // Simulate progress for demo purposes
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          if (progress <= 100) {
            setAnalysisProgress(progress);
          }
        }, 200);

        const response = await fetch(`${API_URL}/analyze`, {
          method: 'POST',
          body: formData,
        });

        clearInterval(interval);
        setAnalysisProgress(100);

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Failed to analyze audio');
        }
        
        const analysisResult = await response.json();
        console.log('Analysis results from API:', analysisResult);
        setLoading(false);
        return analysisResult;
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || "An error occurred during analysis.");
      setLoading(false);
      setAnalysisProgress(0);
      return null;
    }
  }, [file, getSessionId, createNewSessionIfNeeded, useStreaming, startStreamingAnalysis, streamingProgress, streamingError]);

  const startRecording = useCallback(async () => {
    if (recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const recordedFile = new File([audioBlob], "recording.wav", {
            type: "audio/wav",
            lastModified: Date.now(),
        });
        setFile(recordedFile); // Set the recorded file for potential upload
        setRecording(false);
        stream.getTracks().forEach(track => track.stop()); // Stop microphone access
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      setError(null);
    } catch (err) {
      console.error("Error starting recording:", err);
      setError("Failed to start recording. Please check microphone permissions.");
      setRecording(false);
    }
  }, [recording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      // The rest is handled by onstop
    }
  }, [recording]);

  return {
    file,
    setFile,
    recording,
    loading,
    error,
    analysisProgress,
    useStreaming,
    setUseStreaming,
    validateAudioFile,
    handleUpload,
    startRecording,
    stopRecording,
  };
};
