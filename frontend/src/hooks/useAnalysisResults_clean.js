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

    const scoreMatch = normalizedText.match(/Credibility Score:\s*([\d.]+)/i);
    let score = null;
    if (scoreMatch && scoreMatch[1]) {
        score = parseFloat(scoreMatch[1]);
    } else {
        const numberMatch = normalizedText.match(/([\d.]+)/);
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
  };
};
