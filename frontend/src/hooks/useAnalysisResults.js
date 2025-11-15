import { useState, useCallback } from 'react';

// Helper functions (originally in App.jsx)
export const getCredibilityColor = (level) => {
  if (level === null || level === undefined) return "text-gray-500"; // Default or loading
  if (level < 0.4) return "text-red-500"; // Scores 0-39
  if (level < 0.7) return "text-yellow-500"; // Scores 40-69
  return "text-green-500"; // Scores 70-100
};

export const getCredibilityLabel = (level) => {
  if (level === null || level === undefined) return "N/A";
  if (level < 0.4) return "High Risk / Low Credibility";    // Scores 0-39
  if (level < 0.7) return "Medium Risk / Moderate Credibility"; // Scores 40-69
  return "Low Risk / High Credibility";     // Scores 70-100
};

export const parseGeminiAnalysis = (analysisText) => {
    if (!analysisText) return { score: null, reasoning: "No analysis text provided." };

    // This function attempts to parse a score and reasoning from a combined text block.
    // Given the backend now provides structured data (credibility_score, gemini_summary),
    // this function's broad use for top-level score/reasoning is less critical.
    // It might still be useful for parsing specific string fields within gemini_summary if they contain complex text.
    // For now, its direct role in populating a top-level `parsedAnalysis` object will be removed.

    // Normalize text by removing markdown-like formatting for section headers
    const normalizedText = analysisText
        .replace(/## Credibility Score:/i, "")
        .replace(/## Reasoning:/i, "")
        .replace(/\*\*/g, ""); // Remove bold markdown

    const scoreMatch = normalizedText.match(/Credibility Score:\s*([\d.]+)/i); // Match "Credibility Score: 90"
    let score = null;
    if (scoreMatch && scoreMatch[1]) {
        score = parseFloat(scoreMatch[1]);
    } else {
        const numberMatch = normalizedText.match(/([\d.]+)/); // Match "90" or "90.0" or "90.00" or "90.000" etc.
        if (numberMatch && numberMatch[1]) {
            score = parseFloat(numberMatch[1]);
        }
    }

    // Extract reasoning (everything after score)
    let reasoning = normalizedText;
    if (scoreMatch) {
        reasoning = normalizedText.substring(scoreMatch.index + scoreMatch[0].length).trim();
    }
    if (!reasoning) {
        reasoning = "No detailed reasoning provided.";
    }

    return { score, reasoning };
};

export const formatConfidenceLevel = (level) => {
    if (!level) return "Unknown";
    return level.replace(/_/g, ' ').toUpperCase();
};

// New helper functions for enhanced data handling
export const getRiskLevelColor = (riskLevel) => {
  if (!riskLevel) return "text-gray-500";
  const level = riskLevel.toLowerCase();
  if (level === 'low') return "text-green-500";
  if (level === 'medium') return "text-yellow-500";
  if (level === 'high') return "text-red-500";
  return "text-gray-500";
};

export const formatScore = (score, decimals = 0) => {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  return `${score.toFixed(decimals)}`;
};

export const formatPercentageScore = (score, decimals = 0) => {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  return `${score.toFixed(decimals)}%`;
};

export const getScoreColor = (score, thresholds = { low: 40, medium: 70 }) => {
  if (typeof score !== 'number' || isNaN(score)) return "text-gray-500";
  if (score < thresholds.low) return "text-red-500";
  if (score < thresholds.medium) return "text-yellow-500";
  return "text-green-500";
};

export const validateAnalysisResult = (result) => {
  if (!result) return { isValid: false, errors: ['No analysis result provided'] };
  
  const errors = [];
  const warnings = [];
  
  // Check for required fields
  if (typeof result.credibility_score !== 'number') {
    warnings.push('Missing or invalid credibility score');
  }
  
  if (!result.transcript && !result.speaker_transcripts) {
    errors.push('No transcript data available');
  }
  
  if (!result.gemini_summary) {
    warnings.push('Missing Gemini summary analysis');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    hasAdvancedAnalysis: !!(result.manipulation_assessment || result.argument_analysis || result.enhanced_understanding),
    hasSessionInsights: !!result.session_insights,
    hasAudioAnalysis: !!result.audio_analysis
  };
};

export const extractKeyMetrics = (result) => {
  if (!result) return null;
  
  return {
    credibility: result.credibility_score,
    confidence: result.confidence_level,
    overallRisk: result.risk_assessment?.overall_risk,
    manipulationScore: result.manipulation_assessment?.manipulation_score,
    argumentCoherence: result.argument_analysis?.overall_argument_coherence_score,
    respectLevel: result.speaker_attitude?.respect_level_score,
    vocalConfidence: result.audio_analysis?.vocal_confidence_level,
    hasSarcasm: result.speaker_attitude?.sarcasm_detected,
    emotionCount: result.emotion_analysis?.length || 0,
    redFlagsCount: result.red_flags_per_speaker ? 
      Object.values(result.red_flags_per_speaker).flat().length : 0
  };
};

export const useAnalysisResults = () => {
  const [result, setResult] = useState(null);

  const updateAnalysisResult = useCallback((newResult) => {
    console.log('UpdateAnalysisResult called with:', newResult);
    if (newResult === null) {
      console.log('Setting result to null');
      setResult(null);
      return;
    }
    // Directly set the structured result from the backend.
    // The backend now provides credibility_score, gemini_summary, etc., as direct fields.
    // No need for a separate top-level `parsedAnalysis` field based on string parsing here.
    // Components should use result.credibility_score, result.gemini_summary.credibility, etc.
    console.log('Setting result to:', newResult);
    setResult(newResult);
  }, []);

  const exportResults = useCallback(() => {
    if (!result) {
      alert('No results to export.');
      return;
    }
    // Simple JSON export for now
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `analysis_results_${result.session_id || 'current'}.json`);
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }, [result]);

  return {
    result,
    updateAnalysisResult, // Renamed from setResult for clarity
    exportResults,
    // Exposing helpers if they are needed directly by components,
    // though often they'd be used internally or through the processed `result`
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis,
    formatConfidenceLevel,
    getRiskLevelColor,
    formatScore,
    formatPercentageScore,
    getScoreColor,
    validateAnalysisResult,
    extractKeyMetrics,
  };
};
